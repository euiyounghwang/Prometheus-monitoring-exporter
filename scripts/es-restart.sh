#!/bin/bash
set -e

# Check ES Instance & Restart ES
# ./es-restart.sh localhost_api dev

es_config_api_host=$1
env_name=$2

if [[ ! "$es_config_api_host" ]]; then
    echo "'es_config_api_host' argument error"
fi

if [[ ! "$env_name" ]]; then
    echo "'env_name' argument error"
    exit 0
fi

: <<'END'
if [[ -n "$es_config_api_host" ]]; then
    #echo "$1=$( date +%s )" >> ${log_file}
    # echo $es_config_api_host
else
    echo "'es_config_api_host' argument error"
fi

if [[ -n "$env_name" ]]; then
    #echo "$1=$( date +%s )" >> ${log_file}
    # echo $env_name
else
    echo "'env_name' argument error"
fi
END

hn=$(hostname -f)
#echo $hn
host_name=`echo $hn | cut -d '.' -f 1`
#echo $host_name

SCRIPTDIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
#echo $SCRIPTDIR

: <<'END'
dir="$SCRIPTDIR/logs"
echo $dir

if [[ ! -e $dir ]]; then
    mkdir $dir
fi
END

insert_log()
{
    echo "[$host_name] Inserted logs into h2 database through ES configuration API"
    JSON_STRING="{
        \"env\" : \"$env_name\",
        \"host_name\" : \"$host_name\",
        \"status\" : \"$1",
        \"message\" : \"ES TEAM SCRIPT\"
    }"

    #echo $JSON_STRING > a.out

    #cmd=`curl -X POST "http://$es_config_api_host:8004/log/create_log" --header "Content-Type:application/json" -d @a.out`
    cmd=`curl -X POST "http://$es_config_api_host:8004/log/create_log" --header "Content-Type:application/json" -d "$JSON_STRING"`

    response=`echo $cmd `
    echo "Response - $response"
}


ES_PATH="/apps/elasticsearch/latest"

lookup_heap_dump()
{
    #echo $ES_PATH
    for file in $ES_PATH/*.hprof
    do
      if [ -f "${file}" ]; then
        echo 'true';
        insert_log "HEAP_DUMP_FILE EXISTS"
        break
      else
        echo "$ES_PATH -> JAVA HEAP DUMP FILE NOT EXISTS"
      fi
    done
}


#- check java heap dump file exists
lookup_heap_dump


# ---
# Get threshold from ES configuration API service
curl_host="http://$es_config_api_host:8004/config/get_mail_config"

# Need to update the host name of Logstash instance each env.
alert=$(curl -s $curl_host | jq '.localhost.is_mailing')
#echo $alert
SERVICE_NAME=elasticsearch
# insert_log "BATCH SCRIPT"
if [[ -n "$alert" ]]; then
    pid=`ps ax | grep -i '/elasticsearch' | grep -v grep | awk '{print $1}'`
    if [ -n "$pid" ]; then
        echo "[$host_name] $SERVICE_NAME is Running"
    else
        echo "[$host_name] $SERVICE_NAME was not Running"
        if [ "$alert" == "true" ]; then
            echo "[$host_name] Need to start $SERVICE_NAMEES service cmd"
            # --
            # Restart ES Instance
            # sudo service elasticsearch start
            # --
            insert_log "ES_RESTARTED"
        else
            echo "[$host_name] Not started $SERVICE_NAMEES due to alert [$alert]"
        fi
    fi
else
   echo "Request failed"
   echo $curl_host
fi
# ---

#--
#** Script for ES restart **
*/10 * * * * /home/devuser/UtilityScripts/es-restart.sh localhost dev
#** ---------------------- **

