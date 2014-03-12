#!/usr/bin/python -u
import yaml
import socket
import time
import os
import sys
from subprocess import call
import random

FILENAME_BREAK		= "/tmp/restart/break.tmp"
FILENAME_OVERLOAD	= "/tmp/restart/load.tmp"
IP_ADDRESS		= socket.gethostbyname(socket.gethostname())
MEMORY_LIMIT		= "50"
FIXED_STRING		= "event FIXED " + IP_ADDRESS
MEMORY_FILE		= "/tmp/restart/memory.tmp"

while True:
  time.sleep(1)
  if os.path.isfile(FILENAME_BREAK):
    try:
      print "Restarting service and removing " + FILENAME_BREAK
      call(["serf", "event", "-coalesce=false", "FIXING", IP_ADDRESS])
      time.sleep(random.randint(2, 4))
      try:
          os.remove(FILENAME_BREAK)
      except:
          pass #don't care if it's already been deleted
      call(["serf", "event", "-coalesce=false", "FIXED", IP_ADDRESS])
    except Exception as e:
      call(["serf", "event", "-coalesce=false", "EXCEPTION", "%s" % e])      
      
  if os.path.isfile(FILENAME_OVERLOAD):
    print "Restarting service and removing" + FILENAME_OVERLOAD
    try:
	os.remove(FILENAME_OVERLOAD)
    except:
        pass # don't care if it's already been deleted
    call(["serf", "event", "-coalesce=false", "OVERLOADED", IP_ADDRESS])
  
  if os.path.isfile(MEMORY_FILE):
    with open(MEMORY_FILE, 'r') as f:
      memory_use = f.readline().rstrip()
      if memory_use > MEMORY_LIMIT:
        print "Memory usage: " + memory_use + " Memory Limit: " + MEMORY_LIMIT + ". Reporting."
	call(["serf", "event", "-coalesce=false", "MEMORY", IP_ADDRESS + memory_use + "limit=" + MEMORY_LIMIT])
