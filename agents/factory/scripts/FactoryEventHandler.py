#!/usr/bin/python
import re
import os
import SerfCID
import logging
import socket
import sys

MEMORY_FILE = "/tmp/memory.tmp"
BREAK_FILE = "/tmp/break.tmp"


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
                self.logger.info(str(self.handlers))
                self.logger.info(self.handlers[eventName](eventName, self.payload))
                


def newNodeHandler(event, payload):
    return "DEBUG Node handler: " + str(payload)

def memoryHandler(event, payload):
    return "DEBUG memory handler: " + payload

if __name__ == '__main__':
    if not os.path.exists('../logging'):
        os.mkdir('../logging')

    #my_ip = socket.gethostbyname(socket.gethostname())
    logging.basicConfig(filename='../logging/factory.log', level=logging.DEBUG)
    payload = sys.stdin.readlines()
    agentEventHandler = AgentEventHandler(
        payload=payload,
        CID=SerfCID.getCID(),
        envVars=os.environ,
        handlers={"NEWNODE": newNodeHandler,
                  "MEMORY_LEVEL": memoryHandler})

    logging.info("Handling Shit %s " % payload)

    agentEventHandler.handleShit()
