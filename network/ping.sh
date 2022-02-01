#!/bin/bash
HOSTS=$1
NETWORK_ADDRESS=0
HOST_ADDRESS=1


for i in $(seq 1 $HOSTS); 
do 
    #sleep 0.0001
    ping -c1 10.0.$NETWORK_ADDRESS.$HOST_ADDRESS; 
    HOST_ADDRESS=$(($HOST_ADDRESS+1))
    if [[ $HOST_ADDRESS -gt 255 ]]
    then
        NETWORK_ADDRESS=$(($NETWORK_ADDRESS+1))
        HOST_ADDRESS=0
    fi
done
