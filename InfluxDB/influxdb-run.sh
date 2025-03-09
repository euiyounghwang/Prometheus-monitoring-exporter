#!/bin/sh
INFLUXDB="/home/devuser/monitoring/es_monitoring/influxdb/influxdb2-2.7.11/usr/bin"
SERVICE_NAME=influxdb-service

# A self-signed certificate can be generated with openssl. For example, the following command will create a certificate valid for 365 days with both the key and certificate data written to the same file:
# openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout mykey.key -out mycert.pem

# See how we were called.
case "$1" in
  start)
        # Start daemon.
        echo "Starting $SERVICE_NAME";
        # nohup $INFLUXDB/influxd --bolt-path=/apps/monitoring_datas/influx-data/influxd.bolt --engine-path=/apps/monitoring_datas/influx-data/engine --tls-cert=$INFLUXDB/certs/mycert.pem --tls-key=$INFLUXDB/certs/mykey.key &> /dev/null &
        $INFLUXDB/influxd --bolt-path=/apps/monitoring_datas/influx-data/influxd.bolt --engine-path=/apps/monitoring_datas/influx-data/engine --tls-cert=$INFLUXDB/certs/mycert.pem --tls-key=$INFLUXDB/certs/mykey.key
        ;;
  stop)
        # Stop daemons.
        echo "Shutting down $SERVICE_NAME";
        pid=`ps ax | grep -i '/influxdb2-2.7.11' | grep -v grep | awk '{print $1}'`
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
        pid=`ps ax | grep -i '/influxdb2-2.7.11' | grep -v grep | awk '{print $1}'`
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

