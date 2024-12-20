#!/bin/sh
KAFKA_METRICS_EXPORT_PATH=/home/devuser/monitoring/
JAVA_HOME_PATH=/home/devuser/monitoring/openlogic-openjdk-11.0.23+9-linux-x64
SERVICE_NAME=es-jenkins-service

SCRIPTDIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

# See how we were called.
case "$1" in
  start)
        # Start daemon.
        echo "Starting $SERVICE_NAME";
        #nohup $JAVA_HOME_PATH/bin/java -jar $KAFKA_METRICS_EXPORT_PATH/jenkins.war &> /dev/null &
        $JAVA_HOME_PATH/bin/java -jar $KAFKA_METRICS_EXPORT_PATH/jenkins.war
        ;;
  stop)
        # Stop daemons.
        echo "Shutting down $SERVICE_NAME";
        pid=`ps ax | grep -i '/jenkins.war' | grep -v grep | awk '{print $1}'`
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
        pid=`ps ax | grep -i '/jenkins.war' | grep -v grep | awk '{print $1}'`
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

