#!/bin/bash
set -e

SERVICE_NAME='prometheus-gather-server-service'

SCRIPTDIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

pid=`ps ax | grep -i '/server.py' | grep -v grep | awk '{print $1}'`
if [ -n "$pid" ]; then
    echo "$SERVICE_NAME is Running [$pid]"
else
    echo "$SERVICE_NAME was not Running"
    sudo $SCRIPTDIR/prometheus-gather-server.sh start
    
fi

#--
#** metrics for disk usage **
#*/10 * * * * /home/devuser/monitoring/metrics_socket/metrics_start.sh
#** ---------------------- **

