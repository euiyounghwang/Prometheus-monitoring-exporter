package utils

import (
	"bytes"
	"encoding/json"
	"fmt"
	"log"
	"net"
	"reflect"
	"strings"
	"time"

	"db.com/m/logging"
	"db.com/m/repository"
)

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

func Map_to_json(m map[string]interface{}) repository.SERVER_STATUS {
	json_server_data, _ := json.Marshal(m)
	server_status_map := repository.SERVER_STATUS{}
	if err := json.Unmarshal(json_server_data, &server_status_map); err != nil {
		// do error check
		log.Println(err)
	}

	return server_status_map

}

func Get_time_difference_is_ative(inputTime string) string {
	time_gap := 0.51
	// Specific time zone
	nyLocation, _ := time.LoadLocation("America/New_York")
	currentTime := time.Now().In(nyLocation)
	// currentTime.Format("2006-01-02 15:04:05")
	log.Println("time_difference func - currentTime : ", currentTime)

	// date, error := time.Parse("2006-01-02 00:00:00", rows.ADDTS)
	// s := "2022-03-23T07:00:00+01:00"
	loc, _ := time.LoadLocation("America/New_York")
	date, error := time.ParseInLocation(time.DateTime, inputTime, loc)
	if error != nil {
		log.Println(error)
		return "Red"
	}

	log.Println("time_difference func - inputTime", date)

	diff := currentTime.Sub(date)
	log.Printf("Body Json gap_time: %.3fh\n", diff.Hours())
	log.Printf("Body Json gap_time: %.1fmin\n", diff.Minutes())

	if time_gap > diff.Hours() {
		return "Green"
	} else {
		return "Red"
	}
}

func Get_port_open(host string) bool {
	// Connect to the server
	conn, err := net.Dial("tcp", host)
	if err != nil {
		log.Println("Error:", err)
		return false
	}
	defer conn.Close()

	return true
}

func Get_port_list_open(host string) (bool, int, string) {
	result := strings.Split(strings.Trim(host, " "), ",")
	log.Printf("Result: %s, Type : %s\n", result, reflect.TypeOf(result))

	flag := true
	flag_value := 0
	server_status := "red"

	for i, rows := range result {
		rows = strings.Trim(rows, " ")
		log.Println("get_port_list_opensequence : ", i+1)
		// rows = strings.Replace(rows, " ", ",", -1)
		log.Println("get_port_list_open records : ", rows)

		// Connect to the server
		conn, err := net.Dial("tcp", rows)
		if err != nil {
			logging.Info(fmt.Sprintf("Error: %s", err))
			flag = flag && false
			flag_value = flag_value + 0
			// log.Println("flag : ", flag)
			continue
		}
		defer conn.Close()
		flag = flag && true
		flag_value = flag_value + 1
		// log.Println("flag : ", flag)
	}

	if len(result) == flag_value {
		server_status = "Green"
	} else if flag_value < 1 {
		server_status = "Red"
	} else {
		server_status = "Yellow"
	}

	log.Println("** flag ** : ", flag)
	log.Println("** len(result) ** : ", len(result))
	log.Println("** flag_value ** : ", flag_value)
	// log.Println("** server_status ** : ", server_status)

	return flag, flag_value, server_status
}
