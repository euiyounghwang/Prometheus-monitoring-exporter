#!/bin/sh
LOG_AGG_SERVICE_PATH=/home/devuser/monitoring/custom_export
#PATH=$PATH:$LOG_AGG_SERVICE_PATH
SERVICE_NAME=log-aggregatopm-alert-service

SCRIPTDIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

VENV=".venv"

# Python 3.11.7 with Window
if [ -d "$SCRIPTDIR/$VENV/bin" ]; then
    source $SCRIPTDIR/$VENV/bin/activate
else
    source $SCRIPTDIR/$VENV/Scripts/activate
fi

#--
# Alert for text error logs from Dev ES Cluster with logstash-logger-*
#--

# See how we were called.
case "$1" in
  start)
        # Start daemon.
        echo "Starting $SERVICE_NAME";
        #nohup python $LOG_AGG_SERVICE_PATH/logstash-agent-alert.py &> /dev/null &
        python $LOG_AGG_SERVICE_PATH/logstash-agent-alert.py --ts http://localhost:9200
        ;;
  stop)
        # Stop daemons.
        echo "Shutting down $SERVICE_NAME";
        pid=`ps ax | grep -i '/logstash-agent-alert.py' | grep -v grep | awk '{print $1}'`
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
        pid=`ps ax | grep -i '/logstash-agent-alert.py' | grep -v grep | awk '{print $1}'`
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

