#!/bin/bash


### build
OPT="$*" # --no-cache
echo "OPT=$OPT"
docker build $OPT -t "orel33/minivpl-ubuntu22" . || exit 1

### push on docker.com
docker push "orel33/minivpl-ubuntu22"

### push on docker@ubx
docker tag "orel33/minivpl-ubuntu22" "registry.u-bordeaux.fr/orel33/minivpl-ubuntu22" || exit 1
docker push "registry.u-bordeaux.fr/orel33/minivpl-ubuntu22"

# EOF
