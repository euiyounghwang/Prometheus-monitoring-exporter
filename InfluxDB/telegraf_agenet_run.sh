#!/bin/sh
TELEGRAF_AGENT="/home/devuser/monitoring/custom_export/telegraf-1.34.2/"
SERVICE_NAME=telegraf-agent-service


# See how we were called.
case "$1" in
  start)
        # Start daemon.
        echo "Starting $SERVICE_NAME";
        # nohup $TELEGRAF_AGENT/usr/bin/telegraf --config $TELEGRAF_AGENT/etc/telegraf/telegraf.conf &> /dev/null &
        $TELEGRAF_AGENT/usr/bin/telegraf --config $TELEGRAF_AGENT/etc/telegraf/telegraf.conf
        ;;
  stop)
        # Stop daemons.
        echo "Shutting down $SERVICE_NAME";
        pid=`ps ax | grep -i '//telegraf-1.34.2' | grep -v grep | awk '{print $1}'`
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
        pid=`ps ax | grep -i '//telegraf-1.34.2' | grep -v grep | awk '{print $1}'`
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

