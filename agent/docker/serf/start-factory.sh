#!/bin/bash

#if [ "$1" != "" ]; then
#    echo "Starting local serf agent..."
#    ./serf agent -role=container_factory -join $1 -event-handler=`pwd`/scripts/factory-event-handler.sh
#else
#    echo "$0 <IP of a serf agent>"
#fi

LOG_FILE=logging/factory.log

echo "Starting factory..." >> $LOG_FILE
./serf agent -role=container_factory -event-handler=`pwd`/scripts/factory-event-handler.sh
