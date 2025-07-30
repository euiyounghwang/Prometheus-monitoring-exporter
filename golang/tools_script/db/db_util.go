package db

import (
	"bytes"
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"reflect"
	"time"

	_ "github.com/sijms/go-ora/v2"
)

func PrettyString(str string) string {
	var prettyJSON bytes.Buffer
	if err := json.Indent(&prettyJSON, []byte(str), "", "    "); err != nil {
		return ""
	}
	return prettyJSON.String()
}

func Get_DB(connect_str string, sql_param string) {
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

	/* Json */
	json_server_data, _ := json.Marshal(thisMap)
	// log.Println(reflect.TypeOf(json_server_data))
	fmt.Println(PrettyString(string(json_server_data)))
}
