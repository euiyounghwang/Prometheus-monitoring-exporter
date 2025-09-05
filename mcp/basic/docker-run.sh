#!/bin/bash

set -eu

SCRIPTDIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

# ~ V.7
# docker run --rm -it -d --publish 9292:9201 --expose 9201 \
#   -e node.name=fn-platform-omni-data-01 \
#   -e discovery.type=single-node \
#   -e http.port=9201 \
#   -e http.cors.enabled=true \
#   -e http.cors.allow-origin=* \
#   -e http.cors.allow-headers=X-Requested-With,X-Auth-Token,Content-Type,Content-Length,Authorization \
#   -e http.cors.allow-credentials=true \
#   -e xpack.security.enabled=false \
#   -e bootstrap.system_call_filter=false \
#   -e ES_JAVA_OPTS="-Xms1g -Xmx1g" \
#   -v "$SCRIPTDIR:/FN-BEES-Services/" \
#   fn-platform-basic-api:omni_es

# V.8
# docker run --rm -it -d --publish 9203:9201 --expose 9201 \
#   --name fn-platform-omni-data-01 \
#   -e node.roles="[data, master]" \
#   -e node.name=fn-platform-omni-data-01 \
#   -e cluster.name=docker-elasticsearch \
#   -e cluster.initial_master_nodes=fn-platform-omni-data-01 \
#   -e discovery.seed_hosts=fn-platform-omni-data-01 \
#   -e cluster.routing.allocation.disk.threshold_enabled=false \
#   -e http.port=9201 \
#   -e ES_JAVA_OPTS="-Xms1g -Xmx1g" \
#   -e xpack.security.enabled=false \
#   -e xpack.security.http.ssl.enabled=false \
#   -e xpack.license.self_generated.type=basic \
#   -e action.destructive_requires_name=false \
#   -v "$SCRIPTDIR:/FN-BEES-Services/" \
#   fn-platform-basic-api:omni_es
  

docker run --rm --platform linux/amd64 -it -d \
  --name python-mcp-server-basic --publish 8000:8000 --expose 8000 \
  --network bridge \
  # -e ES_HOST=http://host.docker.internal:9203 \
  -e PYTHONUNBUFFERED=1 \
  -e LOG_LEVEL=DEBUG \
  -e FASTMCP_PORT=8000 \
  -e FASTMCP_TRANSPORT=sse \
  -e FASTMCP_DEBUG=true \
  -e FASTMCP_HOST=0.0.0.0 \
  -v "$SCRIPTDIR:/app" \
  python-mcp-server-basic:es


