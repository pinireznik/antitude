#!/bin/bash

if [ "$1" != "serf-base" ] && [ "$1" != "skynet" ] && [ "$1" != "ui" ] && [ "$1" != "resman" ] && [ "$1" != "database" ] && [ "$1" != "webserver" ] && [ "$1" != "loadbalancer" ] && [ "$1" != "python_webapp" ]
  then
    echo "Which image do you want to build?" 
    echo "build <serf-base/skynet/ui/resman/database/webserver/loadbalancer/python_webapp>"
    exit 1;
fi
echo "Copying Dockerfile.${1} to  Dockerfile"
cp -f Dockerfile.${1} Dockerfile
# build base ubuntu with serf agent
echo "Building uglyduckling.nl/${1}"
docker build -t uglyduckling.nl/${1} .
echo "Removing temporary Dockerfile"
rm Dockerfile
