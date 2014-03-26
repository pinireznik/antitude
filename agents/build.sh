#!/bin/bash

if [ "$1" != "serf-base" ] && [ "$1" != "serf" ] && [ "$1" != "ui" ]
  then
    echo "Which image do you want to build?" 
    echo "build <serf-base/serf/ui>"
    exit 1;
fi
echo "Copying Dockerfile.${1} to  Dockerfile"
cp -f Dockerfile.${1} Dockerfile
# build base ubuntu with serf agent
echo "Building uglyduckling.nl/${1}"
docker build -t uglyduckling.nl/${1} .
echo "Removing temporary Dockerfile"
rm Dockerfile
