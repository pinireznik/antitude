class SerfCID:

	CGROUP_FILE		= "/proc/1/cgroup"
	CID_LENGTH		= 64
		
	@staticmethod	
	def getCID():
		try:
			with open(SerfCID.CGROUP_FILE, 'r') as f:
				CID_FULL_LINE = f.readline()									# Get the full line
				CID = CID_FULL_LINE[-SerfCID.CID_LENGTH:]			# Strip off the last CID_LENGTH (Normally 64) characters and return them
				return CID
		except Exception as e:
			print e
			return None