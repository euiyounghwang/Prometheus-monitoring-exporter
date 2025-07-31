package main

import (
	"os"
	"tools_script/db"
)

/* go get github.com/sijms/go-ora/v2 */
func main() {

	/* DB Connection, SQL Run */
	// db.Get_DB(os.Getenv("DB_URL"), os.Getenv("SQL"))
	db.Get_DB_Unknown_Columns(os.Getenv("DB_URL"), os.Getenv("SQL"))
}
