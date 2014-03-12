#!/bin/bash

MEMORY_FILE=/tmp/memory.tmp
read AGENT_IP
if [ "${SERF_USER_EVENT}" = "TEST_SET_MEMORY" ]; then
  echo "Received TEST_SET_MEMORY event on $AGENT_IP" >> /tmp/test.txt
  PAYLOAD=""
  while read line; do
    $PAYLOAD=${line}
  done
  echo $PAYLOAD > $MEMORY_FILE
  serf event TEST_SET_EVENT_RCVD
fi
echo "${SERF_USER_EVENT}"
