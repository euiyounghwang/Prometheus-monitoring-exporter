package main

import (
	"encoding/json"
	"errors"
	"fmt"
	"log"
	"os"
	"reflect"
	"strings"
	"time"

	"db.com/m/api"
	"db.com/m/configuration"
	"db.com/m/logging"
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
	// log.Println(status, server_active_chk, DATA_PIPELINE_ACITVE)
}

func set_service_port(service_name string, url string, m map[string]interface{}) {
	log.Printf("** %s PORT OPEN ** ", service_name)
	// is_port_open := utils.Get_port_open(args_map.ES_URL)
	is_port_open, server_status := utils.Get_port_list_open(url)
	log.Println("** is_port_open: ** ", is_port_open)
	log.Println("** server_status ** : ", server_status)
	m[service_name] = server_status
	// update server_active to global variable
	active_update_func(server_status)
	fmt.Print("\n\n")
}

// var SERVER_ACTIVE_TOTAL_CNT, SERVER_ACTIVE_CNT = 0, 0
// var SERVER_ACITVE, DATA_PIPELINE_ACITVE = true, true
// var SERVER_ACITVE_TXT, DATA_PIPELINE_ACITVE_TXT = "Red", "Red"
// var DATA_PIPELINE_ACITVE_WMX, DATA_PIPELINE_ACITVE_OMX = "Red", "Red"

