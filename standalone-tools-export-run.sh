#!/bin/bash
set -e


SCRIPTDIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
cd $SCRIPTDIR

VENV=".venv"

# Python 3.11.7 with Window
if [ -d "$VENV/bin" ]; then
    source $VENV/bin/activate
else
    source $VENV/Scripts/activate
fi


# Python 3.11.7 with Window
# if [ -d "$ES_REDIS_CONFIGURATION_WRITE_PATH/$VENV/bin" ]; then
#     source $ES_REDIS_CONFIGURATION_WRITE_PATH/$VENV/bin/activate
# else
#     source $ES_REDIS_CONFIGURATION_WRITE_PATH/$VENV/Scripts/activate
# fi


# -- Export Variable
export GRAFANA_DASHBOARD_URL="http://localhost:3000/d/adm08055cf3lsa/es-team-dashboard?orgId=1'&'from=now-5m'&'to=now'&'refresh=5s"
export PROMETHEUS_APPS_HOST="localhost"
export PROMETHEUS_LOOKUP_HOST="localhost"
export PROMETHEUS_USERNAME="test"
export PROMETHEUS_PASSWORD="test"


# -- standalone type
# local
python ./standalone-tools-service-export.py
