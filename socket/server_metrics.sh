#!/bin/sh
KAFKA_METRICS_EXPORT_PATH=/home/biadmin/monitoring/metrics_socket
SERVICE_NAME=es-service-server-gather-service

SCRIPTDIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

process_name='/home/biadmin/monitoring/metrics_socket/server_metrics.py'

SCRIPTDIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
cd $SCRIPTDIR

echo "Running Path .. $SCRIPTDIR"

VENV=".venv"

# Python 3.11.7 with Window
if [ -d "$VENV/bin" ]; then
    source $VENV/bin/activate
else
    source $VENV/Scripts/activate
fi

# Cronjob
# -----
# Disk Service
# Go to DT nodes and sudo su
# */10 * * * * su - biadmin -c "/home/biadmin/monitoring/metrics_socket/server_metrics.sh start"
# Purge Service
# */10 * * * * su - biadmin -c "/home/biadmin/monitoring/metrics_socket/purge_script.sh start"
# Resource Service
# */10 * * * * su - biadmin -c "/home/biadmin/monitoring/metrics_socket/server_metrics.sh start"
# ----


# See how we were called.
case "$1" in
  start)
        PID=$(ps -ef | grep $process_name | grep -v grep)
        test=$?
        if [ $test -eq 0 ]
        then
          PID=$(ps -ef | grep $process_name | grep -v grep | tr -s ' ' | cut -d " " -f2)
          echo $SERVICE_NAME is Running as $PID
          #kill -9 $PID
        else
          # Start daemon.
          echo "Starting $SERVICE_NAME";
        #   nohup python $SCRIPTDIR/server_metrics.py &> /dev/null &
          python $SCRIPTDIR/server_metrics.py
        fi
        ;;
  stop)
        # Stop daemons.
        echo "Shutting down $SERVICE_NAME";
        pid=`ps ax | grep -i '/server_metrics.py' | grep -v grep | awk '{print $1}'`
        if [ -n "$pid" ]
          then
          kill -9 $pid
         else
          echo "$SERVICE_NAME was not Running"
        fi
        ;;
  restart)
        $0 stop
        sleep 2
        $0 start
        ;;
  status)
        pid=`ps ax | grep -i '/server_metrics.py' | grep -v grep | awk '{print $1}'`
        if [ -n "$pid" ]
          then
          echo "$SERVICE_NAME is Running as PID: $pid"
        else
          echo "$SERVICE_NAME is not Running"
        fi
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
esac

