package main

import (
	"bytes"
	"encoding/json"
	"flag"
	"fmt"
	"io/ioutil"
	"net"
	"net/http"
	"os"
	"reflect"
	"strings"

	"github.com/joho/godotenv"
)

// https://medium.com/data-science/use-environment-variable-in-your-next-golang-project-39e17c3aaa66
// There are a few major disadvantages to this approach, but there can be many - Security Issue, Code Management.
// go get github.com/joho/godotenv

type Payload struct {
	db_url string
	sql    string
}

func PrettyString(str string) string {
	var prettyJSON bytes.Buffer
	if err := json.Indent(&prettyJSON, []byte(str), "", "    "); err != nil {
		return ""
	}
	return prettyJSON.String()
}

func Json_Parsing(body string) map[string]interface{} {
	var jsonRes map[string]interface{} // declaring a map for key names as string and values as interface
	resBytes := []byte(body)
	_ = json.Unmarshal(resBytes, &jsonRes) // Unmarshalling

	return jsonRes
}

func get_configuration() {
	// requestURL := fmt.Sprintf("http://localhost:%d", serverPort)
	requestURL := os.Getenv("CONFIGURATION")
	res, err := http.Get(requestURL)
	if err != nil {
		fmt.Printf("error making http request: %s\n", err)
		os.Exit(1)
	}

	defer res.Body.Close()

	fmt.Printf("client: got response!\n")
	body, _ := ioutil.ReadAll(res.Body)
	fmt.Println("response Body:", PrettyString(string(body)))
	fmt.Printf("client: status code: %d\n", res.StatusCode)

	var jsonRes map[string]interface{} // declaring a map for key names as string and values as interface
	jsonRes = Json_Parsing(string(body))

	fmt.Printf("Body Json : %s", jsonRes["alert_exclude_time"])
}

// Struct fields must start with upper case letter (exported) for the JSON package to see their value.
type API_Results struct {
	Running_time float32 `json:"running_time"`
	Request_dbid string  `json:"request_dbid"`
	Results      []struct {
		PROCESSNAME string `json:"processname"`
		STATUS      string `json:"status"`
		ADDTS       string `json:"addts"`
		COUNT       int    `json:"count"`
		DBID        string `json:"dbid"`
	} `json:"results"`
}

type ARG struct {
	ES_URL    string `json:"es_url"`
	KAFKA_URL string `json:"kafka_url"`
}

type SERVER_STATUS struct {
	ES    string `json:"es"`
	KAFKA string `json:"kafka"`
}

func db_api() {
	// """ POST """
	httpposturl := "http://" + os.Getenv("HOST") + ":8002/db/get_db_query"
	fmt.Println("HTTP JSON POST URL:", httpposturl)

	// u := Payload{
	// 	db_url: os.Getenv("DB_URL"),
	// 	sql:    os.Getenv("SQL"),
	// }

	// var jsonData = []byte(`{
	//       "db_url": "jdbc:oracle:thin:test/test@localhost:1234/DEVTEST",
	//       "sql": "SELECT * FROM TB"
	// }`)

	u := map[string]interface{}{
		"db_url": os.Getenv("DB_URL"),
		"sql":    os.Getenv("SQL"),
	}
	jsonData, _ := json.Marshal(u)
	fmt.Println("Payload: ", string(jsonData))
	request, error := http.NewRequest("POST", httpposturl, bytes.NewBuffer(jsonData))
	if error != nil {
		panic(error)
	}
	request.Header.Set("Content-Type", "application/json; charset=UTF-8")

	client := &http.Client{}
	response, error := client.Do(request)
	if error != nil {
		panic(error)
	}
	defer response.Body.Close()

	fmt.Println("response Status:", response.Status)
	fmt.Println("response Headers:", response.Header)
	body, _ := ioutil.ReadAll(response.Body)
	fmt.Println("response Body:", PrettyString(string(body)))

	var jsonRes map[string]interface{} // declaring a map for key names as string and values as interface
	jsonRes = Json_Parsing(string(body))

	// fmt.Printf("Body type : %s", reflect.TypeOf(body))
	fmt.Printf("Body Json : %s", fmt.Sprintf("%f", jsonRes["running_time"]))

	// using struct to parse the Json Format
	// Struct fields must start with upper case letter (exported) for the JSON package to see their value.
	response_map := API_Results{}
	if err := json.Unmarshal(body, &response_map); err != nil {
		// do error check
		fmt.Println(err)
	}
	fmt.Printf("Body Json : %s", response_map.Request_dbid)
	fmt.Print("\n")

	for i, rows := range response_map.Results {
		if i == 0 {
			fmt.Println("Body Json sequence : ", i+1)
			fmt.Println("Body Json records : ", rows.PROCESSNAME)
			fmt.Println("Body Json records-time : ", rows.ADDTS)
		}
	}
}

