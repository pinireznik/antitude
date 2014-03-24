#!/bin/bash
STEP_DELAY=5
OLD_BOUNDARY=0

# Delete the old memory.tmp files
echo
echo "***** Resetting the memory files *****"
echo
find simulation/ -type d -name "172*" -exec rm -fv {}/memory.tmp \;


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
./serf event NEWUINODE
sleep 3

echo 
echo "***** Adding 4 nodes *****"
echo
# Add 4 nodes
sleep 3
./serf event NEWNODE
sleep 3
./serf event NEWNODE
sleep 3
./serf event NEWNODE
sleep 3
./serf event NEWNODE
sleep 3

echo 
echo "***** Breacking all functional agents *****"
echo
./serf event TEST_BREAK_FILE
sleep 3

echo
echo "***** Increasing load *****"
echo
# Start ramping the memory up to a higher amount
for BOUNDARY in 10 30 40 50 80 100
do
  sleep $STEP_DELAY
  NEW_BOUNDARY=$BOUNDARY
    
  for agent in 172.17.0.2 172.17.0.3 172.17.0.4 172.17.0.5
  do
    mkdir -p simulation/$agent
    echo `shuf -i $OLD_BOUNDARY-$NEW_BOUNDARY -n 1` > simulation/$agent/memory.tmp
  done
  OLD_BOUNDARY=$NEW_BOUNDARY
done

echo
echo "***** Load is now high, adding another node *****"
echo
# Now that we're at high load, add another node and set it's load somewhere average
mkdir simulation/172.17.0.6
echo "50" > simulation/172.17.0.6/memory.tmp
serf event NEWNODE

echo
echo "***** Waiting for 10 seconds... *****"
echo
sleep 10

echo
echo "***** Load now reduces slightly across all nodes *****"
echo
# Now decrease the load across all nodes a little
for BOUNDARY in 95 80 70
do
  sleep $STEP_DELAY
  NEW_BOUNDARY=$BOUNDARY

  for agent in 172.17.0.2 172.17.0.3 172.17.0.4 172.17.0.5 172.17.0.6
  do
    echo `shuf -i $NEW_BOUNDARY-$OLD_BOUNDARY -n 1` > simulation/$agent/memory.tmp
  done
  OLD_BOUNDARY=$NEW_BOUNDARY
done

echo
echo "***** Waiting for 10 seconds... *****"
echo
# Then wait for 10 seconds
sleep 10

echo
echo "***** Reducing the load on all nodes *****"
echo
# Now reduce the load on all nodes
for BOUNDARY in 70 50 40 20 10 0
do
  sleep $STEP_DELAY
  NEW_BOUNDARY=$BOUNDARY

  for agent in 172.17.0.2 172.17.0.3 172.17.0.4 172.17.0.5 172.17.0.6
  do
    echo `shuf -i $NEW_BOUNDARY-$OLD_BOUNDARY -n 1` > simulation/$agent/memory.tmp
  done
  OLD_BOUNDARY=$NEW_BOUNDARY
done

# Then kill the 5th node
echo
echo "***** Removing a node *****"
echo
