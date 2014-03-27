#!/bin/bash

LOG_FILE=../logging/factory.log

echo "Starting factory..." >> $LOG_FILE
serf agent -role=container_factory -event-handler=`pwd`/scripts/FactoryEventHandler.py
