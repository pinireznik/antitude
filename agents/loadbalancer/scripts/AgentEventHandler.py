#!/usr/bin/python
import re
import os
import SerfCID
import logging
import socket
import sys
import traceback
import json
import subprocess

BREAK_FILE = "/tmp/break.tmp"
IP_ADDRESS = socket.gethostbyname(socket.gethostname())
MEMORY_FILE = "/tmp/simulation/%s/memory.tmp" % IP_ADDRESS


class AgentEventHandler:

    def __init__(self, payload=[], CID="", envVars={}, event_handlers={}, query_handlers={}):
        self.payload = payload
        self.CID = CID
        self.TARGET_STRING = "TARGET"
        self.TARGET_ALL_STRING = self.TARGET_STRING + "=ALL"
        self.envVars = envVars
        self.logger = logging.getLogger(__name__)
        self.event_handlers = event_handlers
        self.query_handlers = query_handlers

    def getPayload(self):
        return self.payload

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

    def dictPayload(self):
        payload_dict = {}
        for pair in self.payload:
            if "=" in pair:
                kv = pair.split("=")
                payload_dict[kv[0]] = kv[1].strip()
            else:
                continue
        return payload_dict


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
            if eventName in self.event_handlers:
                self.logger.info("Processing user event: %s with payload of %s" % (eventName, self.payload))
                try:
                    self.event_handlers[eventName](eventName, self.dictPayload())
                except:
                    self.logger.info(traceback.format_exc())
                self.logger.info("Processed.")
        elif self.serfEventIs("query") and self.correctTarget():
            queryName = self.getEnvVar("SERF_QUERY_NAME")
            if queryName in self.query_handlers:
                self.logger.info("Processing query: %s with payload of %s" % (queryName, self.payload))
                try:
                    return self.query_handlers[queryName](self.payload)
                except:
                    self.logger.info(traceback.format_exc())
                self.logger.info("Processed.")

def getNodeInfo(node_ip):
    out = subprocess.check_output(['serf','members','-format', 'json'])
    json_out = json.loads(out)
    for member in json_out['members']:
        if member['addr'].split(":")[0] == node_ip:
            return member
    return None

def getNodeTags(node_ip):
    node = getNodeInfo(node_ip)
    return node['tags']


def memoryHandler(event, payload):
    with open(MEMORY_FILE, 'w') as f:
        for l in payload:
            f.write(l)

def breakHandler(event, payload):
    if not os.path.exists(BREAK_FILE):
        open(BREAK_FILE, 'w').close()

def setParent(event, payload):
    logger = logging.getLogger(__name__)
    logger.info(payload['ip'].rstrip())
    if IP_ADDRESS == payload['ip'].rstrip():
        logger.info(IP_ADDRESS)
        parents = getNodeTags(IP_ADDRESS)['parent']
        parents = parents + "," + payload['src']
        subprocess.call(['serf', 'tags', '-set', 'parent=' + parents ]) 
          

def getMemory(payload):
    logger = logging.getLogger(__name__)
    with open(MEMORY_FILE, 'r') as f:
        mem = f.read().strip()
        logger.info("QUERY: Mem level is at %s" % mem)
        return mem

def offerResource(payload):
    logger = logging.getLogger(__name__)
    return IP_ADDRESS
   

if __name__ == '__main__':
    if not os.path.exists('/tmp/logging'):
        os.mkdir('/tmp/logging')
    my_ip = socket.gethostbyname(socket.gethostname())
    if not os.path.exists('/tmp/logging/%s' % my_ip):
        os.mkdir('/tmp/logging/%s' % my_ip)

    logging.basicConfig(filename='/tmp/logging/%s/event_handler.log'
                        % my_ip, level=logging.DEBUG)
    payload = sys.stdin.read().split(" ")
    agentEventHandler = AgentEventHandler(
        payload=payload,
        CID=SerfCID.getCID(),
        envVars=os.environ,
        event_handlers={"TEST_SET_MEMORY": memoryHandler,
                        "TEST_BREAK_FILE": breakHandler,
                        "USING_NODE": setParent},
        query_handlers={"MEM_LEVEL": getMemory,
                        "NEED_NODE": offerResource})

    logging.info("Handling Shit %s " % payload)

    print agentEventHandler.handleShit()
