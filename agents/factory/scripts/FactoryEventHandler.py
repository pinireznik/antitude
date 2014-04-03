#!/usr/bin/python
import re
import os
import SerfCID
import logging
import socket
import sys
import subprocess
import traceback
import json
import inspect, os


# NOTE: ugly code, a lot of try excepts. Its very difficult to debug this script without having access to stdout and stderr
# Basically piping the tracebacks through logger into the log file.

PATH = str(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))) 

class AgentEventHandler:

    def __init__(self, payload=[], CID="", envVars={}, handlers={}):
        self.payload = payload
        self.CID = CID
        self.TARGET_STRING = "TARGET"
        self.TARGET_ALL_STRING = self.TARGET_STRING + "=ALL"
        self.envVars = envVars
        self.logger = logging.getLogger(__name__)
        self.handlers = handlers

    def getPayload(self):
        return self.payload

    def dictPayload(self):
        payload_dict = {}
        for pair in str(self.payload).split(" "):
            kv = pair.split("=")
            payload_dict[kv[0]] = kv[1].strip()
        return payload_dict

    def getCID(self):
        return self.CID
  

    def getArgumentPair(self, argumentKey):
        if len(self.payload) > 0:
            searchObj = re.search(r'%s=[^ ]*' % argumentKey, str(self.payload))
            if searchObj:
                return searchObj.group()

        return None

    def getArgumentValue(self, argumentPair):
        if argumentPair:
            searchObj = re.search(r'[^=]*$', argumentPair)
            if searchObj:
                return searchObj.group()

        return None

    def getEnvVar(self, envVarName):
        return self.envVars.get(envVarName)

    def correctTarget(self):
        argumentPair = self.getArgumentPair(self.TARGET_STRING)
        if (argumentPair is None):
            #TARGET = ALL
            return True

        self.logger.info("checked target: %s" % argumentPair)
        return self.getArgumentValue(argumentPair) == self.CID

    def serfEventIs(self, targetValue):
        return targetValue == self.getEnvVar("SERF_EVENT")

    def handleShit(self):
        # Check we have a user event intended for this container
        if self.serfEventIs("user") and self.correctTarget():
            eventName = self.getEnvVar("SERF_USER_EVENT")
            if eventName in self.handlers:
                self.logger.info("Processing user event: %s with payload of %s" % (eventName, self.payload))
                try:
                   self.handlers[eventName](eventName, self.dictPayload())
                except:
                   self.logger.info(traceback.format_exc())
                

def flatten(x):
    result = []
    for el in x:
        if hasattr(el, "__iter__") and not isinstance(el, str):
            result.extend(flatten(el))
        else:
            result.append(el)
    return result

def getFactoryIP():
    for line in subprocess.check_output(['serf', 'members']).split("\n"):
        if "container_factory" in line:
            return " ".join(line.split()).split(" ")[1].split(":")[0]
    return None

def getNodeIP(cid):
    out = subprocess.check_output(['docker','inspect',cid])
    return json.loads(out)[0]['NetworkSettings']['IPAddress']
    

def createNode(env, role="serf"):
    logger = logging.getLogger(__name__)
    pwd = PATH + "/../../shared"
    image = "uglyduckling.nl/" + role
    params = flatten(['docker', 'run', '-t', '-i', env, '-d', '-v', pwd + '/logging:/tmp/logging', '-v', pwd + '/simulation:/tmp/simulation', '-v', pwd + '/configs:/tmp/configs', image])
    try:
        cid = subprocess.check_output(params).replace("\n", "")
    except:
        logger.info(traceback.format_exc())
        return (None,None)

    node_ip =getNodeIP(cid)
    return (cid, node_ip)


def newNodeHandler(event, payload):
    logger = logging.getLogger(__name__)
    env = []
    factory_ip = getFactoryIP()
    env.append('-e')
    env.append('FACTORY_IPADDRESS=%s' % factory_ip)
    env.append('-e')
    if 'role' in payload:
        env.append('AGENT_ROLE=%s' % payload['role'])
        role = payload['role']
	#This bit isn't right, but not sure how to fix in short-term
        if role == "ui":
            env.append('-p')
            env.append("5000:5000") 
        if role == "python-webapp":
            env.append('-p')
            env.append("5001:5001") 
    else:
        env.append('AGENT_ROLE=%s' % "skynet")
        role = "skynet"
    if 'parent' in payload:
        env.append('-e')
        env.append('AGENT_PARENT=%s' % payload['parent'])

    logger.info("Creating container with role %s" % role)
    (cid,node_ip) = createNode(env, role)
    logger.info("Created node with CID: %s and IP: %s" % (cid, node_ip))
    subprocess.call(["serf", "event", "NODECREATED", str(cid), node_ip]) 
    return True


def getRole(ip):
    logger = logging.getLogger(__name__)
    output = json.loads(subprocess.check_output(["serf", "members", "-format=json"]))
    for member in output['members']:
        logger.info(member)
        if ip == member['addr'].split(':')[0]:
            return member['tags']['role']
    

def memoryHandler(event, payload):
    logger = logging.getLogger(__name__)
    if int(payload['MEMORY_LEVEL']) > 75:
        env = []
        factory_ip = getFactoryIP()
        env.append('-e')
        env.append('FACTORY_IPADDRESS=%s' % factory_ip)
        env.append('-e')
        env.append('AGENT_ROLE=%s' % "resman")
        env.append('-e')
        env.append('QUERY_ROLE=%s' % getRole(payload['IP']))
        logger.info("Memory over 70%, creating resman")
        (cid,node_ip) = createNode(env, "resman")
        logger.info("Created node with CID: %s and IP: %s" % (cid, node_ip))
        subprocess.call(["serf", "event", "NODECREATED", str(cid), node_ip]) 

def removeNodeHandler(event,payload):
    logger = logging.getLogger(__name__)
    if 'cid' in payload:
        logger.info("Removing agent with cid: %s" % payload['cid'])
        subprocess.call(["docker", "kill", payload['cid']]) 
        subprocess.call(["docker", "rm", payload['cid']]) 
        subprocess.call(["serf", "force-leave", payload['cid']]) 
    else:
        logger.error("Cid not found in REMOVENODE event. Not doing anything")
    

if __name__ == '__main__':
    if not os.path.exists(PATH + '/../../logging'):
        os.mkdir(PATH + '/../../logging')

    #my_ip = socket.gethostbyname(socket.gethostname())
    logging.basicConfig(filename=PATH + '/../../logging/factory.log', level=logging.DEBUG)
    try:
      payload = sys.stdin.readlines()
      if len(payload) > 0:
          payload_data = payload[0]
      else:
          payload_data = "params=none"
      agentEventHandler = AgentEventHandler(
          payload=payload_data,
          CID=SerfCID.getCID(),
          envVars=os.environ,
          handlers={"NEWNODE": newNodeHandler,
                    "REMOVENODE": removeNodeHandler,
                    "MEMORY_LEVEL": memoryHandler})
    except:
      logging.info(traceback.format_exc())

    logging.info("Handling Shit %s " % payload)

    agentEventHandler.handleShit()

