#!/bin/bash
./killeverything.sh
kill -15 `pidof serf`
./build.sh
pushd ../ui
#./build.sh
popd
./start-factory.sh > /dev/null 2>&1 &

