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

# -- 
# global variable
# set the PYTHONDONTWRITEBYTECODE environment variable to 1. This stops Python from creating cache files globally or within your environment.
# or 
# Pass the -B flag to the Python command when executing your script:
# set PYTHONDONTWRITEBYTECODE=1
export PYTHONDONTWRITEBYTECODE=1
# --

ENV=new-dev

# python ./ssh_client.py --env dev --service elasticsearch --cmd "ps ax | grep -i '/elasticsearch' | grep -v grep | awk '{print \$1}'"

echo "ENV : $ENV"

# start command smoke
# please add the name of service in order
# Fullly start services in order
python ./ssh_service_check.py --env $ENV --service elasticsearch,logstash,kibana,kafka,kafka_connect,spark_cluster,spark_app --cmd "start"
# Unit Test
# python ./ssh_service_check.py --env $ENV --service logstash,kibana --cmd "start"
# please add the name of service in order
# Full stop services in order
# python ./ssh_service_check.py --env $ENV --service spark_app,spark_cluster,kafka_connect,kafka,kibana,logstash,elasticsearch --cmd "stop"
# Unit Test
# python ./ssh_service_check.py --env $ENV --service logstash,kibana --cmd "stop"


