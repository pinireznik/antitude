#!/bin/bash -vxe

sudo docker login -u=$DOCKER_USERNAME -p=$DOCKER_PASSWORD -e=$DOCKER_EMAIL_ADDRESS
sudo docker push mrmrcoleman/ud_visualise
