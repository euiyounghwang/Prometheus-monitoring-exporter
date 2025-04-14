#!/bin/bash

set -eu

SCRIPTDIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
echo $SCRIPTDIR


docker run --rm -it -d \
  --name go-exporter-api --publish 2100:2112 --expose 2112 \
  --network bridge \
#   -e ES_HOST=http://host.docker.internal:9203 \
  -v "$SCRIPTDIR:/app" \
  go-search_engine-api:es

