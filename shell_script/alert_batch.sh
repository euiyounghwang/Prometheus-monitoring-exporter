#/bin/bash

# Update alert value

# 1: Monday, 6: Saturday, Sunday : 0
# every Friday
#00 23 * * 5 /home/devuser/es_config_interface/scripts/alert_batch.sh localhost dev false
#00 07 * * 5 /home/devuser/es_config_interface/scripts/alert_batch.sh localhost dev true

# cache with job
#/home/devuser/es_config_interface/scripts/alert_job_batch.sh localhost dev false
#/home/devuser/es_config_interface/scripts/alert_job_batch.sh localhost dev true

host=$1
env_name=$2
alert=$3

SCRIPTDIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
echo $SCRIPTDIR

dir="$SCRIPTDIR/logs"
echo $dir

if [[ ! -e $dir ]]; then
    mkdir $dir
fi

log_file="$dir/logfile.$(date +'%Y-%m-%d').log"

if [[ -n "$env_name" ]]; then
    #echo "$1=$( date +%s )" >> ${log_file}
    echo $env_name
else
    echo "'env_name' argument error"
fi

if [[ -n "$alert" ]]; then
    echo $alert
else
    echo "'alert' argument error"
fi

env_names=$(echo $env_name | tr "," "\n")


: <<'END'
curl -X 'POST' \
  'http://localhost:8004/config/update_mail_config' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "env": "dev",
  "alert": "false"
}'
END


#SET=$(seq 0 9)
#for i in $SET
for env_name in $env_names
do
    echo "Alert Updatinng.. "$env_name  
    JSON_STRING="{
        \"env\" : \"$env_name\",
        \"alert\" : \"$alert\",
        \"message\" : \"ES TEAM SCRIPT\"
    }"

    echo $JSON_STRING > a.out

    cmd=`curl -X POST "http://$host:8004/config/update_mail_config" --header "Content-Type:application/json" -d @a.out`

    response=`echo $cmd `
    echo "Response - $response"

    echo >> $log_file
    echo >> $log_file
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] http://$host:8004/config/update_mail_config --header \"Content-Type:application/json\"" >> $log_file
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $JSON_STRING" >> $log_file
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $response" >> $log_file
done

: <<'END'
# Validate
curl_host="http://$host:8004/config/get_mail_config"

#THRESHOLD=$(curl -s $curl_host | jq '.config.disk_usage_percentage_threshold')
ALL_JSON=$(curl -s $curl_host | jq '.')
if [[ -n "$ALL_JSON" ]]; then
   echo "# ES Configuration"
   #echo $ALL_JSON | python -mjson.tool
   env_upper=`echo $env_names | tr '[a-z]' '[A-Z]'`
   mailx -s "[$env_upper] Prometheus Monitoring API - Alert Update" test@1234 << EOF
   $ALL_JSON | python -mjson.tool
EOF
fi
END

#---
# Create cronjob for the alert
# 40 06 17 12 *  /home/devuser/es_config_interface/scripts/alert_job_batch.sh localhost qa13,qa14 false
# 00 16 17 12 *  /home/biadmin/es_config_interface/scripts/alert_job_batch.sh localhost qa13,qa14 true
#---
