#!/bin/sh

FILENAME_BREAK=/tmp/restart/break.tmp
FILENAME_OVERLOAD=/tmp/restart/load.tmp
IP_ADDRESS=`hostname -i`
while [ true ]
do
   sleep 1
   if [ -f $FILENAME_BREAK ]; then
      echo "Restartingi service and removing $FILENAME_BREAK"
      serf event FIXING $IP_ADDRESS
      sleep 2
      rm $FILENAME_BREAK
      serf event FIXED $IP_ADDRESS
   elif [ -f $FILENAME_OVERLOAD ]; then
      echo "Restarting service and removing $FILENAME_OVERLOAD"
      rm $FILENAME_OVERLOAD
      serf event OVERLOADED
   fi
done
