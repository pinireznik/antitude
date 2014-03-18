import AgentEventHandler
import MockOsEnviron
import unittest
import os

class TestAgentEventHandler(unittest.TestCase):
	
	CID													= "ce6437097f5683f0b9fdf01295450753ba600e33562cd4675500fdb03bfd1ff0"
	WRONG_CID										= "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
	PAYLOAD_WITH_TARGET					= "TARGET=" + CID + " MEMORY_LEVEL=80"
	PAYLOAD_NO_TARGET						= "MEMORY_LEVEL=80"
	TARGET_ARGUMENT_KEY					= "TARGET"
	TARGET_ARGUMENT_PAIR 				= "TARGET=" + CID
	TARGET_ARGUMENT_VALUE 			= CID
	MEMORY_LEVEL_ARGUMENT_KEY		= "MEMORY_LEVEL"
	MEMORY_LEVEL_ARGUMENT_PAIR	= "MEMORY_LEVEL=80"
	MEMORY_LEVEL_ARGUMENT_VALUE	= "80"

	def setUp(self):
		pass
	
	def testGetPayload(self):
		agentEventHandler = AgentEventHandler.AgentEventHandler(self.PAYLOAD_WITH_TARGET)
		self.assertEqual(self.PAYLOAD_WITH_TARGET, agentEventHandler.getPayload())

	def testGetArgumentPairs(self):
		agentEventHandler = AgentEventHandler.AgentEventHandler(self.PAYLOAD_WITH_TARGET)
		self.assertEqual(self.TARGET_ARGUMENT_PAIR, agentEventHandler.getArgumentPair(self.TARGET_ARGUMENT_KEY))
		self.assertEqual(self.MEMORY_LEVEL_ARGUMENT_PAIR, agentEventHandler.getArgumentPair(self.MEMORY_LEVEL_ARGUMENT_KEY))

	def testGetArgumentValues(self):
		agentEventHandler = AgentEventHandler.AgentEventHandler(self.PAYLOAD_WITH_TARGET)
		self.assertEqual(self.TARGET_ARGUMENT_VALUE, agentEventHandler.getArgumentValue(self.TARGET_ARGUMENT_PAIR))
		self.assertEqual(self.MEMORY_LEVEL_ARGUMENT_VALUE, agentEventHandler.getArgumentValue(self.MEMORY_LEVEL_ARGUMENT_PAIR))

	def testGetCIDDefault(self):
		agentEventHandler = AgentEventHandler.AgentEventHandler(self.PAYLOAD_WITH_TARGET)
		self.assertEqual("", agentEventHandler.getCID())

	def testGetCID(self):
		agentEventHandler = AgentEventHandler.AgentEventHandler(self.PAYLOAD_WITH_TARGET, self.CID)
		self.assertEqual(self.CID, agentEventHandler.getCID())

	def testCorrectTargetWithCorrectCID(self):
		agentEventHandler = AgentEventHandler.AgentEventHandler(self.PAYLOAD_WITH_TARGET, self.CID)
		self.assertEqual(True, agentEventHandler.correctTarget())

	def testCorrectTargetWithInCorrectCID(self):
		agentEventHandler = AgentEventHandler.AgentEventHandler(self.PAYLOAD_WITH_TARGET, self.WRONG_CID)
		self.assertEqual(False, agentEventHandler.correctTarget())

	def testCorrectTargetWithNoTargetInPayload(self):
		agentEventHandler = AgentEventHandler.AgentEventHandler(self.PAYLOAD_NO_TARGET, self.CID)
		self.assertEqual(True, agentEventHandler.correctTarget())
		
	def testEnvVarWithOsEnviron(self):
		agentEventHandler = AgentEventHandler.AgentEventHandler(self.PAYLOAD_NO_TARGET, self.CID, os.environ)
		self.assertEqual(None, agentEventHandler.getEnvVar("TEST!"))

	def testEnvVarWithMockOsEnviron(self):
		agentEventHandler = AgentEventHandler.AgentEventHandler(self.PAYLOAD_NO_TARGET, self.CID, MockOsEnviron.MockOsEnviron)
		self.assertEqual("user", agentEventHandler.getEnvVar("SERF_EVENT"))

if __name__ == '__main__':
  unittest.main()