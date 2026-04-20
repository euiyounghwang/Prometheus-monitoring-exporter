#!/bin/sh
ES_SERVICE_ALL_EXPORT_PATH=/home/devuser/monitoring/otel
#PATH=$PATH:$ES_SERVICE_ALL_EXPORT_PATH/bin
SERVICE_NAME=opentelemetry-collector-service

SCRIPTDIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
cd $SCRIPTDIR

echo "Running Path .. $SCRIPTDIR"

VENV=".venv"

# Python 3.11.7 with Window
if [ -d "$VENV/bin" ]; then
    source $VENV/bin/activate
else
    source $VENV/Scripts/activate
fi

export es_index_name=".kibana"

# See how we were called.
case "$1" in
  start)
        # Start daemon.
        echo "🦄 Starting $SERVICE_NAME";
        # nohup $ES_SERVICE_ALL_EXPORT_PATH$ES_SERVICE_ALL_EXPORT_PATH/otelcol --config=$ES_SERVICE_ALL_EXPORT_PATH/opentelemetry_collector_config.yaml &> /dev/null &
        $ES_SERVICE_ALL_EXPORT_PATH/otelcol --config=$ES_SERVICE_ALL_EXPORT_PATH/opentelemetry_collector_config.yaml
        ;;
  stop)
        # Stop daemons.
        echo "🦄 Shutting down $SERVICE_NAME";
        pid=`ps ax | grep -i '/otel' | grep -v grep | awk '{print $1}'`
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
        pid=`ps ax | grep -i '/otel' | grep -v grep | awk '{print $1}'`
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

