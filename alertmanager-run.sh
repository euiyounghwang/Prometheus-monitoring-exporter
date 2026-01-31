#!/bin/sh
ALERTMANAGER_EXPORT_PATH=/home/devuser/monitoring/alertmanager-0.20.0.linux-amd64
#PATH=$PATH:$ALERTMANAGER_EXPORT_PATH
SERVICE_NAME=alertmanager-service

# See how we were called.
case "$1" in
  start)
        # Start daemon.
        echo "Starting $SERVICE_NAME";
        #$ALERTMANAGER_EXPORT_PATH/alertmanager --config.file=$ALERTMANAGER_EXPORT_PATH/alertmanager.yml --web.external-url http://0.0.0.0:9093
        nohup $ALERTMANAGER_EXPORT_PATH/alertmanager --config.file=$ALERTMANAGER_EXPORT_PATH/alertmanager.yml --web.external-url http://0.0.0.0:9093 &> /dev/null &
        ;;
  stop)
        # Stop daemons.
        echo "Shutting down $SERVICE_NAME";
        pid=`ps ax | grep -i '/alertmanager.yml' | grep -v grep | awk '{print $1}'`
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
        pid=`ps ax | grep -i '/alertmanager.yml' | grep -v grep | awk '{print $1}'`
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
