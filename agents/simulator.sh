#!/bin/bash
STEP_DELAY=5
OLD_BOUNDARY=0

## Delete the old memory.tmp files
#echo
#echo "***** Resetting the memory files *****"
#echo
#find simulation/ -type d -name "172*" -exec rm -fv {}/memory.tmp \;


echo
echo "***** Cleanning up *****"
echo
./killeverything.sh
./deletelogs.sh


# Start up the system
echo
echo "***** Starting up Skynet *****"
echo
./restart.sh

echo 
echo "***** Adding UI node *****"
echo
sleep 2
serf event NEWNODE role=ui
sleep 3

echo 
echo "***** Adding 4 nodes *****"
echo
# Add 4 nodes
sleep 5
serf event NEWNODE role=loadbalancer 
echo Waiting for database
sleep 20
echo Creating webserver which will reuse existing database
serf event NEWNODE role=webserver
sleep 25

echo Creating three new agents of for the same role
serf event NEWNODE role=skynet
sleep 3
serf event NEWNODE role=skynet
sleep 3
serf event NEWNODE role=skynet
sleep 5

echo 
echo "***** Breacking all functional agents *****"
echo
serf event TEST_BREAK_FILE
sleep 25


echo
echo Starting to increase memory for skynet agents
echo
for node in `serf members | grep skynet | awk '{print $2}' | awk -F ':' '{print $1}'`
do
  echo Increasing memory for $node
  echo 90 > shared/simulation/$node/memory.tmp
  sleep 20
done
serf event NEWNODE role=skynet
sleep 20
echo
echo Reducing  memory for skynet agents after automatic creation of a new one
echo
for node in `serf members | grep skynet | awk '{print $2}' | awk -F ':' '{print $1}'`
do
  echo Decreasing memory for $node
  echo 60 > shared/simulation/$node/memory.tmp
  sleep 5
done

#echo
#echo "***** Increasing load *****"
#echo
## Start ramping the memory up to a higher amount
#for BOUNDARY in 10 30 40 50 80 100
#do
#  sleep $STEP_DELAY
#  NEW_BOUNDARY=$BOUNDARY
#    
#  for agent in 172.17.0.2 172.17.0.3 172.17.0.4 172.17.0.5
#  do
#    echo Increasing load for $agent
#    mkdir -p simulation/$agent
#    echo `shuf -i $OLD_BOUNDARY-$NEW_BOUNDARY -n 1` > simulation/$agent/memory.tmp
#  done
#  OLD_BOUNDARY=$NEW_BOUNDARY
#done
#
#echo
#echo "***** Load is now high, adding another node *****"
#echo
## Now that we're at high load, add another node and set it's load somewhere average
#mkdir simulation/172.17.0.6
#echo "50" > simulation/172.17.0.6/memory.tmp
#serf event NEWNODE
#
#echo
#echo "***** Waiting for 10 seconds... *****"
#echo
#sleep 10
#
#echo
#echo "***** Load now reduces slightly across all nodes *****"
#echo
## Now decrease the load across all nodes a little
#for BOUNDARY in 95 80 70
#do
#  sleep $STEP_DELAY
#  NEW_BOUNDARY=$BOUNDARY
#
#  for agent in 172.17.0.2 172.17.0.3 172.17.0.4 172.17.0.5 172.17.0.6
#  do
#    echo `shuf -i $NEW_BOUNDARY-$OLD_BOUNDARY -n 1` > simulation/$agent/memory.tmp
#  done
#  OLD_BOUNDARY=$NEW_BOUNDARY
#done
#
#echo
#echo "***** Waiting for 10 seconds... *****"
#echo
## Then wait for 10 seconds
#sleep 10
#
#echo
#echo "***** Reducing the load on all nodes *****"
#echo
## Now reduce the load on all nodes
#for BOUNDARY in 70 40 20
#do
#  sleep $STEP_DELAY
#  NEW_BOUNDARY=$BOUNDARY
#
#  for agent in 172.17.0.2 172.17.0.3 172.17.0.4 172.17.0.5 172.17.0.6
#  do
#    echo `shuf -i $NEW_BOUNDARY-$OLD_BOUNDARY -n 1` > simulation/$agent/memory.tmp
#  done
#  OLD_BOUNDARY=$NEW_BOUNDARY
#done
#
## Then kill the 5th node
#echo
#echo "***** Removing a node *****"
#echo
#serf event REMOVENODE cid=`serf members -status=alive -role=functional_agent | head -1 | cut -c1-12`
