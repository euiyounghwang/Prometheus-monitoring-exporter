
#!/bin/bash
set -e

# GET configuration from the particular env (GET http://localhost:8004/config/get_mail_config_from_env)
SET_ENV_NAME=localhost
ALERT_CONFIGURATION_API="http://localhost:8004/config/get_mail_config_from_env?host=test"

# Arguments for the script
export API_HOST=localhost
export ES_URL=localhost:9200,localhost:9200,localhost:9200,localhost:9200
export KIBANA_URL=localhost:5601
export KAFKA_URL=localhost:9092,localhost:9092,localhost:9092
export ZOOKEEPER_URL=localhost:2181,localhost:2181,localhost:2181
export KAFKA_CONNECT_URL=localhost:8083,localhost:8083,localhost:8083
export SPARK_URL=localhost:8080
export DB_URL=jdbc:oracle:thin:test/test@localhost:1234/testdb1,jdbc:oracle:test/test@localhost:1234/testdb2

export SPARK_APP_CEHCK="StreamProcess_TEST1,StreamProcess_TEST2"
# export SPARK_APP_CEHCK="StreamProcessTEST"

go run ./go_db.go -env_name $SET_ENV_NAME -api_host $API_HOST -alert_conf_api $ALERT_CONFIGURATION_API -es_url $ES_URL -kibana_url $KIBANA_URL -kafka_url $KAFKA_URL -zookeeper_url $ZOOKEEPER_URL -kafka_connect_url $KAFKA_CONNECT_URL -spark_url $SPARK_URL -db_url $DB_URL -sql "SELECT * FROM TB"
