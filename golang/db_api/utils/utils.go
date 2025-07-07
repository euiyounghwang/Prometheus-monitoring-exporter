package utils

import (
	"bytes"
	"encoding/json"
	"fmt"
	"log"
	"math"
	"net"
	"reflect"
	"strconv"
	"strings"
	"time"

	"db.com/m/logging"
	"db.com/m/repository"
)

/*
INPUT : "111, 222"
OUTPUT : "111", "222"
*/
func Build_split_string_array(s string) string {
	var sb strings.Builder
	s_array := strings.Split(strings.Replace(s, " ", "", -1), ",")

	for index, element := range s_array {
		sb.WriteString(`"` + element + `"`)
		if index != len(s_array)-1 {
			sb.WriteString(`,`)
		}
	}

	return sb.String()
}

func String_to_float_giga(float_value uint64) float64 {
	ram_total := fmt.Sprintf("%.2f", float64(float_value)/1024/1024/1024)
	ram_total_type_float, err := strconv.ParseFloat(ram_total, 64)

	if err != nil {
		return -1
	}

	return ram_total_type_float
}

func ReplaceStr(str string) string {
	var transformed_strg string = str
	transformed_strg = strings.Replace(transformed_strg, "\t\t", " ", -1)
	transformed_strg = strings.Replace(transformed_strg, " ", "", -1)
	transformed_strg = strings.Replace(transformed_strg, "\t", "", -1)
	transformed_strg = strings.Replace(transformed_strg, "\n", "", -1)
	return transformed_strg
}

func RoundFloat(val float64, precision uint) float64 {
	ratio := math.Pow(10, float64(precision))
	return math.Round(val*ratio) / ratio
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

func Map_to_json(m map[string]interface{}) repository.SERVER_STATUS {
	json_server_data, _ := json.Marshal(m)
	server_status_map := repository.SERVER_STATUS{}
	if err := json.Unmarshal(json_server_data, &server_status_map); err != nil {
		// do error check
		log.Println(err)
	}

	return server_status_map

}

func Get_time_difference_is_ative(inputTime string) (string, float64) {
	time_gap := 0.51
	// Specific time zone
	nyLocation, _ := time.LoadLocation(repository.Global_local_time)
	currentTime := time.Now().In(nyLocation)
	// currentTime.Format("2006-01-02 15:04:05")
	log.Println("time_difference func - currentTime : ", currentTime)

	// date, error := time.Parse("2006-01-02 00:00:00", rows.ADDTS)
	// s := "2022-03-23T07:00:00+01:00"
	loc, _ := time.LoadLocation(repository.Global_local_time)
	date, error := time.ParseInLocation(time.DateTime, inputTime, loc)

	diff := currentTime.Sub(date)

	if error != nil {
		log.Println(error)
		return "Red", diff.Hours()
	}

	log.Println("time_difference func - inputTime", date)

	log.Printf("Body Json gap_time: %.3fh\n", diff.Hours())
	log.Printf("Body Json gap_time: %.1fmin\n", diff.Minutes())

	if time_gap > diff.Hours() {
		return "Green", diff.Hours()
	} else {
		return "Red", diff.Hours()
	}
}

func Get_port_open(idx int, key string, host string) (bool, string) {
	// Connect to the server
	conn, err := net.Dial("tcp", host)
	if err != nil {
		log.Println("Error:", err)
		return false, fmt.Sprintf("[Node #%d - %s_URL] %s is not runnning..", idx, key, key)
	}
	defer conn.Close()

	return true, ""
}

func Get_port_list_open(service_name string, host string) (bool, int, string, []string) {
	result := strings.Split(strings.Trim(host, " "), ",")
	log.Printf("Result: %s, Type : %s\n", result, reflect.TypeOf(result))

	flag := true
	flag_value := 0
	server_status := "red"

	track_error := []string{}

	for i, rows := range result {
		rows = strings.Trim(rows, " ")
		log.Println("get_port_list_opensequence : ", i+1)
		// rows = strings.Replace(rows, " ", ",", -1)
		log.Println("get_port_list_open records : ", rows)

		// Connect to the server
		conn, err := net.Dial("tcp", rows)
		if err != nil {
			logging.Info(fmt.Sprintf("Error: %s", err))
			track_error = append(track_error, fmt.Sprintf("[Node #%d - %s_URL] %s is not runnning..", i+1, service_name, rows))
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

	return flag, flag_value, server_status, track_error
}
