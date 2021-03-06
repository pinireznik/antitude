#!/bin/bash

##### Globals #####

MEMORY_FILE=/tmp/memory.tmp
BREAK_FILE=/tmp/break.tmp
IP_ADDRESS=`hostname -i`
LOG_FILE=/tmp/logging/$IP_ADDRESS.log
read PAYLOAD

##### Helper functions #####

function checkTarget()
{
  TARGET_ARGUMENT=`echo $PAYLOAD | grep -o 'TARGET=[^ ]*'`                        # Extract the target argument pair from the PAYLOAD
  
  if [ "$TARGET_ARGUMENT" = "" ]; then                                            # If no target argument we default to ALL
    TARGET_ARGUMENT="TARGET=ALL"
    echo "No TARGET_ARGUMENT provided. Defaulting to ALL." >> $LOG_FILE
  fi

  TARGET=`echo $TARGET_ARGUMENT | grep -o '[^=]*$'`                               # Extract the TARGET from the target argument pair

  if [ "$TARGET" != "ALL" ]; then                                                 # If the TARGET is not ALL check it against our CID
    if [ "$TARGET" != "$CID" ]; then                                              # If TARGET does not match our CID exit
      echo "Target: $TARGET CID: $CID. No match. Ignoring." >> $LOG_FILE
      echo 0
    else
      echo "Target: $TARGET CID: $CID. Match. Processing." >> $LOG_FILE
      echo 1
    fi
  fi
}

function getCID()
{
  local LINE=`cat /proc/1/cgroup | tail -n 1`
  local CID=${LINE: -64}
  echo $CID
}

##### Main #####

if [ "$(checkTarget)" == "0" ]; then # Is this message for us?
  exit 1
fi

if [ "${SERF_USER_EVENT}" = "TEST_SET_MEMORY" ]; then                                                 # TEST_SET_MEMORY
  echo $IP_ADDRESS - Processing user event: ${SERF_USER_EVENT} with payload of $PAYLOAD >> $LOG_FILE
  echo $PAYLOAD > $MEMORY_FILE
  echo $IP_ADDRESS - Processed user event: ${SERF_USER_EVENT} with payload of $PAYLOAD >> $LOG_FILE
elif [ "${SERF_USER_EVENT}" = "TEST_BREAK_FILE" ]; then                                               # TEST_BREAK_FILE
  echo $IP_ADDRESS - Processing user event: ${SERF_USER_EVENT} with payload of $PAYLOAD >> $LOG_FILE
  touch $BREAK_FILE
  echo $IP_ADDRESS - Processed user event: ${SERF_USER_EVENT} with payload of $PAYLOAD >> $LOG_FILE
elif [ "${SERF_USER_EVENT}" = "TEST_OVERLOADED" ]; then                                               # TEST_OVERLOADED
  echo $IP_ADDRESS - Processing user event: ${SERF_USER_EVENT} with payload of $PAYLOAD >> $LOG_FILE
  ./serf event OVERLOADED $IP_ADDRESS
  echo $IP_ADDRESS - Processed user event: ${SERF_USER_EVENT} with payload of $PAYLOAD >> $LOG_FILE
else
  echo $IP_ADDRESS - Unknown event: ${SERF_USER_EVENT} with payload of $PAYLOAD >> $LOG_FILE
fi

