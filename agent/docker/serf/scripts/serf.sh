#!/bin/bash -ex
# taken forn Anton Lindström
# https://github.com/antonlindstrom/docker-serf
set -e

export PATH=$PATH:/usr/local/bin
IP_ADDRESS=`hostname -i`
LOG_FILE=/tmp/logging/$IP_ADDRESS.log
LINE=`cat /proc/1/cgroup | tail -n 1`
echo ${LINE: -64} >> $LOG_FILE

JOIN_STRING=""

supervisord

# Check if serf-port is set and if so define the join string
if [ -n "$SERF_PORT_7946_TCP_ADDR" ]; then
  echo "Found: $SERF_PORT_7946_TCP_ADDR" >> $LOG_FILE
  echo "Before assignment" >> $LOG_FILE
  JOIN_STRING="-join $SERF_PORT_7946_TCP_ADDR"
  echo "After assignment" >> $LOG_FILE
  echo $JOIN_STRING
fi

echo Joining $IP_ADDRESS with event handler >> $LOG_FILE
serf agent $JOIN_STRING -event-handler=`pwd`/agent-event-handler.sh -role=functional_agent


