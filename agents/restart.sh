#!/bin/bash
./killeverything.sh
kill -15 `pidof serf`
./build.sh skynet
./build.sh ui
./build.sh loadbalancer
./build.sh webserver
./build.sh database 
./build.sh resman
./build.sh python-webapp 
# Do not rebuild base everytime 
#./build.sh serf-base
./start-factory.sh > /dev/null 2>&1 &

