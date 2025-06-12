package main

import (
	"bytes"
	"encoding/json"
	"errors"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"reflect"
	"strings"

	"db.com/m/configuration"
	"db.com/m/repository"
	"db.com/m/utils"
	"github.com/common-nighthawk/go-figure"
	"github.com/joho/godotenv"
)

// https://transform.tools/json-to-go
// repository > model.go
var (
	IndexNameEmptyStringError = errors.New("index name cannot be empty string")
	IndexAlreadyExistsError   = errors.New("elasticsearch index already exists")
	ESInstanceError           = errors.New("elasticsearch goes down")
)

// https://medium.com/data-science/use-environment-variable-in-your-next-golang-project-39e17c3aaa66
// There are a few major disadvantages to this approach, but there can be many - Security Issue, Code Management.
// go get github.com/joho/godotenv
// ascill art
// go get github.com/common-nighthawk/go-figure

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
	fmt.Println("response Body:", utils.PrettyString(string(body)))
	fmt.Printf("client: status code: %d\n", res.StatusCode)

	var jsonRes map[string]interface{} // declaring a map for key names as string and values as interface
	jsonRes = utils.Json_Parsing(string(body))

	fmt.Printf("Body Json : %s", jsonRes["alert_exclude_time"])
}

func db_api(db_url string, sql string, db_type string) {
	// """ POST """
	httpposturl := "http://" + os.Getenv("ES_CONFIGURATION_HOST") + ":8002/db/get_db_query"
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
		// "db_url": os.Getenv("DB_URL"),
		// "sql":    os.Getenv("SQL"),
		"db_url": db_url,
		"sql":    sql,
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
	fmt.Println("response Body:", utils.PrettyString(string(body)))

	var jsonRes map[string]interface{} // declaring a map for key names as string and values as interface
	jsonRes = utils.Json_Parsing(string(body))

	// fmt.Printf("Body type : %s", reflect.TypeOf(body))
	fmt.Printf("Body Json : %s", fmt.Sprintf("%f", jsonRes["running_time"]))

	// using struct to parse the Json Format
	// Struct fields must start with upper case letter (exported) for the JSON package to see their value.
	response_map := repository.API_Results{}
	if err := json.Unmarshal(body, &response_map); err != nil {
		// do error check
		fmt.Println(err)
	}
	fmt.Printf("Body Json : %s\n", response_map.Request_dbid)
	fmt.Printf("len(response_map.Results) : %d", len(response_map.Results))
	fmt.Print("\n")

	// return when the number of records is zero
	if len(response_map.Results) < 1 {
		DATA_PIPELINE_ACITVE = DATA_PIPELINE_ACITVE && false
		return
	}

	for i, rows := range response_map.Results {
		if i == 0 {
			fmt.Println("Body Json sequence : ", i+1)
			fmt.Println("Body Json records : ", rows.PROCESSNAME)

			if db_type == "WMx" {
				DATA_PIPELINE_ACITVE_WMX = utils.Get_time_difference_is_ative(rows.ADDTS)
				if strings.ToLower(DATA_PIPELINE_ACITVE_WMX) == "green" {
					DATA_PIPELINE_ACITVE = DATA_PIPELINE_ACITVE && true
				} else {
					DATA_PIPELINE_ACITVE = DATA_PIPELINE_ACITVE && false
				}

			} else {
				DATA_PIPELINE_ACITVE_OMX = utils.Get_time_difference_is_ative(rows.ADDTS)
				if strings.ToLower(DATA_PIPELINE_ACITVE_OMX) == "green" {
					DATA_PIPELINE_ACITVE = DATA_PIPELINE_ACITVE && true
				} else {
					DATA_PIPELINE_ACITVE = DATA_PIPELINE_ACITVE && false
				}

			}
			// fmt.Println("DATA PIPELINE : ", DATA_PIPELINE_ACITVE)
		}
	}
}

func active_update_func(status string) {
	SERVER_ACTIVE_TOTAL_CNT += 1
	if strings.ToLower(status) == "green" {
		// DATA_PIPELINE_ACITVE = DATA_PIPELINE_ACITVE && true
		SERVER_ACTIVE_CNT += 1
	} else if strings.ToLower(status) == "yellow" {
		// DATA_PIPELINE_ACITVE = DATA_PIPELINE_ACITVE && true
		SERVER_ACTIVE_CNT -= 1
	} else {
		// DATA_PIPELINE_ACITVE = DATA_PIPELINE_ACITVE && false
		SERVER_ACTIVE_CNT += 0
	}
	// fmt.Println(status, server_active_chk, DATA_PIPELINE_ACITVE)
}

func set_service_port(service_name string, url string, m map[string]interface{}) {
	fmt.Printf("** %s PORT OPEN ** ", service_name)
	// is_port_open := utils.Get_port_open(args_map.ES_URL)
	is_port_open, server_status := utils.Get_port_list_open(url)
	fmt.Println("** is_port_open: ** ", is_port_open)
	fmt.Println("** server_status ** : ", server_status)
	m[service_name] = server_status
	// update server_active to global variable
	active_update_func(server_status)
	fmt.Print("\n\n")
}

