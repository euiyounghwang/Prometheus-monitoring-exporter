package tests

import (
	"encoding/json"
	"fmt"
	"testing"

	"db.com/m/configuration"
	utility "db.com/m/utils"
	"github.com/stretchr/testify/assert"
)

func Test_Initial_Configuration(t *testing.T) {
	// assert := assert.New(t)

	// expected_round_float := 90.567
	// assert.Equal(t, utility.RoundFloat(-12.3456789, 10), expected_round_float)

	m := configuration.Get_initialize_args()
	print(m)
	expected_value := "localhost"
	assert.Equal(t, m["api_host"], expected_value)

	expected_query := `{"api_host":"localhost","db_url":"jdbc:oracle:thin:test/test@localhost:1234/testdb1,jdbc:oracle:test/test@localhost:1234/testdb2","es_url":"localhost:9201, localhost:9202","kafka_connect_url":"localhost:8083","kafka_url":"localhost:9092,localhost:9092,localhost:9092","kibana_url":"localhost:5601","spark_url":"localhost:8080","sql":"SELECT * FROM TB","zookeeper_url":"localhost:2181"}`
	jsonData, _ := json.Marshal(m)
	fmt.Printf("jsonData : %s", jsonData)
	assert.Equal(t, string(jsonData), expected_query)

	expected_query = `
		{
			"api_host":"localhost",
			"db_url":"jdbc:oracle:thin:test/test@localhost:1234/testdb1,jdbc:oracle:test/test@localhost:1234/testdb2",
			"es_url":"localhost:9201, localhost:9202",
			"kafka_connect_url":"localhost:8083",
			"kafka_url":"localhost:9092,localhost:9092,localhost:9092",
			"kibana_url":"localhost:5601",
			"spark_url":"localhost:8080",
			"sql":"SELECT * FROM TB",
			"zookeeper_url":"localhost:2181"
		}
	`
	assert.Equal(t, utility.ReplaceStr(string(jsonData)), utility.ReplaceStr(utility.PrettyString(expected_query)))
}
