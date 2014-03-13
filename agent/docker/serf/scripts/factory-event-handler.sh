#!/bin/bash
LOG_FILE=logging/factory.log
HOST_FILE=agentstartup/factoryip

read PAYLOAD

echo "Received user event ${SERF_USER_EVENT} with payload $PAYLOAD" >> $LOG_FILE

if [ "${SERF_USER_EVENT}" = "NEWNODE" ]; then
  HOSTNAME=`hostname`
  echo $HOSTNAME >> $LOG_FILE
  IP_ADDRESS=`./serf members | grep $HOSTNAME | grep -o '[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}'`
  echo $IP_ADDRESS >> $LOG_FILE
  echo $IP_ADDRESS > agentstartup/factoryip
  echo "Creating new container for $PAYLOAD" >> $LOG_FILE
  /usr/bin/docker run -d -v `pwd`/logging:/tmp/logging -v `pwd`/agentstartup:/tmp/factoryip uglyduckling.nl/serf
  echo Exit code: $? >> $LOG_FILE
fi
