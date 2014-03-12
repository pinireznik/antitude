#!/bin/bash

MEMORY_FILE=/tmp/memory.tmp
LOG_FILE=/tmp/logging/`hostname -i`.log
echo 1 >> $LOG_FILE
read PAYLOAD
echo 2 >> $LOG_FILE
if [ "${SERF_USER_EVENT}" = "TEST_SET_MEMORY" ]; then
  echo 3 >> $LOG_FILE
  serf event TEST_SET_EVENT_RCVD
  echo "Received TEST_SET_MEMORY event on $AGENT_IP with payload of $PAYLOAD" >> $LOG_FILE
  echo $PAYLOAD > $MEMORY_FILE
  serf event $PAYLOAD
fi
echo "${SERF_USER_EVENT}"
