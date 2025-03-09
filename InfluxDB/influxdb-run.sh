#!/bin/sh
INFLUXDB="/home/biadmin/monitoring/es_monitoring/influxdb/influxdb2-2.7.11/usr/bin"

$INFLUXDB/influxd --bolt-path=/apps/monitoring_datas/influx-data/influxd.bolt --engine-path=/apps/monitoring_datas/influx-data/engine
