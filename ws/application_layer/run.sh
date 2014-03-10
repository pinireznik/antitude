#!/bin/bash -e

RUN_ID=$(sudo docker run -p 5000:5000 -d mrmrcoleman/ud_visualise)
echo "Container running, press any key to kill it."
read -n 1 -s
echo "Killing container $RUN_ID. This may take a few seconds."
sudo docker stop $RUN_ID
echo "Done!"
