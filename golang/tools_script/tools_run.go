package main

import (
	"os"
	"tools_script/db"
)

/* go get github.com/sijms/go-ora/v2 */
func main() {

	/* DB Test */
	db.Get_DB(os.Getenv("DB_URL"))
}
