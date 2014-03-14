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
if [ -n $FACTORY_IPADDRESS ]; then
  echo "Found: $FACTORY_IPADDRESS" >> $LOG_FILE
  JOIN_STRING="-join $FACTORY_IPADDRESS"
fi

echo serf agent $JOIN_STRING -event-handler=`pwd`/agent-event-handler.sh -role=functional_agent >> $LOG_FILE
serf agent $JOIN_STRING -event-handler=`pwd`/agent-event-handler.sh -role=functional_agent >> $LOG_FILE


