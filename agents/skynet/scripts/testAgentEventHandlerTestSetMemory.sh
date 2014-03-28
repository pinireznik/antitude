#!/bin/bash

# Set environment variables
export SERF_EVENT="user"
export SERF_USER_EVENT="TEST_SET_MEMORY"

# Call the method
echo "TARGET=ALL" | ./AgentEventHandler.py
