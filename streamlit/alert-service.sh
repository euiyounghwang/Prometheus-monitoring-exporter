#!/bin/sh
ALERT_SERVICE_ALL_EXPORT_PATH=/home/devuser/rest_api/streamlit
PATH=$PATH:$ALERT_SERVICE_ALL_EXPORT_PATH/bin
SERVICE_NAME=es-alert-service

# See how we were called.
case "$1" in
  start)
        # Start daemon.
        echo "Starting $SERVICE_NAME";
        #nohup $ALERT_SERVICE_ALL_EXPORT_PATH/alert-ui.sh &> /dev/null &
        $ALERT_SERVICE_ALL_EXPORT_PATH/alert-ui.sh
        ;;
  stop)
        # Stop daemons.
        echo "Shutting down $SERVICE_NAME";
        pid=`ps ax | grep -i '/streamlit' | grep -v grep | awk '{print $1}'`
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
        pid=`ps ax | grep -i '/streamlit' | grep -v grep | awk '{print $1}'`
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
