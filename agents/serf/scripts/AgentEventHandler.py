#!/usr/bin/python
import re
import os
import SerfCID
import logging
import socket
import sys

MEMORY_FILE = "/tmp/memory.tmp"


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
            searchObj = re.search(r"%s=[^ ]*" % argumentKey, self.payload)
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

        return self.getArgumentValue(argumentPair) == self.CID

    def serfEventIs(self, targetValue):
        return targetValue == self.getEnvVar("SERF_EVENT")

    def handleShit(self):
        # Check we have a user event intended for this container
        if self.serfEventIs("user") and self.correctTarget():
            eventName = self.getEnvVar("SERF_USER_EVENT")
            self.logger.info("Handling Event: %s" % eventName)
            if eventName in self.handlers:
                self.handlers[eventName](eventName, self.payload)


def memoryHandler(event, payload):
    logger = logging.getLogger(__name__)
    logger.info("Processing user event: %s with payload of %s" % (event, payload))
    with open(MEMORY_FILE, 'w') as f:
        for l in payload:
            f.write(l)
    logger.info("Processed user event: %s with payload of %s" % (event, payload))


if __name__ == '__main__':

    if not os.path.exists('/tmp/logging'):
        os.mkdir('/tmp/logging')

    my_ip = socket.gethostbyname(socket.gethostname())
    logging.basicConfig(filename='/tmp/logging/%s.log' % my_ip, level=logging.DEBUG)
    payload = sys.stdin.readlines()
    agentEventHandler = AgentEventHandler(payload=payload,
                                          CID=SerfCID.getCID(),
                                          envVars=os.environ,
                                          handlers={"TEST_SET_MEMORY": memoryHandler})
    logging.info("Handling Shit %s " % payload)
    agentEventHandler.handleShit()
