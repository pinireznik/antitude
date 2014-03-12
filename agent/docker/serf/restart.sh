#!/bin/bash

./stop.sh
./build.sh
./start.sh
sleep 2
IP_ADDRESS=`docker inspect node1 | grep IPAddress | grep -o '[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}'`
./start-local-serf.sh $IP_ADDRESS
