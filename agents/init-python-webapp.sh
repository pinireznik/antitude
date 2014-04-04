#!/bin/bash

#This is likely to change
export AGENT_ROLE="python-webapp"
/serf.sh &
python run.py
