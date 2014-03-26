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

# Check if role is set and if so define the right role string
if [ -z $AGENT_ROLE ]; then
  AGENT_ROLE="functional_agent"
  echo "Assigning default role: ${AGENT_ROLE}" >> $LOG_FILE
else
  echo "Found role: $AGENT_ROLE" >> $LOG_FILE
fi


serf agent $JOIN_STRING -event-handler=`pwd`$EVENT_HANDLER -role=${AGENT_ROLE} >> $LOG_FILE &

if [ -e /tmp/configs/$AGENT_ROLE.cfg ]; then
  echo "Config file found for role $AGENT_ROLE" >> $LOG_FILE
  deps=$(cat /tmp/configs/$AGENT_ROLE.cfg | grep deps | cut -d "=" -f 2 | tr ";" "\n")
  for dep in $deps
  do
    echo "Requesting dependency: $dep" >> $LOG_FILE
    serf event -coalesce=false NEWNODE role=$dep
  done
fi

while [ true ]; do
  sleep 1
done
