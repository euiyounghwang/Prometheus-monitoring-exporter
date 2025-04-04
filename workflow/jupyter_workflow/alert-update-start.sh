#!/bin/bash
set -e
ES_ALERT_UI_SERVICE_ALL_EXPORT_PATH='C://Users/euiyoung.hwang/Git_Workspace/Prometheus-monitoring-exporter/'
#ES_ALERT_UI_SERVICE_ALL_EXPORT_PATH='/home/devuser/monitoring/jupyter_notebook/'
SERVICE_NAME=es-alert-ui-service-all-service

#PATH=$PATH:$ES_ALERT_UI_SERVICE_ALL_EXPORT_PATH/bin

SCRIPTDIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
#echo $SCRIPTDIR
cd $SCRIPTDIR

VENV=".venv"

# Python 3.11.7 with Window
if [ -d "$VENV/bin" ]; then
    source $ES_ALERT_UI_SERVICE_ALL_EXPORT_PATH/$VENV/bin/activate
else
    source $ES_ALERT_UI_SERVICE_ALL_EXPORT_PATH/$VENV/Scripts/activate
fi


PROMETHEUS_HOST="dev:localhost,dev1:localhost"
API_HOST="localhost"
QA_LIST="QA1,QA2"
PROD_LIST="PROD1:company1,PROD2:company2"
GRAFANA_DASHBOARD_URL="http://localhost:3000/d/adm08055cf3lsa/es-team-dashboard?orgId=1&refresh=5s&from=now-5m&to=now"
CRONJOB_PATH="/apps/rest_api/es_config_interface/scripts"
GRADIO_USER="admin"
GRADIO_PASSWORD="1"

export PROMETHEUS_HOST
export API_HOST
export QA_LIST
export PROD_LIST
export GRAFANA_DASHBOARD_URL
export CRONJOB_PATH
export GRADIO_USER
export GRADIO_PASSWORD

# gradio run $SCRIPTDIR/Alert_Update.py 
# python $SCRIPTDIR/Alert_Update.py

# See how we were called.
case "$1" in
  start)
        # Start daemon.
        echo "🦄 Starting $SERVICE_NAME";
        #nohup python $SCRIPTDIR/Alert_Update.py &> /dev/null &
        python $SCRIPTDIR/Alert_Update.py
        ;;
  stop)
        # Stop daemons.
        echo "🦄 Shutting down $SERVICE_NAME";
        pid=`ps ax | grep -i '/Alert_Update.py' | grep -v grep | awk '{print $1}'`
        if [ -n "$pid" ]
          then
          kill -9 $pid
         else
          echo "🦄 $SERVICE_NAME was not Running"
        fi
        ;;
  restart)
        $0 stop
        sleep 2
        $0 start
        ;;
  status)
        pid=`ps ax | grep -i '/Alert_Update.py' | grep -v grep | awk '{print $1}'`
        if [ -n "$pid" ]
          then
          echo "🦄 $SERVICE_NAME is Running as PID: $pid"
        else
          echo "🦄 $SERVICE_NAME is not Running"
        fi
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
esac