func get_service_data_pipeline_health(args_map repository.ARG, m_server_status map[string]interface{}) {
	// log.Println("** HTTP GET **")
	// get_configuration()
	// log.Print("\n\n")

	log.Println("** HTTP POST ** ")
	log.Println("args_map.DB_URL : ", args_map.DB_URL)
	result := strings.Split(strings.Trim(args_map.DB_URL, " "), ",")
	log.Printf("Result: %s, Type : %s\n", result, reflect.TypeOf(result))
	db_type := ""
	// data_pipeline_flag := true
	for i, db_url := range result {
		log.Println("db_api call : ", i+1)
		log.Println("db_api call rows: ", db_url)

		if i == 0 {
			db_type = "WMx"
		} else {
			db_type = "OMx"
		}

		// db_api(rows, args_map.SQL, db_type)

		api_endpoint_host := "http://" + args_map.API_HOST + ":8002/db/get_db_query"
		json_post := map[string]interface{}{
			// "db_url": os.Getenv("DB_URL"),
			// "sql":    os.Getenv("SQL"),
			"db_url": db_url,
			"sql":    args_map.SQL,
		}
		body := api.API_Post(api_endpoint_host, json_post, db_type)

		if body != nil {

			// using struct to parse the Json Format
			// Struct fields must start with upper case letter (exported) for the JSON package to see their value.
			response_map := repository.API_Results{}
			if err := json.Unmarshal(body, &response_map); err != nil {
				// do error check
				log.Println(err)
			}
			log.Printf("Body Json : %s\n", response_map.Request_dbid)
			log.Printf("len(response_map.Results) : %d", len(response_map.Results))
			log.Print("\n")

			// return when the number of records is zero
			if len(response_map.Results) < 1 {
				DATA_PIPELINE_ACITVE = DATA_PIPELINE_ACITVE && false
				return
			}

			for i, rows := range response_map.Results {
				if i == 0 {
					log.Println("Body Json sequence : ", i+1)
					log.Println("Body Json records : ", rows.PROCESSNAME)

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
					// log.Println("DATA PIPELINE : ", DATA_PIPELINE_ACITVE)
				}
			}
		} else {
			DATA_PIPELINE_ACITVE = DATA_PIPELINE_ACITVE && false
		}
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
	log.Print("** STATUS **\n")
	json_server_status, _ := json.Marshal(m_server_status)
	logging.Info(fmt.Sprintf("SERVER_STATUS Json: %s", utils.PrettyString(string(json_server_status))))
	logging.Info(fmt.Sprintf("DATA_PIPELINE_ACITVE_WMX : %s, DATA_PIPELINE_ACITVE_OMX : %s\n", DATA_PIPELINE_ACITVE_WMX, DATA_PIPELINE_ACITVE_OMX))
	logging.Info(fmt.Sprintf("SERVER STATUS.ES_URL: %s", server_status_map.ES))
	logging.Info(fmt.Sprintf("SERVER STATUS.KAFKA_URL: %s", server_status_map.KAFKA))
	logging.Info(fmt.Sprintf("* SERVER Active: %s, *DATA PIPELINE Active: %s", server_status_map.SERVER_ACTIVE, server_status_map.DATA_PIPELINE))
	fmt.Print("\n\n")
}

func set_init() {
	// String
	m := configuration.Get_initialize_args()

	jsonData, _ := json.Marshal(m)
	// args_map := repository.ARG{}
	if err := json.Unmarshal(jsonData, &args_map); err != nil {
		// do error check
		log.Println(err)
	}

	log.Println("globla(map) *es_args: ", m["es_url"])
	log.Println("args_map.ES_URL: ", args_map.ES_URL)
	log.Println("Arguments Json:", utils.PrettyString(string(jsonData)))
	fmt.Print("\n\n")
}

/* global variable */
var (
	args_map        = repository.ARG{}
	m_server_status = make(map[string]interface{})

	SERVER_ACTIVE_TOTAL_CNT, SERVER_ACTIVE_CNT         = 0, 0
	SERVER_ACITVE, DATA_PIPELINE_ACITVE                = true, true
	SERVER_ACITVE_TXT, DATA_PIPELINE_ACITVE_TXT        = "Red", "Red"
	DATA_PIPELINE_ACITVE_WMX, DATA_PIPELINE_ACITVE_OMX = "Red", "Red"

	TIME_INTERVAL = 30
)

func get_configuration(jsonRes map[string]interface{}) {
	if jsonRes == nil {
		return
	}

	log.Printf("Body Json : %s", jsonRes["alert_exclude_time"])
	log.Printf("Body Json : %s", jsonRes["test"])
	log.Printf("Body Json : %s", jsonRes["test"].(map[string]interface{})["cc_list"])

	/* Used Struct */
	configuration_strcut := repository.Configuration{}
	jsonData, _ := json.Marshal(jsonRes)
	// json.Unmarshal(jsonData, &configuration_strcut)
	if err := json.Unmarshal(jsonData, &configuration_strcut); err != nil {
		// do error check
		log.Println(err)
	}

	log.Printf("\n")
	/*
		Tried to convert my Go map to a json string with encoding/json Marshal, then convert to json to Strcut with decoding/json UnMarshal

	*/
	log.Printf("Body Strcut configuration_strcut : %s", configuration_strcut.AlertExcludeTime)
	log.Printf("Body Strcut configuration_strcut : %t", configuration_strcut.Test.IsMailing)
	log.Printf("Body Strcut configuration_strcut : %s", configuration_strcut.Test.Env)
	log.Printf("Body Strcut configuration_strcut : %s", configuration_strcut.Test.CcList)
}

/* alert check and push alerts via email/text alert via REST API*/
func alert_work() {
	log.Print("\n\n")

	server_status_map := utils.Map_to_json(m_server_status)
	log.Println("alert work thread..")
	logging.Info(fmt.Sprintf("* [Alert_Work] SERVER Active: %s * DATA PIPELINE Active: %s", server_status_map.SERVER_ACTIVE, server_status_map.DATA_PIPELINE))
	log.Print("\n\n")
}

func work() {
	/*
		for {
			log.Printf("\n\nwork runnning..\n")
			go Get_service_health(args_map, m_server_status)
			time.Sleep(5 * time.Second)
		}
	*/

	/*
		difference go Get_service_health(args_map, m_server_status) and Get_service_health(args_map, m_server_status)
		go fn() runs fn in the background.
		go starts a goroutine, which is managed by golang run-time. It can either run on the current OS thread, or it can run on a
		When you use the Go keyword before a func ure making that func run into a goRoutine, is like a Java Thread, and is the go way for concurrency,
	*/

	/*
		for {
			go Get_service_health(args_map, m_server_status)
			time.Sleep(5 * time.Second)
		}
	*/

	/* set arguments */
	set_init()

	for {

		// Verify if the service port is open
		go set_service_port("ES", args_map.ES_URL, m_server_status)
		go set_service_port("KIBANA", args_map.KIBANA_URL, m_server_status)
		go set_service_port("KAFKA", args_map.KAFKA_URL, m_server_status)

		// Verify if the data pipeline is online
		go get_service_data_pipeline_health(args_map, m_server_status)

		// Get the configuration from the REST API
		go get_configuration(api.API_Get(os.Getenv("CONFIGURATION")))

		// alert_work
		go alert_work()

		time.Sleep(time.Duration(TIME_INTERVAL) * time.Second)
	}

}

func main() {

	// go run ./go_db.go -es_url localhost:9201 -kafka_url localhost:9102
	figure.NewFigure("Service Metrics Exporter", "thick", true).Print()
	// os.Exit(0)

	// Load the .env file in the current directory
	// godotenv.Load()
	// or
	godotenv.Load("../.env")

	// main_func
	work()

}
