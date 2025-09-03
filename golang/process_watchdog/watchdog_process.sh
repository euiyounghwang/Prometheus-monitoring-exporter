
#!/bin/bash
set -e

WATCHDOG_SERVICE_PATH=/home/devuser/monitoring/log_to_logstash
SERVICE_NAME=watchdog-service-auto-start

# -- logstash
#export GREP_PROCESS="/apps/logstash/latest/config/"
export GREP_PROCESS="/apps/logstash/logstash-5.6.4"
export PROCESS_NAME="logstash"
export PROCESS_CMD="sudo service logstash start"

# -- kibana
#export GREP_PROCESS="/apps/kibana/latest/"
#export PROCESS_NAME="kibana"
#export PROCESS_CMD="sudo /apps/kibana/latest/bin/kibana &"

#export GREP_COMMAND_AX="ps ax | grep -i '/apps/logstash/latest/logstash-core' | grep -v grep | awk '{print $1}'"
# LOGSTASH PORT CHECK
#export CHECK_PORTS="':(5043|5044|5045|5046|5047|5048)'"

# -- Cronjob Autostart
#*/30 * * * * /home/biadmin/UtilityScripts/watchdog_process.sh start


case "$1" in
  start)
        pid=`ps ax | grep -i '/process_autostart' | grep -v grep | awk '{print $1}'`
        if [ -n "$pid" ]
          then
          echo "$SERVICE_NAME is Running as PID: $pid"
         else
          # Start daemon.
          echo "Starting $SERVICE_NAME";
          #nohup $WATCHDOG_SERVICE_PATH/process_autostart &> /dev/null &
          $WATCHDOG_SERVICE_PATH/process_autostart
        fi
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
