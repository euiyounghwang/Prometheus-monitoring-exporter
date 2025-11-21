#!/bin/bash
set -e


# Activate virtualenv && run serivce

ROOTDIR=$(pwd)
SCRIPTDIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"


VENV=".venv"

# Python 3.11.7 with Window
if [ -d "$VENV/bin" ]; then
    source $ROOTDIR/$VENV/bin/activate
else
    source $ROOTDIR/$VENV/Scripts/activate
fi

# ssh commands
# sh -c 'sudo su - spark -c "./utils/sparkSubmitWMx.sh status"'
# sh -c 'sudo ~/utils/kafkaUtil.sh status'
# sh -c 'sudo ~/utils/connectUtil.sh status'
# sh -c 'sudo su - elasticsearch -c "/apps/elasticsearch/latest/bin/elasticsearch -d"'
# "sudo netstat -npl --inet | awk '/:9200/ {print $7}' | awk -F \"[ /]+\" '{print $1}'"

# python $SCRIPTDIR/ssh-client.py --service elasticsearch --cmd "ls -l"
# python $SCRIPTDIR/ssh-clients.py --service elasticsearch --cmd "ps ax | grep -i '/elasticsearch' | grep -v grep | awk '{print \$1}'"

# start commands
# python ./ssh-client.py --env dev --service elasticsearch --cmd "start"
# python ./ssh-client.py --env dev --service elasticsearch --cmd "stop"