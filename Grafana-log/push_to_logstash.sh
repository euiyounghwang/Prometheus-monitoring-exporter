#!/bin/sh
LOGGING_SERVICE_ALL_EXPORT_PATH=/home/devuser/monitoring/log_to_logstash
PATH=$PATH:$LOGGING_SERVICE_ALL_EXPORT_PATH/bin
SERVICE_NAME=python-logging-to-logstash-sparklogs

export LOGSTASH_HOST="localhost"
export ENV="Dev"

path="/test/logs"
hostname="Data_Transfer_Node_#1"
logging_file_list="test.log,test1.log"


# ----
# Description
# ----
# To save spark text log, we need to pass it to filebeat-logstash-es cluster.
# However, if we pass all lines in the spark log or archive log files to logstash using filebeat, a lot of traffic will be generated.
# So, instead of filebeat, I implemented a python script as agent to read only error logs and pass them to logstash.
# -- ./push_to_logstash.sh start (This script will be run as agent to send text logs to logstash using TCP socket)
# Then, The Grafana dashboard will read the ES log index and show ERROR logs in near real time.
# ----

# python ./push_to_loki_script.py --path /home/devuser --filename test1.log --hostname Data_Transfer_Node_#1

# See how we were called.
case "$1" in
  start)
        # Start daemon.
        echo "Starting $SERVICE_NAME";
        #nohup python $LOGGING_SERVICE_ALL_EXPORT_PATH/push_to_loki_script.py --path $path --filename $logging_file_list --hostname $hostname --logs ERROR &> /dev/null &
        python $LOGGING_SERVICE_ALL_EXPORT_PATH/push_to_logstash_script.py --path $path --filename $logging_file_list --hostname $hostname --logs ERROR
        ;;
  stop)
        # Stop daemons.
        echo "Shutting down $SERVICE_NAME";
        pid=`ps ax | grep -i '/push_to_logstash_script.py' | grep -v grep | awk '{print $1}'`
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
        pid=`ps ax | grep -i '/push_to_logstash_script.py' | grep -v grep | awk '{print $1}'`
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
