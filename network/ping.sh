#!/bin/bash
HOSTS=$1
for i in $(seq 1 $HOSTS); 
do 
    ping -c1 10.0.0.$i; 
done
