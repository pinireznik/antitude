#!/bin/bash

MEMORY_FILE=/tmp/memory.tmp
read PAYLOAD
if [ "${SERF_USER_EVENT}" = "TEST_SET_MEMORY" ]; then
  serf event TEST_SET_EVENT_RCVD
  echo "Received TEST_SET_MEMORY event on $AGENT_IP with payload of $PAYLOAD" >> /tmp/test.txt
  echo $PAYLOAD > $MEMORY_FILE
  serf event $PAYLOAD
fi
echo "${SERF_USER_EVENT}"
