#!/bin/bash

echo " - Checking local certificates"
mkdir -p /vplbdx/certbot/conf
mkdir -p /vplbdx/certbot/www
mkdir -p /vplbdx/nginx
mkdir -p /vplbdx/registry
mkdir -p /vplbdx/mongo_data
mkdir -p /vplbdx/tmper_data
mkdir -p /vplbdx/redis_data
mkdir -p /dev/kvm
export `cat .env` #The .env file feature only works when you use the docker-compose up command and does not work with docker stack deploy.
rm -rf /vplbdx/ssl/*
cp nginx.conf /vplbdx/ssl/nginx.conf
#cd /usr/local/openresty/nginx/conf/ && ln -s /vplbdx/certbot/conf/live/${SERVER_NAME}/fullchain.pem && ln -s /vplbdx/certbot/conf/live/${SERVER_NAME}/privkey.pem
cp /vplbdx/certbot/conf/live/${SERVER_NAME}/fullchain.pem /vplbdx/ssl/.
cp /vplbdx/certbot/conf/live/${SERVER_NAME}/fullchain.pem /vplbdx/ssl/secure.crt
cp /vplbdx/certbot/conf/live/${SERVER_NAME}/privkey.pem /vplbdx/ssl/.
cp /vplbdx/certbot/conf/live/${SERVER_NAME}/privkey.pem /vplbdx/ssl/secure.key
pwd
#if [ ! -f /vplbdx/ssl/secure.crt -o ! -f /vplbdx/ssl/secure.key ]; then
#    echo "    >> You need to store your cert/key files in vplbdx/ssl as /vplbdx/ssl/secure.crt and /vplbdx/ssl/secure.key files"
#    echo "    >> openssl genrsa 2048 > /vplbdx/ssl/secure.key"
#    echo "    >> chmod 400 /vplbdx/ssl/secure.key"
#    echo "    >> openssl req -new -x509 -nodes -sha256 -days 365 -key /vplbdx/ssl/secure.key -out /vplbdx/ssl/secure.crt"
#    exit 1
#fi

#if [ ! -z "$*" ]; then
#    for host in "$*"
#    do
#	ssh $host mkdir /vplbdx/registry
#    	echo " - Checking distant certificates on $host"
#        ssh $host stat /vplbdx/ssl/secure.crt \> /dev/null 2\>\&1
#        if [ $? -gt 0 ]; then
#            echo "    >> /vplbdx/ssl/secure.crt missing on $host"
#            exit 1
#        fi
#        ssh $host stat /vplbdx/ssl/secure.key \> /dev/null 2\>\&1
#        if [ $? -gt 0 ]; then
#            echo "    >> /vplbdx/ssl/secure.key missing on $host"
#            exit 1
#        fi
#    done
#fi

# Hard cleaning of the system (if needed)
docker system prune -a -f
service docker restart
#if [ ! -z "$*" ]; then
#    for host in "$*"
#    do
#	ssh $host docker system prune -a -f
#	ssh $host service docker restart
#    done
#fi

chmod a+rw /var/run/docker.sock
chmod o+rwx /dev/kvm
echo " - Initializing swarm"
docker swarm init --advertise-addr `hostname -i | cut -f2 -d " "` --task-history-limit 0
sleep 3
#if [ ! -z "$*" ]; then
#    for host in "$*"
#    do
#        echo "   >> $host joining the swarm"
#	ssh $host `docker swarm join-token worker | grep join`
#    done
#fi

echo " - Creating overlay network"

docker network create --driver=overlay --subnet=192.169.18.0/24 --attachable vplpynet
sleep 3
echo " - Deploying the swarm using .env file configuration"
docker stack deploy --compose-file docker-compose.yml moodpy
sleep 3
docker run -d -p $REGISTRY_PORT:5000 registry
#if [ ! -z "$*" ]; then
#  for host in "$*"
#    do
#      ssh $host docker run -d -p $REGISTRY_PORT:5000 registry
#    done
#fi
