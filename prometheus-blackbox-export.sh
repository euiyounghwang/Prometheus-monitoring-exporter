#!/bin/sh
SERVICE_EXPORT_PATH=/home/devuser/monitoring/es_monitoring/blackbox_exporter-0.28.0.linux-386
PATH=$PATH:$SERVICE_EXPORT_PATH/bin
SERVICE_NAME=prometheus-blackbox_exporter-service

# See how we were called.
case "$1" in
  start)
        # Start daemon.
        echo "Starting $SERVICE_NAME";
        #nohup $SERVICE_EXPORT_PATH/blackbox_exporter --config.file=./blackbox.yml &> /dev/null &
        $SERVICE_EXPORT_PATH/blackbox_exporter --config.file=$SERVICE_EXPORT_PATH/blackbox.yml
        ;;
  stop)
        # Stop daemons.
        echo "Shutting down $SERVICE_NAME";
        pid=`ps ax | grep -i '/blackbox_exporter' | grep -v grep | awk '{print $1}'`
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
        pid=`ps ax | grep -i '/blackbox_exporter' | grep -v grep | awk '{print $1}'`
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

