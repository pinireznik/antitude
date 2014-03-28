#!/bin/bash
./killeverything.sh
kill -15 `pidof serf`
pushd ..
./build.sh serf
./build.sh ui
# Do not rebuild base everytime 
#./build.sh serf-base
popd
./start-factory.sh > /dev/null 2>&1 &

