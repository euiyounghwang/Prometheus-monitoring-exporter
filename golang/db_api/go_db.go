package main

import (
	"encoding/json"
	"errors"
	"fmt"
	"log"
	"os"
	"reflect"
	"slices"
	"strings"
	"time"

	"db.com/m/api"
	"db.com/m/configuration"
	"db.com/m/grafana"
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

func active_update_func(host_total_cnt int, port_open_cnt int) {
	SERVER_ACTIVE_TOTAL_CNT += host_total_cnt
	SERVER_ACTIVE_CNT += port_open_cnt
	/*
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
	*/
}

func set_service_port(service_name string, service_nodes string, url string, m map[string]interface{}) {
	log.Printf("** %s PORT OPEN ** ", service_name)
	// is_port_open := utils.Get_port_open(args_map.ES_URL)
	// track_error_func := []string{}
	is_port_open, port_open_cnt, server_status, track_error_func := utils.Get_port_list_open(service_name, url)
	log.Println("** is_port_open: ** ", is_port_open)
	log.Println("** server_status ** : ", server_status)

	m[service_name] = server_status
	if service_nodes != "" {
		m[service_nodes] = port_open_cnt
	}

	/* Update gloal variable */
	for _, alert_message := range track_error_func {
		TRACK_ERROR = append(TRACK_ERROR, alert_message)
	}

	fmt.Print("\n\n")

}

// var SERVER_ACTIVE_TOTAL_CNT, SERVER_ACTIVE_CNT = 0, 0
// var SERVER_ACITVE, DATA_PIPELINE_ACITVE = true, true
// var SERVER_ACITVE_TXT, DATA_PIPELINE_ACITVE_TXT = "Red", "Red"
// var DATA_PIPELINE_ACITVE_WMX, DATA_PIPELINE_ACITVE_OMX = "Red", "Red"

func get_service_data_pipeline_health(args_map repository.ARG) {
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
		body := api.API_Post(api_endpoint_host, json_post)

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
			if response_map.Results == nil {
				/* Update Track Error */
				TRACK_ERROR = append(TRACK_ERROR, fmt.Sprintf("[%s_DB] %s", strings.ToUpper(db_type), response_map.Message))
				DATA_PIPELINE_ACITVE = DATA_PIPELINE_ACITVE && false
				continue
			}

			if len(response_map.Results) < 1 {
				DATA_PIPELINE_ACITVE = DATA_PIPELINE_ACITVE && false
				/* Update Track Error */
				TRACK_ERROR = append(TRACK_ERROR, fmt.Sprintf("[%s] No 'Data Pipeline' Process records", strings.ToUpper(db_type)))
				continue
			}

			TIME_GAP := 0.0
			for i, rows := range response_map.Results {
				if i == 0 {
					log.Println("Body Json sequence : ", i+1)
					log.Println("Body Json records : ", rows.PROCESSNAME)

					if db_type == "WMx" {
						DATA_PIPELINE_ACITVE_WMX, TIME_GAP = utils.Get_time_difference(rows.ADDTS)
						if strings.ToLower(DATA_PIPELINE_ACITVE_WMX) == "green" {
							DATA_PIPELINE_ACITVE = DATA_PIPELINE_ACITVE && true
						} else {
							DATA_PIPELINE_ACITVE = DATA_PIPELINE_ACITVE && false
							/* Update Track Error */
							TRACK_ERROR = append(TRACK_ERROR, fmt.Sprintf("[%s] Data has not been processed in the last 30 minutes. [%f hours]", strings.ToUpper(db_type), TIME_GAP))
						}

					} else {
						DATA_PIPELINE_ACITVE_OMX, TIME_GAP = utils.Get_time_difference(rows.ADDTS)
						if strings.ToLower(DATA_PIPELINE_ACITVE_OMX) == "green" {
							DATA_PIPELINE_ACITVE = DATA_PIPELINE_ACITVE && true
						} else {
							DATA_PIPELINE_ACITVE = DATA_PIPELINE_ACITVE && false
							/* Update Track Error */
							TRACK_ERROR = append(TRACK_ERROR, fmt.Sprintf("[%s] Data has not been processed in the last 30 minutes. [%f hours]", strings.ToUpper(db_type), TIME_GAP))
						}
					}
				}
			}
		} else {
			DATA_PIPELINE_ACITVE = DATA_PIPELINE_ACITVE && false
		}
		log.Println("DATA PIPELINE : ", DATA_PIPELINE_ACITVE)
	}
}

