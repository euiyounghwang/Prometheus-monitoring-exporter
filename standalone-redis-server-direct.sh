#!/bin/sh

#ES_REDIS_CONFIGURATION_WRITE_PATH=/home/devuser/monitoring/custom_export
SCRIPTDIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

echo "Starting $SERVICE_NAME";
source $SCRIPTDIR/.venv/bin/activate
python $SCRIPTDIR/standalone-redis-server-script.py