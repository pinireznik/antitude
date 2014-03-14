#!/bin/bash 
LOG_FILE=logging/factory.log
read PAYLOAD
echo "`date '+%F %T'` Received user event ${SERF_USER_EVENT} with payload $PAYLOAD" >> $LOG_FILE
TEST_FILE=./test/test.txt

if [ "${SERF_USER_EVENT}" = "NEWNODE" ]; then
  HOSTNAME=`hostname`
  IP_ADDRESS=`./serf members | grep $HOSTNAME | grep -o '[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}'`
	echo "`date '+%F %T'` Creating container and attaching to factory at $IP_ADDRESS" >> $LOG_FILE
  /usr/bin/docker run -e "FACTORY_IPADDRESS=$IP_ADDRESS" -d -v `pwd`/logging:/tmp/logging uglyduckling.nl/serf
elif [ "${SERF_USER_EVENT}" = "REMOVENODE" ]; then
  echo "`date '+%F %T'` Removing container with ID = $PAYLOAD" >> $LOG_FILE
  /usr/bin/docker kill $PAYLOAD
  /usr/bin/docker rm $PAYLOAD
elif [ "${SERF_USER_EVENT}" = "FIXED" ]; then
  echo "`date '+%F %T'` fixed agent $PAYLOAD" >> $LOG_FILE
  # writing to the test file
  echo "$PAYLOAD ${SERF_USER_EVENT}" >> $TEST_FILE
elif [ "${SERF_USER_EVENT}" = "MEMORY" ]; then
  echo "`date '+%F %T'` memory use on agent $PAYLOAD" >> $LOG_FILE
fi
echo "`date '+%F %T'` ${SERF_USER_LTIME} ${SERF_EVENT} ${SERF_USER_EVENT} PAYLOAD=${PAYLOAD}" >> $LOG_FILE


