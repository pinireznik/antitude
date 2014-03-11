#!/bin/bash -vxe

CONTAINER_FILE=/tmp/containerid
CONTAINER_ID=0

if [ -f "$CONTAINER_FILE" ]
then
  sudo docker stop `cat $CONTAINER_FILE`
fi

sudo docker pull mrmrcoleman/mitosis_web
RUN_ID=$(sudo docker run -p 5000:5000 -d mrmrcoleman/mitosis_web)
echo $RUN_ID > $CONTAINER_FILE


