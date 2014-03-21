#!/bin/bash 
LOG_FILE=logging/factory.log
read PAYLOAD
echo "`date '+%F %T'` Received user event ${SERF_USER_EVENT} with payload $PAYLOAD" >> $LOG_FILE
TEST_FILE=./test/test.txt

if [ "${SERF_USER_EVENT}" = "NEWNODE" ]; then
  HOSTNAME=`hostname`
  IP_ADDRESS=`./serf members | grep $HOSTNAME | grep -o '[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}'`
  echo "`date '+%F %T'` Creating node and attaching to factory at $IP_ADDRESS" >> $LOG_FILE
  CID=$(/usr/bin/docker run -e "FACTORY_IPADDRESS=$IP_ADDRESS" -e "EVENT_HANDLER=AgentEventHandler.py" -d -v `pwd`/logging:/tmp/logging -v `pwd`/simulation:/tmp/simulation uglyduckling.nl/serf)
  NEWNODE_IP=`/usr/bin/docker inspect $CID | grep IPAddress | grep -o '[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}'`
  echo "`date '+%F %T'` Created new node with CID: $CID and public IP: $NEWNODE_IP" >> $LOG_FILE
  ./serf event NODECREATED $CID $NEWNODE_IP
elif [ "${SERF_USER_EVENT}" = "REMOVENODE" ]; then
  echo "`date '+%F %T'` Removing container with ID = $PAYLOAD" >> $LOG_FILE
  /usr/bin/docker kill $PAYLOAD
  /usr/bin/docker rm $PAYLOAD
  ./serf force-leave $PAYLOAD
fi
echo "`date '+%F %T'` ${SERF_USER_LTIME} ${SERF_EVENT} ${SERF_USER_EVENT} PAYLOAD=${PAYLOAD}" >> $LOG_FILE

if [[ -z "${PAYLOAD}" ]]; then
	curl -i -X PUT -H "Content-Type:text/plain"  http://localhost:5000/send/${SERF_USER_EVENT}
else 
	curl -i -X PUT -H "Content-Type:text/plain" -d "${PAYLOAD}" http://localhost:5000/send/${SERF_USER_EVENT}
fi