func get_port_open(host string) bool {
	// Connect to the server
	conn, err := net.Dial("tcp", host)
	if err != nil {
		fmt.Println("Error:", err)
		return false
	}
	defer conn.Close()

	return true
}

func get_port_list_open(host string) (bool, string) {
	result := strings.Split(strings.Trim(host, " "), ",")
	fmt.Printf("Result: %s, Type : %s\n", result, reflect.TypeOf(result))

	flag := true
	flag_value := 0
	server_status := "red"

	for i, rows := range result {
		rows = strings.Trim(rows, " ")
		fmt.Println("get_port_list_opensequence : ", i+1)
		// rows = strings.Replace(rows, " ", ",", -1)
		fmt.Println("get_port_list_open records : ", rows)

		// Connect to the server
		conn, err := net.Dial("tcp", rows)
		if err != nil {
			fmt.Println("Error:", err)
			flag = flag && false
			flag_value = flag_value + 0
			// fmt.Println("flag : ", flag)
			continue
		}
		defer conn.Close()
		flag = flag && true
		flag_value = flag_value + 1
		// fmt.Println("flag : ", flag)
	}

	if len(result) == flag_value {
		server_status = "Green"
	} else if flag_value < 1 {
		server_status = "Red"
	} else {
		server_status = "Yellow"
	}

	fmt.Println("** flag ** : ", flag)
	fmt.Println("** len(result) ** : ", len(result))
	fmt.Println("** flag_value ** : ", flag_value)
	// fmt.Println("** server_status ** : ", server_status)

	return flag, server_status
}

func initialize_args() map[string]interface{} {
	es_args := flag.String("es_url", "localhost:9201, localhost:9202", "string")
	kafka_args := flag.String("kafka_url", "localhost:9092", "string")

	flag.Parse()
	fmt.Println("es_args:", *es_args)
	fmt.Println("kafka_args:", *kafka_args)

	m := make(map[string]interface{})
	m["es_url"] = *es_args
	m["kafka_url"] = *kafka_args

	// m := make(map[string]interface{})
	// m["key1"] = make(map[string]interface{})
	// m["key1"].(map[string]interface{})["key2"] = "value"

	return m
}

func map_to_json(m map[string]interface{}) *SERVER_STATUS {
	json_server_data, _ := json.Marshal(m)
	server_status_map := SERVER_STATUS{}
	if err := json.Unmarshal(json_server_data, &server_status_map); err != nil {
		// do error check
		fmt.Println(err)
	}

	return &server_status_map

}

func main() {

	// go run ./go_db.go -es_url localhost:9201 -kafka_url localhost:9102

	// String
	m := initialize_args()
	jsonData, _ := json.Marshal(m)
	args_map := ARG{}
	if err := json.Unmarshal(jsonData, &args_map); err != nil {
		// do error check
		fmt.Println(err)
	}

	fmt.Println("globla(map) *es_args: ", m["es_url"])
	fmt.Println("args_map.ES_URL: ", args_map.ES_URL)
	fmt.Println("Arguments Json:", PrettyString(string(jsonData)))
	fmt.Print("\n\n")

	m_server_status := make(map[string]interface{})

	fmt.Println("** ES PORT OPEN ** ")
	// is_port_open := get_port_open(args_map.ES_URL)
	is_port_open, server_status := get_port_list_open(args_map.ES_URL)
	fmt.Println("** is_port_open: ** ", is_port_open)
	fmt.Println("** server_status ** : ", server_status)
	m_server_status["es"] = server_status
	fmt.Print("\n\n")

	fmt.Println("** KAFKA PORT OPEN ** ")
	// is_port_open := get_port_open(args_map.ES_URL)
	is_port_open, server_status = get_port_list_open(args_map.KAFKA_URL)
	fmt.Println("** is_port_open: ** ", is_port_open)
	fmt.Println("** server_status ** : ", server_status)
	m_server_status["kafka"] = server_status

	// json_server_data, _ := json.Marshal(m_server_status)
	// server_status_map := SERVER_STATUS{}
	// if err := json.Unmarshal(json_server_data, &server_status_map); err != nil {
	// 	// do error check
	// 	fmt.Println(err)
	// }
	server_status_map := map_to_json(m_server_status)

	fmt.Print("\n\n")

	// Load the .env file in the current directory
	// godotenv.Load()
	// or
	godotenv.Load("../.env")

	// fmt.Println("** HTTP GET **")
	// get_configuration()
	// fmt.Print("\n\n")

	fmt.Println("** HTTP POST ** ")
	db_api()

	fmt.Println("SERVER STATUS.ES_URL: ", server_status_map.ES)
	fmt.Println("SERVER STATUS.KAFKA_URL: ", server_status_map.KAFKA)
}
