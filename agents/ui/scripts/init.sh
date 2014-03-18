#!/bin/bash

#This is likely to change
/serf.sh &
cd /app
python server.py debug
