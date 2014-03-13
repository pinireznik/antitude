#!/bin/bash
./killallcontainers.sh
kill -15 `pidof serf`
./build.sh
./start-factory.sh > /dev/null 2>&1 &

