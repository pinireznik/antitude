#!/bin/bash -ex
# taken forn Anton Lindström
# https://github.com/antonlindstrom/docker-serf
set -e

export PATH=$PATH:/usr/local/bin
IP_ADDRESS=`hostname -i`
LOG_FILE=/tmp/logging/$IP_ADDRESS.log
LINE=`cat /proc/1/cgroup | tail -n 1`
echo ${LINE: -64} >> $LOG_FILE

if [ -z "$EVENT_HANDLER" ]; then
  echo "EVENT_HANDLER environment variable is empty. Exiting." >> $LOG_FILE
  exit 1
fi

JOIN_STRING=""

supervisord

# Check if serf-port is set and if so define the join string
if [ -n $FACTORY_IPADDRESS ]; then
  echo "Found: $FACTORY_IPADDRESS" >> $LOG_FILE
  JOIN_STRING="-join $FACTORY_IPADDRESS"
fi

serf agent $JOIN_STRING -event-handler=`pwd`/$EVENT_HANDLER -role=functional_agent >> $LOG_FILE


