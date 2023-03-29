#!/bin/bash
numproc=$1; if [ -z $numproc ]; then numproc=4; fi # Number of processes to use

echo $numproc

for (( i=1; i<=$numproc; i++ ))
    do
        echo "Running batch process $i ..."
        screen -Ldm python3 src/batch.py @# Run the models
        sleep 1
    done
