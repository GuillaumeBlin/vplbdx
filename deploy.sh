#!/bin/bash

echo " - Checking local certificates"
mkdir /vplbdx/registry
mkdir /vplbdx/mongo_data
mkdir /vplbdx/tmper_data
mkdir /vplbdx/redis_data
mkdir /dev/kvm
if [ ! -f /vplbdx/ssl/secure.crt -o ! -f /vplbdx/ssl/secure.key ]; then
    echo "    >> You need to store your cert/key files in vplbdx/ssl as /vplbdx/ssl/secure.crt and /vplbdx/ssl/secure.key files"
    exit 1
fi

if [ ! -z "$*" ]; then
    for host in "$*"
    do
	ssh $host mkdir /vplbdx/registry
    	echo " - Checking distant certificates on $host"
        ssh $host stat /vplbdx/ssl/secure.crt \> /dev/null 2\>\&1
        if [ $? -gt 0 ]; then
            echo "    >> /vplbdx/ssl/secure.crt missing on $host"
            exit 1
        fi
        ssh $host stat /vplbdx/ssl/secure.key \> /dev/null 2\>\&1
        if [ $? -gt 0 ]; then
            echo "    >> /vplbdx/ssl/secure.key missing on $host"
            exit 1
        fi
    done
fi

# Hard cleaning of the system (if needed)
docker system prune -a -f
service docker restart
if [ ! -z "$*" ]; then
    for host in "$*"
    do
	ssh $host docker system prune -a -f
	ssh $host service docker restart
    done
fi

chmod a+rw /var/run/docker.sock
chmod o+rwx /dev/kvm
echo " - Initializing swarm"
docker swarm init --advertise-addr `hostname -i | cut -f2 -d " "` --task-history-limit 0
sleep 3
if [ ! -z "$*" ]; then
    for host in "$*"
    do
        echo "   >> $host joining the swarm"
	ssh $host `docker swarm join-token worker | grep join`
    done
fi

echo " - Creating overlay network"

docker network create --driver=overlay --subnet=192.169.18.0/24 --attachable vplpynet
sleep 3
export `cat .env` #The .env file feature only works when you use the docker-compose up command and does not work with docker stack deploy.
echo " - Deploying the swarm using .env file configuration"
docker stack deploy --compose-file docker-compose.yml moodpy
sleep 3
docker run -d -p $REGISTRY_PORT:5000 registry
if [ ! -z "$*" ]; then
  for host in "$*"
    do
      ssh $host docker run -d -p $REGISTRY_PORT:5000 registry
    done
fi
