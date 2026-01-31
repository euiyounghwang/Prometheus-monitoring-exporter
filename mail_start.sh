#!/bin/bash
set -e

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

# -- Export Variable
export GRAFANA_DASHBORD_URL="http://localhost:3000/d/adm08055cf3lsa/es-team-dashboard?orgId=1'&'from=now-5m'&'to=now'&'refresh=5s"
export EMAIL_LIST="test@mail.com"
# -- 

python $SCRIPTDIR/mail/mail_alert.py
