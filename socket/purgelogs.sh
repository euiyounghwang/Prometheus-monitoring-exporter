#!/bin/sh
# sudo find /apps/var/spark/logs/*log* -mtime +0 -exec rm {} \;
sudo find /apps/monitoring_script/airflow/logs/scheduler/ -type d -mtime +2 -exec rm -rf {} \;