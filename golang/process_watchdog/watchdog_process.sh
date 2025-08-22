
#!/bin/bash
set -e

WATCHDOG_SERVICE_PATH=/home/devuser/monitoring/log_to_logstash
SERVICE_NAME=watchdog-service-auto-start

# Arguments for the script
export GREP_PROCESS="/apps/logstash/latest/config/"
# LOGSTASH PORT CHECK
export CHECK_PORTS="':(5043|5044|5045|5046|5047|5048)'"


case "$1" in
  start)
        # Start daemon.
        echo "Starting $SERVICE_NAME";
        #nohup $WATCHDOG_SERVICE_PATH/process_autostart &> /dev/null &
        $WATCHDOG_SERVICE_PATH/process_autostart
        ;;
  stop)
        # Stop daemons.
        echo "Shutting down $SERVICE_NAME";
        pid=`ps ax | grep -i '/process_autostart' | grep -v grep | awk '{print $1}'`
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
        pid=`ps ax | grep -i '/process_autostart' | grep -v grep | awk '{print $1}'`
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
