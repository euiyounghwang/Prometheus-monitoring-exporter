#!/bin/bash
set -e

# Activate virtualenv && run serivce

SCRIPTDIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
cd $SCRIPTDIR

VENV=".venv"

# Python 3.11.7 with Window
if [ -d "$VENV/bin" ]; then
    source $VENV/bin/activate
else
    source $VENV/Scripts/activate
fi

# -- server/clinet based on HTTP
#python ./prometheus_client_export.py --host localhost --url http://{}:9999/health?kafka_url=localhost:29092,localhost:39092,localhost:49092"&"es_url=localhost:9200,localhost:9501,localhost:9503"&"kibana_url=localhost:5601"&"logstash_url=process
# -- logstash : Get the process from local instance
python ./prometheus_client_export.py --host localhost --url http://{}:9999/health?kafka_url=localhost:29092,localhost:39092,localhost:49092"&"es_url=localhost:9200,localhost:9501,localhost:9503"&"kibana_url=localhost:5601
