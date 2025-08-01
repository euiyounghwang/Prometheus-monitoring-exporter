package db

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"reflect"
	"strings"
	"time"
	"tools_script/util"

	_ "github.com/sijms/go-ora/v2"
)

func Get_Oracle_DB(connect_str string, sql_param string) {
	/* DB SQL */
	start := time.Now()

	db, err := sql.Open("oracle", connect_str)
	if err != nil {
		panic(err)
	}
	defer db.Close() // Disconnect the DB connection

	// 데이터베이스 연결 확인
	err = db.Ping()
	if err != nil {
		panic(err)
	}

	// 연결 성공 메시지 출력
	log.Println("DB connects successfully..")
	log.Println(reflect.TypeOf(db))
	log.Printf("SQL : %s\n", sql_param)

	rows, err := db.Query(sql_param)
	if err != nil {
		fmt.Println("Error running query")
		fmt.Println(err)
		return
	}
	defer rows.Close()

	var processname string
	var status string
	var count string
	var addts string
	var dbid string

	var idx int

	// thisMap := make(map[int][]map[string]string)
	thisMap := []map[string]string{}

	for rows.Next() {

		err = rows.Scan(&processname, &status, &addts, &count, &dbid)
		if err != nil {
			panic(err)
		}

		/* golang time format : https://go.dev/src/time/format.go */
		parsed_date, _ := time.Parse(time.RFC3339, addts)

		aMap := map[string]string{
			"processname": processname,
			"status":      status,
			"addts":       parsed_date.Format("2006-01-02 15:04:05"),
			"count":       count,
		}
		// thisMap[idx] = append(thisMap[idx], aMap)
		thisMap = append(thisMap, aMap)
		idx += 1
	}

	elapsed := time.Since(start) // Or: time.Now().Sub(start)
	db_ids := connect_str[strings.LastIndex(connect_str, "/")+1:]

	// Json_response := make(map[string][]map[string]string)
	// Json_response := make(map[string]interface{})
	Json_response := map[string]interface{}{
		"results":      thisMap,
		"running_time": elapsed.Seconds(),
		"request_dbid": db_ids,
	}
	// Json_response["results"] = thisMap
	// Json_response["running_time"] = elapsed.Seconds()
	fmt.Printf("Elapsed time: %s\n", elapsed)

	/* Json */
	json_server_data, _ := json.Marshal(Json_response)
	// log.Println(reflect.TypeOf(json_server_data))
	fmt.Println(util.PrettyString(string(json_server_data)))
}

func Get_Oracle_DB_Unknown_Columns(connect_str string, sql_param string) {
	/* DB SQL */
	start := time.Now()

	db, err := sql.Open("oracle", connect_str)
	if err != nil {
		panic(err)
	}
	defer db.Close() // Disconnect the DB connection

	// 데이터베이스 연결 확인
	err = db.Ping()
	if err != nil {
		panic(err)
	}

	// 연결 성공 메시지 출력
	log.Println("DB connects successfully..")
	log.Println(reflect.TypeOf(db))
	log.Printf("SQL : %s\n", sql_param)

	rows, err := db.Query(sql_param)
	if err != nil {
		fmt.Println("Error running query")
		fmt.Println(err)
		return
	}
	defer rows.Close()

	// the map key is the field name
	var thisMap []map[string]interface{}

	for rows.Next() {
		// figure out what columns were returned
		// the column names will be the JSON object field keys
		columns, _ := rows.ColumnTypes()

		// Scan needs an array of pointers to the values it is setting
		// This creates the object and sets the values correctly
		values := make([]interface{}, len(columns))
		object := map[string]interface{}{}

		// for i, column := range columns {
		// 	object[column.Name()] = reflect.New(column.ScanType()).Interface()
		// 	values[i] = object[column.Name()]
		// }

		for i, column := range columns {
			// is_time_type := false
			v := reflect.New(column.ScanType()).Interface()
			switch v.(type) {
			case *[]uint8:
				v = new(string)
			case *time.Time:
				// log.Printf("%v: %T", column.Name(), v)
				// is_time_type = true
			default:
				// use this to find the type for the field
				// you need to change
				// log.Printf("%v: %T", column.Name(), v)
			}

			object[column.Name()] = v
			values[i] = object[column.Name()]
		}

		err = rows.Scan(values...)
		if err != nil {
			fmt.Println(err)
			return
		}

		thisMap = append(thisMap, object)
	}

	elapsed := time.Since(start) // Or: time.Now().Sub(start)
	db_ids := connect_str[strings.LastIndex(connect_str, "/")+1:]

	// Json_response := make(map[string][]map[string]string)
	// Json_response := make(map[string]interface{})
	Json_response := map[string]interface{}{
		"results":      thisMap,
		"running_time": util.RoundToDecimalPlaces(elapsed.Seconds(), 3),
		"request_dbid": db_ids,
	}
	// Json_response["results"] = thisMap
	// Json_response["running_time"] = elapsed.Seconds()
	fmt.Printf("Elapsed time: %s\n", elapsed)

	/* Json */
	json_server_data, _ := json.Marshal(Json_response)
	// log.Println(reflect.TypeOf(json_server_data))

	/* indent because I want to read the output */
	fmt.Println(util.PrettyString(string(json_server_data)))
}
