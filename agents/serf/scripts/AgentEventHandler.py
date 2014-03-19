#!/usr/bin/python
import re
import os
import SerfCID
import logging


class AgentEventHandler:
    def __init__(self, payload="", CID="", envVars={}, handlers={}):
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
        searchObj = re.search(r"%s=[^ ]*" % argumentKey, self.payload)
        if searchObj:
            return searchObj.group()
        else:
            return None

    def getArgumentValue(self, argumentPair):
        searchObj = re.search(r'[^=]*$', argumentPair)
        if searchObj:
            return searchObj.group()
        else:
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
                self.handlers[eventName](self.payload)


def memoryHandler(payload):
    logger = logging.getLogger(__name__)
    logger.info("Called memory handler")
    print "here"


if __name__ == '__main__':

    agentEventHandler = AgentEventHandler(payload=raw_input(),
                                          CID=SerfCID.getCID(),
                                          envVars=os.environ,
                                          handlers={"TEST_SET_MEMORY": memoryHandler})
    agentEventHandler.handleShit()
