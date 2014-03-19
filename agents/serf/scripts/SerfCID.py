class SerfCID:

	CGROUP_FILE		= "/proc/1/cgroup"
	CID_LENGTH		= 64
		
	@staticmethod	
	def getCID():
		try:
			with open(SerfCID.CGROUP_FILE, 'r') as f:
				first_line = f.readline()
				return first_line
		except Exception as e:
			print e
			return None