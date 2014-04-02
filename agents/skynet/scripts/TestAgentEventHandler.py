#!/usr/bin/python
from AgentEventHandler import AgentEventHandler
import unittest
import os
import logging
from testfixtures import LogCapture
import subprocess


class TestAgentEventHandler(unittest.TestCase):

    CID = "ce6437097f5683f0b9fdf01295450753ba600e33562cd4675500fdb03bfd1ff0"
    WRONG_CID = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX\
                XXX"
    PAYLOAD_WITH_TARGET = "TARGET=" + CID + " MEMORY_LEVEL=80"
    PAYLOAD_NO_TARGET = "MEMORY_LEVEL=80"
    TARGET_ARGUMENT_KEY = "TARGET"
    TARGET_ARGUMENT_PAIR = "TARGET=" + CID
    TARGET_ARGUMENT_VALUE = CID
    MEMORY_LEVEL_ARGUMENT_KEY = "MEMORY_LEVEL"
    MEMORY_LEVEL_ARGUMENT_PAIR = "MEMORY_LEVEL=80"
    MEMORY_LEVEL_ARGUMENT_VALUE = "80"

    def setUp(self):
        pass

    def testGetPayload(self):
        agentEventHandler = AgentEventHandler(
            self.PAYLOAD_WITH_TARGET)
        self.assertEqual(
            self.PAYLOAD_WITH_TARGET, agentEventHandler.getPayload())

    def testGetArgumentPairs(self):
        agentEventHandler = AgentEventHandler(
            self.PAYLOAD_WITH_TARGET)
        self.assertEqual(
            self.TARGET_ARGUMENT_PAIR,
            agentEventHandler.getArgumentPair(self.TARGET_ARGUMENT_KEY))
        self.assertEqual(
            self.MEMORY_LEVEL_ARGUMENT_PAIR,
            agentEventHandler.getArgumentPair(self.MEMORY_LEVEL_ARGUMENT_KEY))

    def testGetArgumentValues(self):
        agentEventHandler = AgentEventHandler(
            self.PAYLOAD_WITH_TARGET)
        self.assertEqual(
            self.TARGET_ARGUMENT_VALUE,
            agentEventHandler.getArgumentValue(self.TARGET_ARGUMENT_PAIR))
        self.assertEqual(
            self.MEMORY_LEVEL_ARGUMENT_VALUE,
            agentEventHandler.getArgumentValue(
                self.MEMORY_LEVEL_ARGUMENT_PAIR))

    def testGetCIDDefault(self):
        agentEventHandler = AgentEventHandler(
            self.PAYLOAD_WITH_TARGET)
        self.assertEqual("", agentEventHandler.getCID())

    def testGetCID(self):
        agentEventHandler = AgentEventHandler(
            self.PAYLOAD_WITH_TARGET, self.CID)
        self.assertEqual(self.CID, agentEventHandler.getCID())

    def testCorrectTargetWithCorrectCID(self):
        agentEventHandler = AgentEventHandler(
            self.PAYLOAD_WITH_TARGET, self.CID)
        self.assertEqual(True, agentEventHandler.correctTarget())

    def testCorrectTargetWithInCorrectCID(self):
        agentEventHandler = AgentEventHandler(
            self.PAYLOAD_WITH_TARGET, self.WRONG_CID)
        self.assertEqual(False, agentEventHandler.correctTarget())

    def testCorrectTargetWithNoTargetInPayload(self):
        agentEventHandler = AgentEventHandler(self.PAYLOAD_NO_TARGET, self.CID)
        self.assertEqual(True, agentEventHandler.correctTarget())

    def testEnvVarWithOsEnviron(self):
        agentEventHandler = AgentEventHandler(
            self.PAYLOAD_NO_TARGET, self.CID, os.environ)
        self.assertEqual(None, agentEventHandler.getEnvVar("TEST!"))

    def testEnvVarWithMockOsEnviron(self):
        agentEventHandler = AgentEventHandler(
            self.PAYLOAD_NO_TARGET,
            self.CID,
            {"SERF_EVENT": "user", "SERF_USER_EVENT": "TEST_SET_MEMORY"})
        self.assertEqual("user", agentEventHandler.getEnvVar("SERF_EVENT"))

    def testSerfEventIs(self):
        agentEventHandler = AgentEventHandler(
            self.PAYLOAD_NO_TARGET,
            self.CID,
            {"SERF_EVENT": "user", "SERF_USER_EVENT": "TEST_SET_MEMORY"})
        self.assertEqual(True, agentEventHandler.serfEventIs("user"))

    def testLogging(self):
        def testMemoryHandler(event, payload):
            logger = logging.getLogger(__name__)
            logger.info("Called memory handler")

        with LogCapture() as l:
            agentEventHandler = AgentEventHandler(
                payload=self.PAYLOAD_WITH_TARGET,
                CID=self.CID,
                envVars={"SERF_EVENT": "user",
                         "SERF_USER_EVENT": "TEST_SET_MEMORY"},
                event_handlers={"TEST_SET_MEMORY": testMemoryHandler})
            agentEventHandler.handleShit()
            self.checkLogMessages(l,
                                  "Processing user event: TEST_SET_MEMORY",
                                  "Called memory handler",
                                  "Processed")

    def checkLogMessages(self, log, *messages):
        log_str = str(log)
        ind = 0
        for m in messages:
            try:
                new_ind = log_str.index(m, ind)
                ind = new_ind + len(m)
            except ValueError:
                self.fail('Message "%s" did not appear in: \n %s'
                          % (m, log_str[ind:-1]))

    def testCommandLineCall(self):
        #Check what happens when we replicate a serf call
        subprocess.check_call(["python", "AgentEventHandler.py"],
                              env={"SERF_EVENT": "user",
                                   "SERF_USER_EVENT": "TEST_SET_MEMORY"})

        #Test with std-in
        p = subprocess.Popen(["python", "AgentEventHandler.py"],
                             stdin=subprocess.PIPE,
                             env={"SERF_EVENT": "user",
                                  "SERF_USER_EVENT": "TEST_SET_MEMORY"})
        p.communicate(input='one\ntwo\nthree\nfour\nfive\nsix\n')[0]
        self.assertEqual(p.returncode, 0)

if __name__ == '__main__':
    unittest.main()
