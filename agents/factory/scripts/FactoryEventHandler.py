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
    for line in subprocess.check_output(['/usr/bin/serf', 'members']).split("\n"):
        if "container_factory" in line:
            return " ".join(line.split()).split(" ")[1].split(":")[0]
    return None

def getNodeIP(cid):
    out = subprocess.check_output(['/usr/bin/docker','inspect',cid])
    return json.loads(out)[0]['NetworkSettings']['IPAddress']
    

def createNode(env, role="serf"):
    logger = logging.getLogger(__name__)
    pwd = PATH + "/../../shared"
    image = "uglyduckling.nl/" + role
    params = flatten(['/usr/bin/docker', 'run', '-t', '-i', env, '-d', '-v', pwd + '/logging:/tmp/logging', '-v', pwd + '/simulation:/tmp/simulation', '-v', pwd + '/configs:/tmp/configs', image])
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
    env.append('AGENT_ROLE=%s' % payload['role'])
    if 'parent' in payload:
        env.append('-e')
        env.append('AGENT_PARENT=%s' % payload['parent'])

    logger.info("Creating container with role %s" % payload['role'])
    (cid,node_ip) = createNode(env, payload['role'])
    logger.info("Created node with CID: %s and IP: %s" % (cid, node_ip))
    subprocess.call(["/usr/bin/serf", "event", "NODECREATED", str(cid), node_ip]) 
    return True
    

def memoryHandler(event, payload):
    logger = logging.getLogger(__name__)
    if int(payload['MEMORY_LEVEL']) > 75:
        env = []
        factory_ip = getFactoryIP()
        env.append('-e')
        env.append('FACTORY_IPADDRESS=%s' % factory_ip)
        env.append('-e')
        env.append('AGENT_ROLE=%s' % "resman")
        logger.info("Memory over 70%, creating resman")
        (cid,node_ip) = createNode(env, "resman")
        logger.info("Created node with CID: %s and IP: %s" % (cid, node_ip))
        subprocess.call(["/usr/bin/serf", "event", "NODECREATED", str(cid), node_ip]) 


if __name__ == '__main__':
    if not os.path.exists('../logging'):
        os.mkdir('../logging')

    

    #my_ip = socket.gethostbyname(socket.gethostname())
    logging.basicConfig(filename='../logging/factory.log', level=logging.DEBUG)
    payload = sys.stdin.readlines()[0]
    agentEventHandler = AgentEventHandler(
        payload=payload,
        CID=SerfCID.getCID(),
        envVars=os.environ,
        handlers={"NEWNODE": newNodeHandler,
                  "MEMORY_LEVEL": memoryHandler})

    logging.info("Handling Shit %s " % payload)

    agentEventHandler.handleShit()