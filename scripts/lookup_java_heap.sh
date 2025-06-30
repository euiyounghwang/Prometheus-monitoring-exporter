#!/bin/bash
set -e

# Check if ES Java Heap file exists

hn=$(hostname -f)
#echo $hn
host_name=`echo $hn | cut -d '.' -f 1`
echo $host_name

SCRIPTDIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
echo $SCRIPTDIR


ES_PATH="/apps/elasticsearch/latest"
#ES_PATH="/apps/scripts"

CURRENT=$(df /apps | grep / | awk '{ print $5}' | sed 's/%//g')
echo "Current /apps usage : $CURRENT"%

#--
# config for email address via API endpoint
#--
es_config_api_host="localhost"

# ---
# Get threshold from ES configuration API service
curl_host="http://$es_config_api_host:8004/config/get_gloabl_config"

# Need to update the host name of Logstash instance each env.
email_address=$(curl -s $curl_host | jq '.config.shell_script_mail_address')
echo $email_address


lookup_heap_dump()
{
    #echo $ES_PATH
    for file in $ES_PATH/*.hprof
    do
        if [ -f "${file}" ]; then
            echo  "HEAP_DUMP_FILE EXISTS : $file"
                # Send an email if HEAP DUMP FILE exists
                mailx -s '[Dev] Monitoring Script for elasticsearch [Disk Space Alert]' $email_address << EOF
Your $host_name has $file. Used: $CURRENT%
EOF
            break
        else
            echo "$ES_PATH -> JAVA HEAP DUMP FILE NOT EXISTS"
        fi
    done
}



#- check java heap dump file exists
lookup_heap_dump

#--
#** Script for Java Heap file **
# */10 * * * * /home/devuser/UtilityScripts/lookup_java_heap.sh
#** ---------------------- **
