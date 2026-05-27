#!/bin/sh
KAFKA_METRICS_EXPORT_PATH=/home/devuser/monitoring/metrics_socket
SERVICE_NAME=es-service-purge-script-service

SCRIPTDIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

process_name='/home/biadmin/monitoring/metrics_socket/purge_script.py'

# See how we were called.
case "$1" in
  start)
        PID=$(ps -ef | grep $process_name | grep -v grep)
        test=$?
        if [ $test -eq 0 ]
        then
          PID=$(ps -ef | grep $process_name | grep -v grep | tr -s ' ' | cut -d " " -f2)
          echo $SERVICE_NAME is Running as $PID
          #kill -9 $PID
        else
          # Start daemon.
          echo "🦄 Starting $SERVICE_NAME";
          # nohup python $SCRIPTDIR/purge_script.py --server_port 8001 --spark_log /apps/var/spark/logs --kafka_log /apps/kafka/latest/logs --interval 3600 --delete_interval 2 &> /dev/null &
          python $SCRIPTDIR/purge_script.py --server_port 8001 --spark_log /apps/var/spark/logs --kafka_log /apps/kafka/latest/logs --interval 3600 --delete_interval 2
        fi
        ;;
  stop)
        # Stop daemons.
        echo "🦄 Shutting down $SERVICE_NAME";
        pid=`ps ax | grep -i '/purge_script.py' | grep -v grep | awk '{print $1}'`
        if [ -n "$pid" ]
          then
          kill -9 $pid
         else
          echo "🦄 $SERVICE_NAME was not Running"
        fi
        ;;
  restart)
        $0 stop
        sleep 2
        $0 start
        ;;
  status)
        pid=`ps ax | grep -i '/purge_script.py' | grep -v grep | awk '{print $1}'`
        if [ -n "$pid" ]
          then
          echo "🦄 $SERVICE_NAME is Running as PID: $pid"
        else
          echo "🦄 $SERVICE_NAME is not Running"
        fi
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
esac

