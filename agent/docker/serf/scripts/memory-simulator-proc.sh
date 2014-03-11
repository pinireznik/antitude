#!/bin/bash

FILENAME_MEMORY=/tmp/memory.tmp
RANGE=100

while [ true ]
do
   memory_use=$RANDOM
   let "memory_use %= $RANGE"
   sleep 3
   echo $memory_use > $FILENAME_MEMORY
done
