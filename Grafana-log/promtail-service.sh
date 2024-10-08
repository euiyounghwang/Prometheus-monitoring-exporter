#!/bin/sh

LOKI_PATH=/home/devuser/monitoring/grafana-loki
SERVICE_NAME=grafana-promtail-service

#-- 
# sudo vi /etc/rc.d/rc.local
# sudo chmod 755 /etc/rc.local && sudo systemctl enable rc-local

# sudo systemctl status rc-local.service
# sudo service rc-local stop
# sudo service rc-local status

# See how we were called.
case "$1" in
  start)
        # Start daemon.
        echo "Starting $SERVICE_NAME";
        # nohup $LOKI_PATH/promtail-linux-amd64 --config.file=$LOKI_PATH/promtail-config.yml &> /dev/null &
        $LOKI_PATH/promtail-linux-amd64 --config.file=$LOKI_PATH/promtail-config.yml
        ;;
  stop)
        # Stop daemons.
        echo "Shutting down $SERVICE_NAME";
        pid=`ps ax | grep -i '/promtail-linux-amd64' | grep -v grep | awk '{print $1}'`
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
        pid=`ps ax | grep -i '/promtail-linux-amd64' | grep -v grep | awk '{print $1}'`
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