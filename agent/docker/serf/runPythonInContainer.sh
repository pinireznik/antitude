#!/bin/bash

docker run -v `pwd`/scripts:/tmp/scripts -v `pwd`:/tmp/restart -name pythoncontainer uglyduckling.nl/serf /tmp/scripts/restart-proc.py
docker rm pythoncontainer
