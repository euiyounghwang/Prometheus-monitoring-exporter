
#!/bin/bash
set -e

SERVICE_NAME=elasticsearch

PID_DIR="/apps/elasticsearch/"
prog="elasticsearch"
pidfile="$PID_DIR/${prog}.pid"

pid=`ps ax | grep -i '/elasticsearch-8.17.0' | grep -v grep | awk '{print $1}'`
if [ -n "$pid" ]; then
    echo "$SERVICE_NAME is Running as PID: $pid"
else
    #sh -c 'sudo su - elasticsearch -c "/apps/elasticsearch/latest/bin/elasticsearch -p $pidfile -d"'
    #sh -c 'sudo su - elasticsearch -c "/apps/elasticsearch/latest/bin/elasticsearch -p /apps/elasticsearch/elasticsearch.pid -d"'
    sh -c 'sudo service elasticsearch start'
fi
