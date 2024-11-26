#!/bin/sh
GRAFANA_EXPORT_PATH=/home/devuser/monitoring/grafana-v10.4.2/
PATH=$PATH:$GRAFANA_EXPORT_PATH/bin
SERVICE_NAME=grafana-service

# See how we were called.
case "$1" in
  start)
        # Start daemon.
        echo "Starting $SERVICE_NAME";
        nohup $GRAFANA_EXPORT_PATH/bin/grafana-server --homepath  $GRAFANA_EXPORT_PATH --config= $GRAFANA_EXPORT_PATH/conf/defaults.ini &> /dev/null &
        ;;
  stop)
        # Stop daemons.
        echo "Shutting down $SERVICE_NAME";
        pid=`ps ax | grep -i '/grafana-v10' | grep -v grep | awk '{print $1}'`
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
        pid=`ps ax | grep -i '/grafana-v10' | grep -v grep | awk '{print $1}'`
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

