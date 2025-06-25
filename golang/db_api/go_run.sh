
#!/bin/bash
set -e

export ES_CONFIGURATION_HOST="localhost"
export CONFIGURATION="http://localhost:8004/config/get_mail_config"

# Arguments for the script
export API_HOST=localhost
export ES_URL=localhost:9200,localhost:9200,localhost:9200,localhost:9200
export KIBANA_URL=localhost:5601
export KAFKA_URL=localhost:9092,localhost:9092,localhost:9092
export SPARK_URL=localhost:8080
export DB_URL=jdbc:oracle:thin:test/test@localhost:1234/testdb1,jdbc:oracle:test/test@localhost:1234/testdb2

export SPARK_APP_CEHCK="StreamProcess_TEST1,StreamProcess_TEST2"
# export SPARK_APP_CEHCK="StreamProcessTEST"

go run ./go_db.go -api_host $API_HOST -es_url $ES_URL -kibana_url $KIBANA_URL -kafka_url $KAFKA_URL -spark_url $SPARK_URL -db_url $DB_URL -sql "SELECT * FROM TB"
