#!/bin/bash

MEMORY_FILE=/tmp/memory.tmp
BREAK_FILE=/tmp/break.tmp
IP_ADDRESS=`hostname -i`
LOG_FILE=/tmp/logging/$IP_ADDRESS.log

if [ "${SERF_EVENT}" = "user" ]; then # Only process user events in here
  read PAYLOAD
  echo $IP_ADDRESS - Received user event: ${SERF_USER_EVENT} with payload of $PAYLOAD >> $LOG_FILE
  if [ "${SERF_USER_EVENT}" = "TEST_SET_MEMORY" ]; then							# TEST_SET_MEMORY
    echo $IP_ADDRESS - Processing user event: ${SERF_USER_EVENT} with payload of $PAYLOAD >> $LOG_FILE
    echo $PAYLOAD > $MEMORY_FILE
    echo $IP_ADDRESS - Processed user event: ${SERF_USER_EVENT} with payload of $PAYLOAD >> $LOG_FILE
  elif [ "${SERF_USER_EVENT}" = "TEST_BREAK_FILE" ]; then						# TEST_BREAK_FILE
    echo $IP_ADDRESS - Processing user event: ${SERF_USER_EVENT} with payload of $PAYLOAD >> $LOG_FILE
    touch $BREAK_FILE
    echo $IP_ADDRESS - Processed user event: ${SERF_USER_EVENT} with payload of $PAYLOAD >> $LOG_FILE
  elif [ "${SERF_USER_EVENT}" = "TEST_OVERLOADED" ]; then
    echo $IP_ADDRESS - Processing user event: ${SERF_USER_EVENT} with payload of $PAYLOAD >> $LOG_FILE
    ./serf event OVERLOADED $IP_ADDRESS
    echo $IP_ADDRESS - Processed user event: ${SERF_USER_EVENT} with payload of $PAYLOAD >> $LOG_FILE
  else
    echo $IP_ADDRESS - Unknown event: ${SERF_USER_EVENT} with payload of $PAYLOAD >> $LOG_FILE
  fi
fi
