#!/bin/bash
set -e

SCRIPTDIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
cd $SCRIPTDIR

# -- Export Variable
export GRAFANA_DASHBOARD_URL="http://localhost:3000/d/adm08055cf3lsa/es-team-dashboard?orgId=1'&'from=now-5m'&'to=now'&'refresh=5s"
export ZOOKEEPER_URLS="localhost:2181,localhost:2181,localhost:2181"
export BROKER_LIST="localhost:9092,localhost:9092,localhost:9092"
export GET_KAFKA_ISR_LIST="$SCRIPTDIR/kafka_2.11-0.11.0.0/bin/kafka-topics.sh --describe --zookeeper $ZOOKEEPER_URLS --topic ELASTIC_PIPELINE_QUEUE"

# -- 

python $SCRIPTDIR/mail/terminal_test.py
