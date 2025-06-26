package configuration

import "flag"

/*
-------
same worker for Python like the following
parser = argparse.ArgumentParser(description="Index into Elasticsearch using this script")
parser.add_argument('-e', '--es', dest='es', default="http://localhost:9250", help='host target')
args = parser.parse_args()
go run ./tools/bulk_index_script.go --es_host=http://localhost:9209 --index_name=test_ominisearch_v1_go
-------
*/
var (
	api_host          string
	es_url            string
	kibana_url        string
	kafka_url         string
	zookeeper_url     string
	kafka_connect_url string
	spark_url         string
	db_url            string
	sql               string
)

func Get_initialize_args() map[string]interface{} {
	/*
		es_args := flag.String("es_url", "localhost:9201, localhost:9202", "string")
		kafka_args := flag.String("kafka_url", "localhost:9092", "string")
		db_url_args := flag.String("db_url", "jdbc:oracle:thin:test/test@localhost:1234/testdb1,jdbc:oracle:test/test@localhost:1234/testdb2", "string")
	*/

	flag.StringVar(&api_host, "api_host", "localhost", "string")
	flag.StringVar(&es_url, "es_url", "localhost:9201, localhost:9202", "string")
	flag.StringVar(&kibana_url, "kibana_url", "localhost:5601", "string")
	flag.StringVar(&kafka_url, "kafka_url", "localhost:9092", "string")
	flag.StringVar(&zookeeper_url, "zookeeper_url", "localhost:2181", "string")
	flag.StringVar(&kafka_connect_url, "kafka_connect_url", "localhost:8083", "string")
	flag.StringVar(&spark_url, "spark_url", "localhost:8080", "string")
	flag.StringVar(&db_url, "db_url", "jdbc:oracle:thin:test/test@localhost:1234/testdb1,jdbc:oracle:test/test@localhost:1234/testdb2", "string")
	flag.StringVar(&sql, "sql", "SELECT * FROM TB", "string")

	flag.Parse()

	/*
		fmt.Println("es_url:", es_url)
		fmt.Println("kafka_url:", kafka_url)
		fmt.Println("db_url:", db_url)
		// fmt.Println("db_url_args:", *db_url_args)
	*/

	m := make(map[string]interface{})
	m["api_host"] = api_host
	m["es_url"] = es_url
	m["kibana_url"] = kibana_url
	m["kafka_url"] = kafka_url
	m["zookeeper_url"] = zookeeper_url
	m["kafka_connect_url"] = kafka_connect_url
	m["spark_url"] = spark_url
	m["db_url"] = db_url
	m["sql"] = sql

	// m := make(map[string]interface{})
	// m["key1"] = make(map[string]interface{})
	// m["key1"].(map[string]interface{})["key2"] = "value"

	return m
}
