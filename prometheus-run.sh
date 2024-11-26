#!/bin/sh
PROMETHEUS_EXPORT_PATH=/home/devuser/monitoring/prometheus-2.37.0.linux-amd64/
PATH=$PATH:$PROMETHEUS_EXPORT_PATH/bin
SERVICE_NAME=prometheus-service

# See how we were called.
case "$1" in
  start)
        # Start daemon.
        echo "Starting $SERVICE_NAME";
        nohup $PROMETHEUS_EXPORT_PATH/prometheus --config.file=$PROMETHEUS_EXPORT_PATH/prometheus.yml --storage.tsdb.retention.time=14d --storage.tsdb.retention.size=2GB --web.enable-admin-api --storage.tsdb.path=$PROMETHEUS_EXPORT_PATH &> /dev/null &
        ;;
  stop)
        # Stop daemons.
        echo "Shutting down $SERVICE_NAME";
        pid=`ps ax | grep -i '/prometheus.yml' | grep -v grep | awk '{print $1}'`
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
        pid=`ps ax | grep -i '/prometheus.yml' | grep -v grep | awk '{print $1}'`
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

