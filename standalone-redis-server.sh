#!/bin/sh

# -- Redis
#sudo $SCRIPTDIR/src/redis-server $SCRIPTDIR/redis.conf --protected-mode no

#redis-cli --cluster create 127.0.0.1:6379 127.0.0.1:6479 127.0.0.1:6579
#redis-cli --cluster create --replicas  1 127.0.0.1:6379 127.0.0.1:6479 127.0.0.1:6579

SCRIPTDIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

# -- Batch 

#!/bin/sh
ES_REDIS_CONFIGURATION_WRITE_PATH=/home/devuser/monitoring/custom_export
SERVICE_NAME=es-configuration-service

VENV=".venv"

# Python 3.11.7 with Window
if [ -d "$ES_REDIS_CONFIGURATION_WRITE_PATH/$VENV/bin" ]; then
    source $ES_REDIS_CONFIGURATION_WRITE_PATH/$VENV/bin/activate
else
    source $ES_REDIS_CONFIGURATION_WRITE_PATH/$VENV/Scripts/activate
fi

# See how we were called.
case "$1" in
  start)
        # Start daemon.
        echo "Starting $SERVICE_NAME";
        source $SCRIPTDIR/.venv/bin/activate
        nohup python $ES_REDIS_CONFIGURATION_WRITE_PATH/standalone-redis-server-script.py &> /dev/null &
        #python $ES_REDIS_CONFIGURATION_WRITE_PATH/standalone-redis-server-script.py
        ;;
  stop)
        # Stop daemons.
        echo "Shutting down $SERVICE_NAME";
        pid=`ps ax | grep -i '/standalone-redis-server-script.py' | grep -v grep | awk '{print $1}'`
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
        pid=`ps ax | grep -i '/standalone-redis-server-script.py' | grep -v grep | awk '{print $1}'`
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