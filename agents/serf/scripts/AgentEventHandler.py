#!/usr/bin/python
import re
import os
import SerfCID


class AgentEventHandler:
    def __init__(self, payload="", CID="", envVarGetter=""):
        self.payload = payload
        self.CID = CID
        self.TARGET_STRING = "TARGET"
        self.TARGET_ALL_STRING = self.TARGET_STRING + "=ALL"
        self.envVarGetter = envVarGetter

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
        return self.envVarGetter.get(envVarName)

    def correctTarget(self):
        argumentPair = self.getArgumentPair(self.TARGET_STRING)
        if (argumentPair is None):
            #TARGET = ALL
            return True

        return self.getArgumentValue(argumentPair) == self.CID

    def serfEventIs(self, targetValue):
        serfEventValue = self.getEnvVar("SERF_EVENT")
        if serfEventValue == targetValue:
            return True
        else:
            return False

if __name__ == '__main__':
    PAYLOAD = raw_input()
    CID = SerfCID.SerfCID.getCID()
    envVarGetter = os.environ

    agentEventHandler = AgentEventHandler(PAYLOAD, CID, envVarGetter)

    # Check that this is a user event and that it is intended for this container
    if agentEventHandler.serfEventIs("user") and agentEventHandler.correctTarget():
        eventName = agentEventHandler.getEnvVar("SERF_USER_EVENT")
    print eventName
