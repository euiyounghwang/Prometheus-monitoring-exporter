#!/bin/sh
LOGGING_SERVICE_ALL_EXPORT_PATH=/home/devuser/monitoring/log_to_loki
PATH=$PATH:$LOGGING_SERVICE_ALL_EXPORT_PATH/bin
SERVICE_NAME=grafana-logging-to-loki-service-all-service

export LOKI_RESTAPI_HOST="localhost"
export ENV="DEV"

path="/home/devuser"
hostname="Data_Transfer_Node_#1"
logging_file_list="test.log"

# python ./push_to_loki_script.py --path /home/devuser --filename test1.log --hostname Data_Transfer_Node_#1

# See how we were called.
case "$1" in
  start)
        # Start daemon.
        echo "Starting $SERVICE_NAME";
        # nohup python $LOGGING_SERVICE_ALL_EXPORT_PATH/push_to_loki_script.py --path $path --filename $logging_file_list --hostname $hostname &> /dev/null &
        python $LOGGING_SERVICE_ALL_EXPORT_PATH/push_to_loki_script.py --path $path --filename $logging_file_list --hostname $hostname
        ;;
  stop)
        # Stop daemons.
        echo "Shutting down $SERVICE_NAME";
        pid=`ps ax | grep -i '/push_to_loki_script.py' | grep -v grep | awk '{print $1}'`
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
        pid=`ps ax | grep -i '/push_to_loki_script.py' | grep -v grep | awk '{print $1}'`
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

