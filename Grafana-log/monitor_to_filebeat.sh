#!/bin/sh
FILEBEAT_METRICS_EXPORT_PATH=/home/devuser/monitoring/log_to_logstash
SERVICE_NAME=es-service-filebeat-gather-service

SCRIPTDIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

# See how we were called.
case "$1" in
  start)
        # Start daemon.
        echo "Starting $SERVICE_NAME";
        # nohup python $FILEBEAT_METRICS_EXPORT_PATH/monitor_to_filebeat.py &> /dev/null &
        python $FILEBEAT_METRICS_EXPORT_PATH/monitor_to_filebeat.py
        ;;
  stop)
        # Stop daemons.
        echo "Shutting down $SERVICE_NAME";
        pid=`ps ax | grep -i '/monitor_to_filebeat.py' | grep -v grep | awk '{print $1}'`
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
        pid=`ps ax | grep -i '/monitor_to_filebeat.py' | grep -v grep | awk '{print $1}'`
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

