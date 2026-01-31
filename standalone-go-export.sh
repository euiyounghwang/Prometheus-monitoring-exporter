#!/bin/bash
set -e

JAVA_HOME='/home/biadmin/jdk1.8.0_151'
#PATH=$PATH:$JAVA_HOME
export PATH=$JAVA_HOME/bin:$PATH
export JAVA_HOME

# Activate virtualenv && run serivce

SCRIPTDIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
cd $SCRIPTDIR

VENV=".venv"

# Python 3.11.7 with Window
if [ -d "$VENV/bin" ]; then
    source $VENV/bin/activate
else
    source $VENV/Scripts/activate
fi

VENV=".venv"

# Python 3.11.7 with Window
# if [ -d "$ES_REDIS_CONFIGURATION_WRITE_PATH/$VENV/bin" ]; then
#     source $ES_REDIS_CONFIGURATION_WRITE_PATH/$VENV/bin/activate
# else
#     source $ES_REDIS_CONFIGURATION_WRITE_PATH/$VENV/Scripts/activate
# fi


# -- Export Variable
export GRAFANA_DASHBOARD_URL="http://localhost:3000/d/adm08055cf3lsa/es-team-dashboard?orgId=1'&'from=now-5m'&'to=now'&'refresh=5s"
export SMTP_HOST="localhost"
export SMTP_PORT=212
export MAIL_SENDER="mymail"
export ES_CONFIGURATION_URL="http://localhost:8004/docs"
export ES_CONFIGURATION_HOST="localhost"
export REMOTE_AGENT_HOST="localhost"
# -- 

export PYTHONDONTWRITEBYTECODE=1

python ./standalone-go-export.py --env_name localhost --es_url localhost:9200,localhost:9201,localhost:9201,localhost:9200
