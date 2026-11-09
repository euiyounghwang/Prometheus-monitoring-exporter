#!/bin/bash

# 기본 호스트명
HOST=$(hostname)

# FQDN (Fully Qualified Domain Name) 가져오기 [-f]
FQDN=$(hostname -f)

# 짧은 호스트명(Short hostname) 가져오기 [-s]
SHORT_HOST=$(hostname -s)

echo "Hostname: $HOST"
echo "FQDN: $FQDN"
echo "Short Host: $SHORT_HOST"