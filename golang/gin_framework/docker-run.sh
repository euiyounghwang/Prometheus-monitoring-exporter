#!/bin/bash

set -eu

SCRIPTDIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
echo $SCRIPTDIR


docker run --rm -it -d \
  --name go-swagger-api --publish 8080:8080 --expose 8080 \
  --network bridge \
  -v "$SCRIPTDIR:/app" \
  go-swagger-api:es


#gin_framework git:(master) ✗ ./docker-run.sh  
#0b5f8d2398a8e22d851cc8c4694a318ae1dbb6f83eee6d7a59b0c5592f05bbda

# Docker Container logs sample
# docker logs -f 0b5f8d2398a8e22d851cc8c4694a318ae1dbb6f83eee6d7a59b0c5592f05bbda
