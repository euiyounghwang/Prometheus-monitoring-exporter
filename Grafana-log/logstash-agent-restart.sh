#!/bin/bash
set -e

LOGGING_SERVICE_ALL_EXPORT_PATH=/home/devuser/monitoring/log_to_logstash
SERVICE_NAME=python-logging-to-logstash-sparklogs

SCRIPTDIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
#echo $SCRIPTDIR

: <<'END'
dir="$SCRIPTDIR/logs"
echo $dir

if [[ ! -e $dir ]]; then
    mkdir $dir
fi
END

hn=$(hostname -f)
#echo $hn
host_name=`echo $hn | cut -d '.' -f 1`

# ---
# Get threshold from ES configuration API service
pid=`ps ax | grep -i '/push_to_logstash_script.py' | grep -v grep | awk '{print $1}'`
if [ -n "$pid" ]; then
    echo "[$host_name] $SERVICE_NAME is Running as PID: $pid"
else
    echo "[$host_name] $SERVICE_NAME was not Running"
    # --
    # Restart spark-logs aggregation agent if it was not running..
    # $LOGGING_SERVICE_ALL_EXPORT_PATH/push_to_logstash.sh start
fi
# ---

#--
#** Script for Log Agent Restart **
#*/5 * * * * /home/devuser/monitoring/log_to_logstash/push_to_logstash.sh start
#** ---------------------- **

