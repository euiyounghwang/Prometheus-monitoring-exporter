#!/bin/bash

set -eu

#docker build --no-cache \

docker build \
  -f "$(dirname "$0")/Dockerfile" \
  -t go-exporter-api:es \
  --target runtime \
  "$(dirname "$0")/."