#!/bin/bash -ex
# taken forn Anton Lindström
# https://github.com/antonlindstrom/docker-serf
set -e

export PATH=$PATH:/usr/local/bin
IP_ADDRESS=`hostname -i`
mkdir /tmp/simulation/$IP_ADDRESS -p
mkdir /tmp/logging/$IP_ADDRESS -p
rm -f /tmp/logging/$IP_ADDRESS/*
mkdir /tmp/deps
LOG_FILE=/tmp/logging/$IP_ADDRESS/startup_script.log
LINE=`cat /proc/1/cgroup | tail -n 1`
echo ${LINE: -64} >> $LOG_FILE

EVENT_HANDLER="UIEventHandler.py"

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

serf agent $JOIN_STRING -event-handler=`pwd`$EVENT_HANDLER  >> $LOG_FILE &
sleep 2 # Cant set the tags if the agent is not connected
serf tags -set role=${AGENT_ROLE}
echo DEBUG: $AGENT_PARENT >> $LOG_FILE
if [ -z $AGENT_PARENT ]; then
  echo "Parent variable not present" >> $LOG_FILE
else
  echo "Setting parent to $AGENT_PARENT" >> $LOG_FILE
  serf tags -set parent=$AGENT_PARENT
fi

if [ -e /tmp/configs/$AGENT_ROLE.cfg ]; then
  echo "Config file found for role $AGENT_ROLE" >> $LOG_FILE
  deps=$(cat /tmp/configs/$AGENT_ROLE.cfg | grep deps | cut -d "=" -f 2 | tr ";" "\n")
  for dep in $deps
  do
    echo "Requesting dependency: $dep" >> $LOG_FILE
    serf event -coalesce=false NEWNODE "role=$dep parent=$AGENT_ROLE"
  done
fi

while [ true ]; do
  sleep 1
done
