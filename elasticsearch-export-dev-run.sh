#!/bin/sh
# -- Elasticsearch Exporter GitHub : https://github.com/prometheus-community/elasticsearch_exporter
ELASTICSEARCH_EXPORT_PATH=/home/devuser/monitoring/es_exporter/elasticsearch_exporter-1.6.0.linux-386/
#PATH=$PATH:$ELASTICSEARCH_EXPORT_PATH/bin
SERVICE_NAME=elasticsearch-export-service
ES_HOST=localhost:9200
PORT=9201

# See how we were called.
case "$1" in
  start)
        # Start daemon.
        echo "Starting $SERVICE_NAME";
        #nohup $ELASTICSEARCH_EXPORT_PATH/elasticsearch_exporter --es.uri=http://$ES_HOST --es.all --es.indices --es.timeout 20s --es.snapshots --web.listen-address :$PORT &> /dev/null &
        $ELASTICSEARCH_EXPORT_PATH/elasticsearch_exporter --es.uri=http://$ES_HOST --es.all --es.indices --es.timeout 20s --es.snapshots --web.listen-address :$PORT
        ;;
  stop)
        # Stop daemons.
        echo "Shutting down $SERVICE_NAME";
        pid=`ps ax | grep -i '/elasticsearch_exporter --es.uri=http://'$ES_HOST | grep -v grep | awk '{print $1}'`
        if [ -n "$pid" ]
          then
          kill -9 $pid
         else
          echo "$SERVICE_NAME was not Running"
        fi
        ;;
  restart)
        #$0 stop
        #sleep 2
        #$0 start
        $0 stop
        $0 start
        sleep 5
        ;;
  status)
        pid=`ps ax | grep -i '/elasticsearch_exporter --es.uri=http://'$ES_HOST | grep -v grep | awk '{print $1}'`
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
