#!/bin/bash
set -e


SCRIPTDIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
cd $SCRIPTDIR

PATH='C://Users/euiyoung.hwang/Git_Workspace/Prometheus-monitoring-exporter/'

VENV=".venv"

# Python 3.11.7 with Window
if [ -d "$VENV/bin" ]; then
    source $PATH/$VENV/bin/activate
else
    source $PATH/$VENV/Scripts/activate
fi

PROMETHEUS_HOST="dev:localhost,dev1:localhost"
API_HOST="localhost"
QA_LIST="QA1,QA2"
PROD_LIST="PROD1:company1,PROD2:company2"
GRAFANA_DASHBOARD_URL="http://localhost:3000/d/adm08055cf3lsa/es-team-dashboard?orgId=1&refresh=5s&from=now-5m&to=now"
USER="devuser"


export PROMETHEUS_HOST
export API_HOST
export QA_LIST
export PROD_LIST
export GRAFANA_DASHBOARD_URL
export USER

# gradio run $SCRIPTDIR/Alert_Update.py 
python $SCRIPTDIR/Alert_Update.py
