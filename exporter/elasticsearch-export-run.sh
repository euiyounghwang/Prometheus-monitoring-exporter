#!/bin/sh
ELASTICSEARCH_EXPORT_PATH=/home/devuser/monitoring/elasticsearch_exporter-1.6.0.linux-386/
PATH=$PATH:$ELASTICSEARCH_EXPORT_PATH/bin
SERVICE_NAME=elasticsearch-export-service

# See how we were called.
case "$1" in
  start)
        # Start daemon.
        echo "Starting $SERVICE_NAME";
        # for Dev ES Cluster
        # nohup $ELASTICSEARCH_EXPORT_PATH/elasticsearch_exporter --es.uri=http://localhost:9200 --es.all --es.indices --es.timeout 20s --es.snapshots &
        nohup $ELASTICSEARCH_EXPORT_PATH/elasticsearch_exporter --es.uri=http://localhost:9200 --es.all --es.indices --es.timeout 20s --es.snapshots --web.listen-address :9101 &> /dev/null &
        # nohup $ELASTICSEARCH_EXPORT_PATH/elasticsearch_exporter --es.uri=https://test:1@localhost:9200 --es.all --es.indices --es.timeout 20s --es.snapshots --es.ssl-skip-verify --web.listen-address :9101 &> /dev/null &
        ;;
  stop)
        # Stop daemons.
        echo "Shutting down $SERVICE_NAME";
        pid=`ps ax | grep -i '/elasticsearch_exporter --es.uri=http://localhost:9200' | grep -v grep | awk '{print $1}'`
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
        pid=`ps ax | grep -i '/elasticsearch_exporter --es.uri=http://localhost:9200' | grep -v grep | awk '{print $1}'`
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

