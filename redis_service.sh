#!/bin/sh
REDIS_SERVICE_ALL_EXPORT_PATH=/home/devuser/monitoring/redis-5.0.7/
SERVICE_NAME=redis-service-all-service

# See how we were called.
case "$1" in
  start)
        # Start daemon.
        echo "🦄 Starting $SERVICE_NAME";
        # nohup $REDIS_SERVICE_ALL_EXPORT_PATH/src/redis-server $REDIS_SERVICE_ALL_EXPORT_PATH/redis.conf --protected-mode no &> /dev/null &
        $REDIS_SERVICE_ALL_EXPORT_PATH/src/redis-server $REDIS_SERVICE_ALL_EXPORT_PATH/redis.conf --protected-mode no
        ;;
  stop)
        # Stop daemons.
        echo "🦄 Shutting down $SERVICE_NAME";
        pid=`ps ax | grep -i '/src/redis-server' | grep -v grep | awk '{print $1}'`
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
        # Need to wait for two seconds to start python script via Fabric
        sleep 2
        ;;
  status)
        pid=`ps ax | grep -i '/src/redis-server' | grep -v grep | awk '{print $1}'`
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

