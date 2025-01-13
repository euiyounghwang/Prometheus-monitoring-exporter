#!/bin/bash
set -e

KIBANA_PATH="/apps/kibana/latest/bin/kibana"

SERVICE_NAME='kibana-instance-service'

SCRIPTDIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

pid=`ps ax | grep -i '/bin/kibana' | grep -v grep | awk '{print $1}'`
if [ -n "$pid" ]; then
    echo "$SERVICE_NAME is Running [$pid]"
else
    echo "$SERVICE_NAME was not Running"
    sudo $KIBANA_PATH &
fi

#--
#** Script for ES restart **
#*/10 * * * * /home/devuser/UtilityScripts/es-restart.sh localhost dev
#** ---------------------- **
