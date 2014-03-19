class MockOsEnviron:

	SERF_EVENT_KEY									= "SERF_EVENT"
	SERF_USER_EVENT_KEY							= "SERF_USER_EVENT"
	SERF_EVENT_VALUE_GOOD						= "user"
	SERF_EVENT_VALUE_BAD						= "XXXX"
	SERF_USER_EVENT_TEST_SET_MEMORY = "TEST_SET_MEMORY"
	
	mockDictionary = {SERF_EVENT_KEY: SERF_EVENT_VALUE_GOOD, SERF_USER_EVENT_KEY: SERF_USER_EVENT_TEST_SET_MEMORY}
	
	@staticmethod	
	def get(dictionaryKey):
		return MockOsEnviron.mockDictionary.get(dictionaryKey)