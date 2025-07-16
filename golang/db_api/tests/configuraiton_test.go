package tests

import (
	"encoding/json"
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
	// print(m)

	expected_value := "localhost"
	/*
		val, ok := m["api_host"]
			// If the key exists
			if ok {
				// Do something
	}*/
	if val, ok := m["api_host"]; ok {
		//do something here
		assert.Equal(t, val, "localhost")
		assert.Equal(t, m["api_host"], expected_value)
	}

	expected_query := `{"alert_conf_api":"localhost","api_host":"localhost","db_url":"jdbc:oracle:thin:test/test@localhost:1234/testdb1,jdbc:oracle:test/test@localhost:1234/testdb2","env_name":"localhost","es_url":"localhost:9201, localhost:9202, localhost:9203","kafka_connect_url":"localhost:8083","kafka_url":"localhost:9092,localhost:9092,localhost:9092","kibana_url":"localhost:5601","spark_url":"localhost:8080","sql":"SELECT * FROM TB","zookeeper_url":"localhost:2181"}`
	jsonData, _ := json.Marshal(m)
	// fmt.Printf("jsonData : %s", jsonData)
	assert.Equal(t, string(jsonData), expected_query)

	expected_query = `
		{
			"alert_conf_api":"localhost",
			"api_host":"localhost",
			"db_url":"jdbc:oracle:thin:test/test@localhost:1234/testdb1,jdbc:oracle:test/test@localhost:1234/testdb2",
			"env_name":"localhost",
			"es_url":"localhost:9201, localhost:9202, localhost:9203",
			"kafka_connect_url":"localhost:8083",
			"kafka_url":"localhost:9092,localhost:9092,localhost:9092",
			"kibana_url":"localhost:5601",
			"spark_url":"localhost:8080",
			"sql":"SELECT * FROM TB",
			"zookeeper_url":"localhost:2181"
		}
	`
	/* one line */
	assert.Equal(t, utility.ReplaceStr(string(jsonData)), utility.ReplaceStr(utility.PrettyString(expected_query)))
	/* json_format */
	assert.Equal(t, utility.PrettyString(utility.ReplaceStr(string(jsonData))), utility.PrettyString(utility.ReplaceStr(expected_query)))
}
