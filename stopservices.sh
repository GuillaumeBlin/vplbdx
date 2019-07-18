#!/bin/bash

echo " - Removing the swarm elements"
builders=`docker node ls | grep -v "Leader" | grep -v "MANAGER STATUS" | tr -s " " | cut -f2 -d " "| tr "\n" " "`
echo "    >> Detroying swarm"
docker stack rm moodpy
sleep 3
echo "    >> Detroying swarm overlay network"
docker network rm vplpynet
sleep 3
if [ ! -z "$builders" ]; then
    for host in "$builders"
    do
	echo "    >> Asking $host to leave the swarm"
        ssh $host docker swarm leave --force
    done
fi
echo "    >> Asking manager to leave the swarm"
docker swarm leave --force
