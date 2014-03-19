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

if __name__ == '__main__':
    PAYLOAD = raw_input()
    CID = SerfCID.SerfCID.getCID()
    envVarGetter = os.environ

    print PAYLOAD
    print CID
    agentEventHandler = AgentEventHandler(PAYLOAD, CID, envVarGetter)
    if not agentEventHandler.correctTarget():
        print "It's not for me!"
    else:
        print "It's for me!"
