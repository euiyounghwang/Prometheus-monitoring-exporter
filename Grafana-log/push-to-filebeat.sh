#!/bin/sh
LOGGING_SERVICE_ALL_EXPORT_PATH=/home/devuser/monitoring/filebeat-5.6.16-linux-x86_64
#PATH=$PATH:$LOGGING_SERVICE_ALL_EXPORT_PATH
SERVICE_NAME=filebeat-to-logstash-sparklogs


# See how we were called.
case "$1" in
  start)
        # Start daemon.
        echo "Starting $SERVICE_NAME";
        nohup $LOGGING_SERVICE_ALL_EXPORT_PATH/filebeat -c $LOGGING_SERVICE_ALL_EXPORT_PATH/filebeat.yml &> /dev/null &
        # $LOGGING_SERVICE_ALL_EXPORT_PATH/filebeat -e -c $LOGGING_SERVICE_ALL_EXPORT_PATH/filebeat.yml -d "publish" &
        #$LOGGING_SERVICE_ALL_EXPORT_PATH/filebeat -c $LOGGING_SERVICE_ALL_EXPORT_PATH/filebeat.yml
        ;;
  stop)
        # Stop daemons.
        echo "Shutting down $SERVICE_NAME";
        pid=`ps ax | grep -i '/filebeat.yml' | grep -v grep | awk '{print $1}'`
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
        pid=`ps ax | grep -i '/filebeat.yml' | grep -v grep | awk '{print $1}'`
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

