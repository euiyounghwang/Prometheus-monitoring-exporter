#!/bin/bash

set -eu

#docker build --no-cache \


docker build \
  -f "$(dirname "$0")/Dockerfile" \
  -t python-mcp-server-basic:es \
  --target runtime \
  "$(dirname "$0")/."


# 이미지 빌드 및 컨테이너 시작 및 백그라운드
#$ docker-compose up -d --build

# 로그 확인 (백그라운드 실행 시)
#$ docker-compose logs -f

# 서버 중지
#$ docker-compose down

# 동시 실행
#$ docker-compose down & docker-compose up -d --build & docker-compose logs -f