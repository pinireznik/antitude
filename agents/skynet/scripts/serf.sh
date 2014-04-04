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

echo 25 > /tmp/simulation/$IP_ADDRESS/memory.tmp
chmod o+w /tmp/simulation/$IP_ADDRESS -R
chmod o+w /tmp/logging/$IP_ADDRESS -R

EVENT_HANDLER="AgentEventHandler.py"

JOIN_STRING=""

supervisord


function need_node {

    local _outvar=`serf query -tag role=$1 NEED_NODE |  grep "Response from" | awk -F':' '{  gsub (" ", "", $2); print $2 }'`
    echo "$_outvar"

}

function create_node {

    echo "Requesting node creation: $1" >> $LOG_FILE
    serf event -coalesce=false NEWNODE "role=$1 parent=$2"


}

function using_node {

    echo "Sending USING_NODE event for $2" >> $LOG_FILE
    serf event USING_NODE "src=$1  ip=$2"

}

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
    depip=''
    depip=$(need_node $dep)
    if [ -z $depip] 
    then
      echo "No $dep available, creating one"  >> $LOG_FILE
      create_node $dep $IP_ADDRESS
      sleep 5
      depip=$(need_node $dep)
      echo "$dep available at $depip" >> $LOG_FILE
      echo $depip:6379 > /tmp/deps/$dep.cfg
    else
      echo "$dep available at $depip" >> $LOG_FILE
      using_node $IP_ADDRESS $depip
      echo $depip:6379 > /tmp/deps/$dep.cfg
    fi
    #echo "$dep available at $depip" >> $LOG_FILE
    #using_node $IP_ADDRESS $depip
    #serf event -coalesce=false NEWNODE "role=$dep parent=$IP_ADDRESS"
  done
fi

while [ true ]; do
  sleep 1
done
