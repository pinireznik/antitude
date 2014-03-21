#!/bin/bash

docker run -e FACTORY_IPADDRESS=10.0.2.15 -e EVENT_HANDLER=AgentEventHandler.py -d -v `pwd`/logging:/tmp/logging -p 5000:5000 uglyduckling.nl/ui
