#!/bin/bash

MEMORY_FILE=/tmp/memory.tmp
IP_ADDRESS=`hostname -i`
LOG_FILE=/tmp/logging/$IP_ADDRESS.log

if [ "${SERF_EVENT}" = "user" ]; then # Only process user events in here
  read PAYLOAD
  echo $IP_ADDRESS - Received user event: ${SERF_USER_EVENT} with payload of $PAYLOAD >> $LOG_FILE
  if [ "${SERF_USER_EVENT}" = "TEST_SET_MEMORY" ]; then
    echo $IP_ADDRESS - Processing user event: ${SERF_USER_EVENT} with payload of $PAYLOAD >> $LOG_FILE
    echo $PAYLOAD > $MEMORY_FILE
    echo $IP_ADDRESS - Processed user event: ${SERF_USER_EVENT} with payload of $PAYLOAD >> $LOG_FILE
  fi
fi
echo "${SERF_USER_EVENT}"
