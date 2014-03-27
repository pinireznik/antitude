import logging

CGROUP_FILE = "/proc/1/cgroup"
CID_LENGTH = 64

def getCID():
    try:
        with open(CGROUP_FILE, 'r') as f:
            CID_FULL_LINE = f.readline()  # Get the full line
            CID = CID_FULL_LINE[-CID_LENGTH:]  # Strip off the last CID_LENGTH (Normally 64) characters and return them
            return CID
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error("Failed to retrieve CID: %s" % e)
        return None
