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
            payload_dict[kv[0]] = kv[1]
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
                   self.handlers[eventName](eventName, self.dictPayload(), self.logger)
                except:
                   self.logger.info(traceback.format_exc())
                

'''
  HOSTNAME=`hostname`
  for params in `echo $PAYLOAD | tr " " "\n"`
  do
    printf -v `echo $params | cut -d "=" -f 1` `echo $params | cut -d "=" -f 2`
    echo DEBUG: $parent >> $LOG_FILE
  done
  IP_ADDRESS=`./serf members | grep $HOSTNAME | grep -o '[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}'`
  echo "`date '+%F %T'` Creating node with role $ROLE and attaching to factory at $IP_ADDRESS" >> $LOG_FILE
  CID=$(/usr/bin/docker run -e "AGENT_PARENT=$parent" -e "AGENT_ROLE=$role" -e "FACTORY_IPADDRESS=$IP_ADDRESS" -e "EVENT_HANDLER=${EVENT_HANDLER}" -d -v `pwd`/logging:/tmp/logging -v `pwd`/simulation:/tmp/simulation -v `pwd`/configs:/tmp/configs ${DOCKER_PORT_EXPOSE} ${DOCKER_IMAGE})
  NEWNODE_IP=`/usr/bin/docker inspect $CID | grep IPAddress | grep -o '[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}'`
  echo "`date '+%F %T'` Created new node with CID: $CID and public IP: $NEWNODE_IP" >> $LOG_FILE
  ./serf event NODECREATED $CID $NEWNODE_IP
'''
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
    


def newNodeHandler(event, payload, logger):
    env = []
    factory_ip = getFactoryIP()
    env.append('-e')
    env.append('FACTORY_IPADDRESS=%s' % factory_ip)
    if 'role' in payload:
        image = "uglyduckling.nl/" + payload['role']
    else:
        image = "uglyduckling.nl/serf"
    if 'parent' in payload:
        env.append('-e')
        env.append('AGENT_PARENT=%s' % payload['parent'])
    pwd = "../shared"
    logger.info("Creating container with role %s" % payload['role'])
    params = flatten(['/usr/bin/docker', 'run', env, '-d', '-v', pwd + '/logging:/tmp/logging', '-v', pwd + '/simulation:/tmp/simulation', '-v', pwd + '/configs:/tmp/configs', image])
    try:
        cid = subprocess.check_output(params).replace("\n", "")
    except:
        logger.error(traceback.format_exc())
        return False

    node_ip =getNodeIP(cid)
    logger.info("Created node with CID: %s and IP: %s" % (cid, node_ip))
    subprocess.call(["/usr/bin/serf", "event", "NODECREATED", str(cid), node_ip]) 
    return True
    

def memoryHandler(event, payload):
    return "DEBUG memory handler: " + str(payload)

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
