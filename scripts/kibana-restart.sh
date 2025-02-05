#!/bin/bash
set -e

KIBANA_PATH="/apps/kibana/latest/bin/kibana"

SERVICE_NAME='kibana-instance-service'

SCRIPTDIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

hn=$(hostname -f)
#echo $hn
host_name=`echo $hn | cut -d '.' -f 1`
#echo $host_name

#es_config_api_host=$1
es_config_api_host='localhost'

# Get threshold from ES configuration API service
curl_host="http://$es_config_api_host:8004/config/get_mail_config"

# Need to update the host name of Logstash instance each env.
alert=$(curl -s $curl_host | jq '.localhost.is_mailing')
#echo $alert
SERVICE_NAME=kibana
# insert_log "BATCH SCRIPT"
if [[ -n "$alert" ]]; then
    pid=`ps ax | grep -i '/bin/kibana' | grep -v grep | awk '{print $1}'`
    if [ -n "$pid" ]; then
        echo "[$host_name] $SERVICE_NAME is Running"
    else
        echo "[$host_name] $SERVICE_NAME was not Running"
        if [ "$alert" == "true" ]; then
            echo "[$host_name] Need to start $SERVICE_NAMEES service cmd"
            # sudo $KIBANA_PATH &
            # insert_log "KIBANA_RESTARTED"
        else
            echo "[$host_name] Not started $SERVICE_NAMEES due to alert [$alert]"
        fi
    fi
else
   echo "Request failed"
   echo $curl_host
fi

#** Kibana
#*/10 * * * * /home/devuser/UtilityScripts/kibana-restart.sh

