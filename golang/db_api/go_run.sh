
#!/bin/bash
set -e

export ES_CONFIGURATION_HOST="localhost"
export CONFIGURATION="http://localhost:8004/config/get_mail_config"

go run ./go_db.go -es_url localhost:9201,localhost:9202,localhost:9203 -kibana_url localhost:5601 -kafka_url localhost:9092 -db_url jdbc:oracle:thin:test/test@localhost:1234/testdb1,jdbc:oracle:test/test@localhost:1234/testdb2 -sql "SELECT * FROM TB"