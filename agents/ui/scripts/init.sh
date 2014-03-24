#!/bin/bash

#This is likely to change
export AGENT_ROLE="ui"
/serf.sh &
cd /app
python server.py debug