func set_initialize() {
	/* Initialize */
	SERVER_ACTIVE_TOTAL_CNT, SERVER_ACTIVE_CNT = 0, 0
	SERVER_ACITVE, DATA_PIPELINE_ACITVE = true, true
	SERVER_ACITVE_TXT, DATA_PIPELINE_ACITVE_TXT = "Red", "Red"
	DATA_PIPELINE_ACITVE_WMX, DATA_PIPELINE_ACITVE_OMX = "Red", "Red"
	SPARK_APP_STATUS = "Red"
	LEN_SPARK_CUSTOM_APP = 0
	SPARK_CUSTOM_APP_LIST = ""

	/* Error Track */
	TRACK_ERROR = []string{}
}

/* global variable */
var (
	args_map        = repository.ARG{}
	m_server_status = make(map[string]interface{})

	SERVER_ACTIVE_TOTAL_CNT, SERVER_ACTIVE_CNT         = 0, 0
	SERVER_ACITVE, DATA_PIPELINE_ACITVE                = true, true
	SERVER_ACITVE_TXT, DATA_PIPELINE_ACITVE_TXT        = "Red", "Red"
	DATA_PIPELINE_ACITVE_WMX, DATA_PIPELINE_ACITVE_OMX = "Red", "Red"
	SPARK_APP_STATUS                                   = "Red"
	LEN_SPARK_CUSTOM_APP                               = 0
	SPARK_CUSTOM_APP_LIST                              = ""

	/* Error Track */
	TRACK_ERROR = []string{}

	TIME_INTERVAL = 30
)

func get_configuration(jsonRes map[string]interface{}) {
	if jsonRes == nil {
		return
	}

	/* configuration all */
	// log.Printf("Body Json : %s", jsonRes["alert_exclude_time"])
	// log.Printf("Body Json : %s", jsonRes["test"])
	// log.Printf("Body Json : %s", jsonRes["test"].(map[string]interface{})["cc_list"])

	// /* Used Struct */
	// configuration_strcut := repository.Configuration{}
	// jsonData, _ := json.Marshal(jsonRes)
	// // json.Unmarshal(jsonData, &configuration_strcut)
	// if err := json.Unmarshal(jsonData, &configuration_strcut); err != nil {
	// 	// do error check
	// 	log.Println(err)
	// }

	// log.Printf("\n")
	// /*
	// 	Tried to convert my Go map to a json string with encoding/json Marshal, then convert to json to Strcut with decoding/json UnMarshal

	// */
	// log.Printf("Body Strcut configuration_strcut : %s", configuration_strcut.AlertExcludeTime)
	// log.Printf("Body Strcut configuration_strcut : %t", configuration_strcut.Test.IsMailing)
	// log.Printf("Body Strcut configuration_strcut : %s", configuration_strcut.Test.Env)
	// log.Printf("Body Strcut configuration_strcut : %s", configuration_strcut.Test.CcList)

	/* Used Struct */
	configuration_strcut := repository.ALERT_Configuration{}
	jsonData, _ := json.Marshal(jsonRes)
	// json.Unmarshal(jsonData, &configuration_strcut)
	if err := json.Unmarshal(jsonData, &configuration_strcut); err != nil {
		// do error check
		log.Println(err)
	}

	log.Printf("\n")

	log.Printf("Body Strcut configuration_strcut : %t", configuration_strcut.IsMailing)

	/* Update is_Mailing */
	repository.ALERT_MAIL_ENABLED = configuration_strcut.IsMailing
	/* Update SMS */
	repository.ALERT_SMS_ENABLED = configuration_strcut.IsSms
}