var SERVER_ACTIVE_TOTAL_CNT, SERVER_ACTIVE_CNT = 0, 0
var SERVER_ACITVE, DATA_PIPELINE_ACITVE = true, true
var SERVER_ACITVE_TXT, DATA_PIPELINE_ACITVE_TXT = "Red", "Red"
var DATA_PIPELINE_ACITVE_WMX, DATA_PIPELINE_ACITVE_OMX = "Red", "Red"

func Get_service_health(args_map repository.ARG, m_server_status map[string]interface{}) {
	// fmt.Println("** HTTP GET **")
	// get_configuration()
	// fmt.Print("\n\n")

	fmt.Println("** HTTP POST ** ")
	fmt.Println("args_map.DB_URL : ", args_map.DB_URL)
	result := strings.Split(strings.Trim(args_map.DB_URL, " "), ",")
	fmt.Printf("Result: %s, Type : %s\n", result, reflect.TypeOf(result))
	db_type := ""
	// data_pipeline_flag := true
	for i, rows := range result {
		fmt.Println("db_api call : ", i+1)
		fmt.Println("db_api call rows: ", rows)

		if i == 0 {
			db_type = "WMx"
		} else {
			db_type = "OMx"
		}
		db_api(rows, args_map.SQL, db_type)
	}

	// verify the Server Active
	if SERVER_ACTIVE_CNT == SERVER_ACTIVE_TOTAL_CNT {
		SERVER_ACITVE_TXT = "Green"
	} else if SERVER_ACTIVE_CNT == 0 {
		SERVER_ACITVE_TXT = "Red"
	} else {
		SERVER_ACITVE_TXT = "Yellow"
	}

	if DATA_PIPELINE_ACITVE {
		DATA_PIPELINE_ACITVE_TXT = "Green"
	} else {
		DATA_PIPELINE_ACITVE_TXT = "Red"
	}
	m_server_status["SERVER_ACTIVE"] = SERVER_ACITVE_TXT
	m_server_status["DATA_PIPELINE"] = DATA_PIPELINE_ACITVE_TXT

	// update all status to server_status_mm_server_statusap
	server_status_map := utils.Map_to_json(m_server_status)

	fmt.Print("\n\n")
	fmt.Print("** STATUS **\n")
	json_server_status, _ := json.Marshal(m_server_status)
	fmt.Println("SERVER_STATUS Json:", utils.PrettyString(string(json_server_status)))
	fmt.Printf("DATA_PIPELINE_ACITVE_WMX : %s, DATA_PIPELINE_ACITVE_OMX : %s\n", DATA_PIPELINE_ACITVE_WMX, DATA_PIPELINE_ACITVE_OMX)
	fmt.Println("SERVER STATUS.ES_URL: ", server_status_map.ES)
	fmt.Println("SERVER STATUS.KAFKA_URL: ", server_status_map.KAFKA)
	fmt.Println("* SERVER Active: ", server_status_map.SERVER_ACTIVE, ", * DATA PIPELINE Active: ", server_status_map.DATA_PIPELINE)
}

func work(args_map repository.ARG, m_server_status map[string]interface{}) {
	/*
		for {
			fmt.Printf("\n\nwork runnning..\n")
			go Get_service_health(args_map, m_server_status)
			time.Sleep(5 * time.Second)
		}
	*/

	/*
		difference go Get_service_health(args_map, m_server_status) and Get_service_health(args_map, m_server_status)
	*/
	Get_service_health(args_map, m_server_status)

}

func main() {

	// go run ./go_db.go -es_url localhost:9201 -kafka_url localhost:9102
	figure.NewFigure("Service Metrics Exporter", "thick", true).Print()
	// os.Exit(0)

	// Load the .env file in the current directory
	// godotenv.Load()
	// or
	godotenv.Load("../.env")

	// String
	m := configuration.Get_initialize_args()
	jsonData, _ := json.Marshal(m)
	args_map := repository.ARG{}
	if err := json.Unmarshal(jsonData, &args_map); err != nil {
		// do error check
		fmt.Println(err)
	}

	fmt.Println("globla(map) *es_args: ", m["es_url"])
	fmt.Println("args_map.ES_URL: ", args_map.ES_URL)
	fmt.Println("Arguments Json:", utils.PrettyString(string(jsonData)))
	fmt.Print("\n\n")

	m_server_status := make(map[string]interface{})

	set_service_port("ES", args_map.ES_URL, m_server_status)
	set_service_port("KIBANA", args_map.KIBANA_URL, m_server_status)
	set_service_port("KAFKA", args_map.KAFKA_URL, m_server_status)

	// main_func
	work(args_map, m_server_status)

}
