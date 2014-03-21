#!/bin/bash 
LOG_FILE=/tmp/logging/ui.log
read PAYLOAD
echo "`date '+%F %T'` Received user event ${SERF_USER_EVENT} with payload $PAYLOAD" >> $LOG_FILE

echo "`date '+%F %T'` ${SERF_USER_LTIME} ${SERF_EVENT} ${SERF_USER_EVENT} PAYLOAD=${PAYLOAD}" >> $LOG_FILE

if [[ -z "${PAYLOAD}" ]]; then
	curl -i -X PUT -H "Content-Type:text/plain"  http://localhost:5000/send/${SERF_USER_EVENT}
else 
	curl -i -X PUT -H "Content-Type:text/plain" -d "${PAYLOAD}" http://localhost:5000/send/${SERF_USER_EVENT}
fi
