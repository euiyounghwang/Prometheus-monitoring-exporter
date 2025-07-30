package db

import (
	"database/sql"
	"log"
	"reflect"

	_ "github.com/sijms/go-ora/v2"
)

func Get_DB(connect_str string) bool {
	db, err := sql.Open("oracle", connect_str)
	if err != nil {
		panic(err)
	}
	defer db.Close() // Disconnect the DB connection

	// 데이터베이스 연결 확인
	err = db.Ping()
	if err != nil {
		// panic(err)
		return false
	}

	// 연결 성공 메시지 출력
	log.Println("DB connects successfully..")

	log.Println(reflect.TypeOf(db))
	return true
}