func get_service_spark_app(args_map repository.ARG) {
	spark_master_host_port := strings.Split(strings.Trim(args_map.KAFKA_URL, " "), ",")[0]
	spark_master_host := strings.Split(strings.Trim(spark_master_host_port, " "), ":")[0]
	log.Printf("spark_master_host : %s", spark_master_host)

	api_endpoint_host := "http://" + spark_master_host + ":8080/json"

	body := api.API_Get(api_endpoint_host)

	if body == nil {
		/* Update Track Error */
		TRACK_ERROR = append(TRACK_ERROR, fmt.Sprintf("[SPARK CLUSTER] %s API do not reachable", api_endpoint_host))
	} else {
		response_map := repository.SPARK_APP_Results{}
		jsonbyte, _ := json.Marshal(body)
		// json.Unmarshal(jsonData, &configuration_strcut)
		if err := json.Unmarshal(jsonbyte, &response_map); err != nil {
			// do error check
			log.Println(err)
		}
		log.Printf("get_service_spark_app Json : %s\n", response_map.URL)
		log.Printf("get_service_spark_app, len(response_map.Activeapps) : %d", len(response_map.Activeapps))
		log.Print("\n")

		// return when the number of records is zero
		if len(response_map.Activeapps) < 1 {
			/* Update STATUS */
			SPARK_APP_STATUS = "Red"
			SERVER_ACITVE = SERVER_ACITVE && false
			/* Update Track Error */
			TRACK_ERROR = append(TRACK_ERROR, fmt.Sprintf("[SPARK CLUSTER] %s custom apps are not running", api_endpoint_host))
			return
		}

		custom_apps := []string{}
		for _, rows := range response_map.Activeapps {
			custom_apps = append(custom_apps, rows.Name)
		}
		log.Println("custom_apps : ", custom_apps)

		var EXIST_APPS = true

		/* initialize */
		SPARK_CUSTOM_APP_LIST = ""
		LEN_SPARK_CUSTOM_APP = 0
		/* --------------- */
		spark_app_check_list := strings.Split(os.Getenv("SPARK_APP_CEHCK"), ",")
		// fmt.Println("len(spark_app_check_list)", len(spark_app_check_list))
		for _, app := range spark_app_check_list {
			LEN_SPARK_CUSTOM_APP += 1
			if slices.Contains(custom_apps, app) {
				log.Println("app : ", app)
				EXIST_APPS = EXIST_APPS && true
			} else {
				EXIST_APPS = EXIST_APPS && false
				/* Create logs */
				/* Update Track Error */
				TRACK_ERROR = append(TRACK_ERROR, fmt.Sprintf("[SPARK CLUSTER APP] %s, no spark custom job (%s). Please confirm/run this.", api_endpoint_host, app))
			}
			SPARK_CUSTOM_APP_LIST += "," + app
		}

		if EXIST_APPS {
			SPARK_APP_STATUS = "Green"
			SERVER_ACITVE = SERVER_ACITVE && true
		} else {
			SPARK_APP_STATUS = "Red"
			SERVER_ACITVE = SERVER_ACITVE && false
		}

		/*
			for i, rows := range response_map.Activeapps {
				log.Println("Body Json sequence : ", i+1)
				log.Println("Body Json records : ", rows.Name)
				for _, app := range strings.Split(os.Getenv("SPARK_APP_CEHCK"), ",") {
					if app == rows.Name {
						RUNNING_APP = RUNNING_APP && true
					}
				}
				if strings.Contains(rows.Name, "StreamProcess") {
					// Update STATUS : need to decide the status with yellow or green if all spark custom app is running //
					SPARK_APP_STATUS = "Green"
					SERVER_ACITVE = SERVER_ACITVE && true
				}
			}
		*/
	}
}

