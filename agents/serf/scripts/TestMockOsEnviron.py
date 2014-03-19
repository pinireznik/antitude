#!/usr/bin/python
import MockOsEnviron
import unittest

class TestMockOsEnviron(unittest.TestCase):

	SERF_EVENT_KEY									= "SERF_EVENT"
	SERF_USER_EVENT_KEY							= "SERF_USER_EVENT"
	SERF_EVENT_VALUE_GOOD						= "user"
	SERF_EVENT_VALUE_BAD						= "XXXX"
	SERF_USER_EVENT_TEST_SET_MEMORY = "TEST_SET_MEMORY"

	def setUp(self):
		pass
	
	def testGetSERF_EVENT_VALUE_GOOD(self):
		MockDictionary = {self.SERF_EVENT_KEY: self.SERF_EVENT_VALUE_GOOD}
		self.assertEqual(self.SERF_EVENT_VALUE_GOOD, MockOsEnviron.MockOsEnviron.get(self.SERF_EVENT_KEY))
		
	def testGetSERF_EVENT_VALUE_BAD(self):
		MockDictionary = {self.SERF_EVENT_KEY: self.SERF_EVENT_VALUE_BAD}
		self.assertNotEqual(self.SERF_EVENT_VALUE_BAD, MockOsEnviron.MockOsEnviron.get(self.SERF_EVENT_KEY))

	def testGetSERF_USER_EVENT(self):
		MockDictionary = {self.SERF_USER_EVENT_KEY: self.SERF_USER_EVENT_TEST_SET_MEMORY}
		self.assertEqual(self.SERF_USER_EVENT_TEST_SET_MEMORY, MockOsEnviron.MockOsEnviron.get(self.SERF_USER_EVENT_KEY))

if __name__ == '__main__':
  unittest.main()