#!/usr/bin/python -u
import socket
import time
import os
import sys
from subprocess import call
import random

FILENAME_BREAK		    = "/tmp/break.tmp"
FILENAME_OVERLOAD	    = "/tmp/load.tmp"
IP_ADDRESS		        = socket.gethostbyname(socket.gethostname())
MEMORY_LIMIT		      = "50"
FIXED_STRING		      = "event FIXED " + IP_ADDRESS
LOG_FILE		          = "/tmp/logging/" + IP_ADDRESS + ".log"
SIMULATION_DIRECTORY  = "/tmp/simulation/" + IP_ADDRESS
MEMORY_FILE		        = SIMULATION_DIRECTORY + "/memory.tmp"
LAST_MEM = None

while True:
    time.sleep(1)
    memory_use = None
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
        print "Found memory file"
        with open(MEMORY_FILE, 'r') as f:
            memory_use = f.readline().rstrip()
            print "Memory use: " + memory_use
        if LAST_MEM != memory_use:
            print "Memory use changed, sending event"
            call(["serf", "event", "-coalesce=false", "MEMORY_LEVEL", "MEMORY_LEVEL=%s IP=%s" % (memory_use, IP_ADDRESS)])
    global LAST_MEM
    LAST_MEM = memory_use 
