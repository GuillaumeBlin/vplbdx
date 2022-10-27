#!/bin/bash


### build
OPT="$*" # --no-cache
echo "OPT=$OPT"
docker build $OPT -t "orel33/minivpl-ubuntu20" . || exit 1

### push on docker.com
# run "docker login" before
docker push "orel33/minivpl-ubuntu20"

### push on docker@ubx
# run "docker login registry.u-bordeaux.fr"
docker tag "orel33/minivpl-ubuntu20" "registry.u-bordeaux.fr/orel33/minivpl-ubuntu20" || exit 1
docker push "registry.u-bordeaux.fr/orel33/minivpl-ubuntu20"

# EOF
