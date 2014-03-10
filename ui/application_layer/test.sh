#!/bin/bash -vxe

RUN_ID=$(sudo docker run -p 5000:5000 -d mrmrcoleman/ud_visualise)
sleep 5
cd visualise
python test.py
sudo docker stop $RUN_ID
