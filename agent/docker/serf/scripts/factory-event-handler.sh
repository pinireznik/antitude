#!/bin/bash 
LOG_FILE=logging/factory.log
HOST_FILE=agentstartup/factoryip

read PAYLOAD

echo "Received user event ${SERF_USER_EVENT} with payload $PAYLOAD" >> $LOG_FILE
TEST_FILE=./test/test.txt

read PAYLOAD

if [ "${SERF_USER_EVENT}" = "NEWNODE" ]; then
  HOSTNAME=`hostname`
  IP_ADDRESS=`./serf members | grep $HOSTNAME | grep -o '[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}'`
  echo $IP_ADDRESS > agentstartup/factoryip
  echo "Creating new container for $PAYLOAD" >> $LOG_FILE
  /usr/bin/docker run -d -v `pwd`/logging:/tmp/logging -v `pwd`/agentstartup:/tmp/factoryip uglyduckling.nl/serf
elif [ "${SERF_USER_EVENT}" = "FIXED" ]; then
        echo "fixed agent $PAYLOAD" >> $LOG_FILE
	# writing to the test file
	echo "$PAYLOAD ${SERF_USER_EVENT}" >> $TEST_FILE
elif [ "${SERF_USER_EVENT}" = "MEMORY" ]; then
        echo "memory use on agent $PAYLOAD" >> $LOG_FILE
fi
echo "`date '+%F %T'` ${SERF_USER_LTIME} ${SERF_EVENT} ${SERF_USER_EVENT} PAYLOAD=${PAYLOAD}" >> $LOG_FILE