func update_service_status() {
	// verify the Server Active
	if SERVER_ACTIVE_CNT >= SERVER_ACTIVE_TOTAL_CNT {
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

	/* Update SPARK APP */
	m_server_status["SPARK_APP"] = SPARK_APP_STATUS
	m_server_status["SPARK_CUSTOM_APPS"] = LEN_SPARK_CUSTOM_APP
	// Slicing first character
	if len(SPARK_CUSTOM_APP_LIST) > 1 {
		m_server_status["SPARK_CUSTOM_APPS_LIST"] = SPARK_CUSTOM_APP_LIST[1:]
	} else {
		m_server_status["SPARK_CUSTOM_APPS_LIST"] = ""
	}

	// update all status to server_status_mm_server_statusap
	server_status_map := utils.Map_to_json(m_server_status)

	/* ALERT History */
	if len(repository.SAVED_ALERT_HISTORY) > 1 {
		// Re-slice the slice to exclude the last element
		repository.SAVED_ALERT_HISTORY = repository.SAVED_ALERT_HISTORY[1:len(repository.SAVED_ALERT_HISTORY)]
	}

	/* ALERT UPDATE : track the error messages in TRACK_ERROR string array*/
	// if len(TRACK_ERROR) > 0 {
	if !(SERVER_ACITVE && DATA_PIPELINE_ACITVE) {
		repository.SAVED_THREAD_ALERT = true
		repository.SAVED_ALERT_HISTORY = append(repository.SAVED_ALERT_HISTORY, true)
	} else {
		repository.SAVED_THREAD_ALERT = false
		repository.SAVED_ALERT_HISTORY = append(repository.SAVED_ALERT_HISTORY, false)
	}

	fmt.Print("\n\n")
	log.Print("** STATUS **\n")
	/*
		json_server_status, _ := json.Marshal(m_server_status)
		logging.Info(fmt.Sprintf("SERVER_STATUS Json: %s", utils.PrettyString(string(json_server_status))))
	*/
	logging.Info(fmt.Sprintf("SERVER_STATUS Json: %s", utils.Transform_map_to_json_string(m_server_status)))
	logging.Info(fmt.Sprintf("Alert Error Tract: %s\n", TRACK_ERROR))
	logging.Info(fmt.Sprintf("DATA_PIPELINE_ACITVE_WMX : %s, DATA_PIPELINE_ACITVE_OMX : %s\n", DATA_PIPELINE_ACITVE_WMX, DATA_PIPELINE_ACITVE_OMX))
	logging.Info(fmt.Sprintf("SERVER STATUS.ES_URL: %s, SERVER STATUS.KAFKA_URL: %s", server_status_map.ES, server_status_map.KAFKA))
	logging.Info(fmt.Sprintf("*SERVER Active: %s, *DATA PIPELINE Active: %s", server_status_map.SERVER_ACTIVE, server_status_map.DATA_PIPELINE))
	logging.Info(fmt.Sprintf("*SAVED_THREAD_ALERT: %t, SAVED_ALERT_HISTORY: %t", repository.SAVED_THREAD_ALERT, repository.SAVED_ALERT_HISTORY))
	logging.Info(fmt.Sprintf("*PUSH_ALERT_TIME: %s", repository.PUSH_ALERT_TIME))
	logging.Info(fmt.Sprintf("*SERVER_ACTIVE_TOTAL_CNT: %d, SERVER_ACTIVE_CNT: %d", SERVER_ACTIVE_TOTAL_CNT, SERVER_ACTIVE_CNT))
	logging.Info(fmt.Sprintf("*ENV : %s, ALERT_MAIL_ENABLED : %t, ALERT_SMS_ENABLED : %t", args_map.ENV_NAME, repository.ALERT_MAIL_ENABLED, repository.ALERT_SMS_ENABLED))
	fmt.Print("\n\n")

	/* Push status into Grafana-Loki service if all services went back to green */
	saved_history_green_alert := reflect.DeepEqual(repository.SAVED_ALERT_HISTORY, []bool{true, false})
	logging.Info(fmt.Sprintf("'Services are back online to Grafana Loki: %t", saved_history_green_alert))
	/* Push status into Grafana-loki */
	if saved_history_green_alert {
		logging.Info("* [Grafana Loki] Inserting the status..")
		/* Add Grafana Loki via REST API */
		/* Push_alert_loki(api_host string, service string, logging_level string, env string, host string, host_name string, log_filename string, message string) */
		grafana.Push_alert_loki(
			os.Getenv("GRAFANA_LOKI_HOST"),
			"prometheus-golang-monitoring-service",
			"info",
			args_map.ENV_NAME,
			args_map.ENV_NAME,
			args_map.ENV_NAME,
			"",
			"Services are back online",
		)
	}
}

/* alert check and push alerts via email/text alert via REST API*/
func alert_work() {
	fmt.Print("\n\n")

	server_status_map := utils.Map_to_json(m_server_status)
	logging.Info("alert work thread..")
	logging.Info(fmt.Sprintf("* [Alert_Work] SERVER Active: %s * DATA PIPELINE Active: %s", server_status_map.SERVER_ACTIVE, server_status_map.DATA_PIPELINE))
	logging.Info(fmt.Sprintf("* [Alert_Work] SAVED_THREAD_ALERT: %t", repository.SAVED_THREAD_ALERT))

	/* Push alert to email */
	if repository.SAVED_THREAD_ALERT {
		/* Push alert loginc here */
		/* Push alert every 1 hour as a push inverval */
		if utils.Get_two_date_time_difference(utils.Get_current_time(), repository.PUSH_ALERT_TIME) > repository.PUSH_ALERT_INTERVAL_HOUR {
			if repository.ALERT_MAIL_ENABLED {
				/* Push alert to an email */
				logging.Warn("* [Alert_Work] Pushing email....")
			} else {
				logging.Warn(fmt.Sprintf("* [Alert_Work] * %s alert configuration is False", args_map.ALERT_CONF_API))
			}

			/* Update this date if alert is sent corretly */
			repository.PUSH_ALERT_TIME = utils.Get_current_time()
			logging.Info(fmt.Sprintf("* [Alert_Work] Get_current_time: %s", utils.Get_current_time()))

			/* Push alert logs into Grafana-Loki service */
			logging.Warn("* [Alert_Work] Push alert message to Grafana Loki....")

			/* Add Grafana Loki via REST API */
			/* Push_alert_loki(api_host string, service string, logging_level string, env string, host string, host_name string, log_filename string, message string) */
			grafana.Push_alert_loki(
				os.Getenv("GRAFANA_LOKI_HOST"),
				"prometheus-golang-monitoring-service",
				"error",
				args_map.ENV_NAME,
				args_map.ENV_NAME,
				args_map.ENV_NAME,
				"",
				// utils.Transform_strings_array_to_html(TRACK_ERROR, false),
				"Dev Test..",
			)
		}

		logging.Info(fmt.Sprintf("* [Alert_Work] Alert Messages: %s", utils.Transform_strings_array_to_html(TRACK_ERROR, true)))
	}

	fmt.Print("\n\n")
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
	// set_init()
	/* You can define init(), but you can't call it yourself: */
	/* init() is always called, regardless if there's main or not, so if you import a package that has an init function, it will be executed. */
	// init()

	for {

		/* Initialize */
		set_initialize()

		// Get the configuration from the REST API
		/* argument as map[string]interface{} into get_configuration func */
		// get_configuration(api.API_Get(os.Getenv("CONFIGURATION")))
		get_configuration(api.API_Get(args_map.ALERT_CONF_API))

		// Verify if the service port is open
		set_service_port("ES", "ES_NODES", args_map.ES_URL, m_server_status)
		set_service_port("KIBANA", "", args_map.KIBANA_URL, m_server_status)
		set_service_port("LOGSTASH", "", args_map.LOGSTASH_URL, m_server_status)
		set_service_port("KAFKA", "KAFKA_NODES", args_map.KAFKA_URL, m_server_status)
		set_service_port("ZOOKEEPER", "ZOOKEEPER_NODES", args_map.ZOOKEEPER_URL, m_server_status)
		set_service_port("KAFAK_CONNECT", "KAFAK_CONNECT_NODES", args_map.KAFKA_CONNECT_URL, m_server_status)
		set_service_port("SPARK", "", args_map.SPARK_URL, m_server_status)

		/* Verify if the data pipeline is online */
		get_service_data_pipeline_health(args_map)

		/* check if spark app is running */
		get_service_spark_app(args_map)

		/* Update services status */
		update_service_status()

		// alert_work
		go alert_work()

		time.Sleep(time.Duration(TIME_INTERVAL) * time.Second)
	}

}

func init() {

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
