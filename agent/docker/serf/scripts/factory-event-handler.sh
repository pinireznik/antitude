 #!/bin/bash
LOG_FILE=./mitosis.log

read PAYLOAD

if [ "${SERF_USER_EVENT}" = "OVERLOADED" ]; then
        echo "create new container for $PAYLOAD" >> $LOG_FILE
        /usr/bin/docker run -d -name node3 -link node1:serf uglyduckling.nl/serf
elif [ "${SERF_USER_EVENT}" = "FIXED" ]; then
        echo "fixed agent $PAYLOAD" >> $LOG_FILE
elif [ "${SERF_USER_EVENT}" = "MEMORY" ]; then
        echo "memory use on agent $PAYLOAD" >> $LOG_FILE
fi
echo "`date '+%F %T'` ${SERF_USER_LTIME} ${SERF_EVENT} ${SERF_USER_EVENT} PAYLOAD=${PAYLOAD}" >> $LOG_FILE

echo "${SERF_USER_EVENT}"
