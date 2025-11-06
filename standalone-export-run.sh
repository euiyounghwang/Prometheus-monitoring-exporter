#!/bin/bash
set -e

JAVA_HOME='/home/biadmin/jdk1.8.0_151'
#PATH=$PATH:$JAVA_HOME
export PATH=$JAVA_HOME/bin:$PATH
export JAVA_HOME

# Activate virtualenv && run serivce

SCRIPTDIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
cd $SCRIPTDIR

VENV=".venv"

# Python 3.11.7 with Window
if [ -d "$VENV/bin" ]; then
    source $VENV/bin/activate
else
    source $VENV/Scripts/activate
fi

VENV=".venv"

# Python 3.11.7 with Window
# if [ -d "$ES_REDIS_CONFIGURATION_WRITE_PATH/$VENV/bin" ]; then
#     source $ES_REDIS_CONFIGURATION_WRITE_PATH/$VENV/bin/activate
# else
#     source $ES_REDIS_CONFIGURATION_WRITE_PATH/$VENV/Scripts/activate
# fi


# -- Export Variable
export GRAFANA_DASHBOARD_URL="http://localhost:3000/d/adm08055cf3lsa/es-team-dashboard?orgId=1'&'from=now-5m'&'to=now'&'refresh=5s"
export SMTP_HOST="localhost"
export SMTP_PORT=212
export MAIL_SENDER="mymail"
export ES_CONFIGURATION_URL="http://localhost:8004/docs"
export ES_CONFIGURATION_HOST="localhost"
export ES_EXPORTER_HOST="localhost"
export ES_MONITORING_APPS_EXPORTER_RUN_HOST="localhost:1001"
export ES_MONITORING_APPS_EXPORTER_URL_HOST="localhost:9001"
export SPARK_APP_CEHCK="StreamProcessEXP"
export BASIC_AUTH_SH="basic_auth_encoded"
export PROMETHEUS_USERNAME="test"
export PROMETHEUS_PASSWORD="test"
export CERTIFICATE_TEST_HOST="localhost"


export ZOOKEEPER_URLS="localhost:2181,localhost:2181,localhost:2181"
export BROKER_LIST="localhost:9092,localhost:9092,localhost:9092"
export GET_KAFKA_ISR_LIST="$SCRIPTDIR/kafka_2.11-0.11.0.0/bin/kafka-topics.sh --describe --zookeeper $ZOOKEEPER_URLS --topic ELASTIC_PIPELINE_QUEUE"
export KAFKA_JOB_INTERFACE_API="localhost:8008"
export ES_NODES_DISK_AVAILABLE_THRESHOLD="10"
export ES_HOST_URL_PREFIX="https"
# -- 

#-- ARG
DATA_TRANSFER_NODE_1=localhost_dt_1
DATA_TRANSFER_NODE_2=localhost_dt_2
DATA_TRANSFER_NODE_3=localhost_dt_3
ES_NODE_1=localhost_es_1
ES_NODE_2=localhost_es_2
ES_NODE_2=localhost_es_3
LOGSTASH_HOST=localhost
KIBANA_URL=localhost:5601
LOGSTASH_URL=$LOGSTASH_HOST:5043,$LOGSTASH_HOST:5044,$LOGSTASH_HOST:5045,$LOGSTASH_HOST:5046,$LOGSTASH_HOST:5047,$LOGSTASH_HOST:5048
DOMAIN_NICK_NAME=localhost.com
RUN_PORT=9002
#--

# -- standalone type
# local
# server : --first node of kafka_url is a master node to get the number of jobs using http://localhost:8080/json

# -- direct access to db
#python ./standalone-es-service-export.py --interface db --url jdbc:oracle:thin:id/passwd@address:port/test_db --db_run false --kafka_url localhost:9092,localhost:9092,localhost:9092 --kafka_connect_url localhost:8083,localhost:8083,localhost:8083 --zookeeper_url  localhost:2181,localhost:2181,localhost:2181 --es_url localhost:9200,localhost:9201,localhost:9201,localhost:9200 --kibana_url localhost:5601 --sql "SELECT processname from test"

# -- collect records through DB interface Restapi
# -- Only Dev has "--redis_url localhost:6379 --configuration_job_url localhost:9116 ----es_configuration_api_url localhost:8004"
# python ./standalone-es-service-export.py --env_name localhost --interface http --db_http_host localhost:8002 --url jdbc:oracle:thin:id/passwd@address:port/test_db,jdbc:oracle:thin:id/passwd@address:port/test_db --db_run false --kafka_url localhost:9092,localhost:9092,localhost:9092 --kafka_connect_url localhost:8083,localhost:8083,localhost:8083 --zookeeper_url  localhost:2181,localhost:2181,localhost:2181 --es_url localhost:9200,localhost:9201,localhost:9201,localhost:9200 --kibana_url localhost:5601 --redis_url localhost:6379 --configuration_job_url localhost:9116 --es_configuration_api_url localhost:8004 --log_db_url localhost:9092 --alert_monitoring_url localhost:8501 --loki_url localhost:3100 --loki_api_url localhost:8010 --loki_custom_promtail_agent_url localhost1:2000,localhost2:2000,localhost3:2000 --log_aggregation_agent_url localhost1:2000,localhost2:2000,localhost3:2000 --sql "SELECT processname from test" --kafka_sql "SELECT processname from test"
python ./standalone-es-service-export.py --env_name localhost --port $RUN_PORT --domain_name_as_nick_name $DOMAIN_NICK_NAME --spark_cluster_https true --interface http --db_http_host localhost:8002 --url jdbc:oracle:thin:id/passwd@address:port/test_db,jdbc:oracle:thin:id/passwd@address:port/test_db --db_run false --kafka_url $DATA_TRANSFER_NODE_1:9092,$DATA_TRANSFER_NODE_2:9092,$DATA_TRANSFER_NODE_3:9092 --kafka_connect_url $DATA_TRANSFER_NODE_1:8083,$DATA_TRANSFER_NODE_2:8083,$DATA_TRANSFER_NODE_3:8083 --zookeeper_url  $DATA_TRANSFER_NODE_1:2181,$DATA_TRANSFER_NODE_2:2181,$DATA_TRANSFER_NODE_3:2181 --es_url $ES_NODE_1:9200,$ES_NODE_2:9201,$ES_NODE_3:9201 --kibana_url $KIBANA_URL --logstash_url $LOGSTASH_URL --redis_url localhost:6379 --configuration_job_url localhost:9116 --es_configuration_api_url localhost:8004 --log_db_url localhost:9092 --alert_monitoring_url localhost:8501 --log_aggregation_agent_url localhost1:2000,localhost2:2000,localhost3:2000 --sql "SELECT processname from test" --sql_backlog "SELECT backlog from test" --backlog true --spark_cluster_https true --xMatters true --certs_alert true --tools_alert_url localhost:9999
