package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"

	"github.com/joho/godotenv"
)

// https://medium.com/data-science/use-environment-variable-in-your-next-golang-project-39e17c3aaa66
// go get github.com/joho/godotenv

type Payload struct {
	db_url string
	sql    string
}

func PrettyString(str string) string {
	var prettyJSON bytes.Buffer
	if err := json.Indent(&prettyJSON, []byte(str), "", "    "); err != nil {
		return ""
	}
	return prettyJSON.String()
}

func db_api() {
	// """ POST """
	httpposturl := "http://" + os.Getenv("HOST") + ":8002/db/get_db_query"
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
		"db_url": os.Getenv("DB_URL"),
		"sql":    os.Getenv("SQL"),
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
	fmt.Println("response Body:", PrettyString(string(body)))
}

func main() {
	// Load the .env file in the current directory
	// godotenv.Load()
	// or
	godotenv.Load("../.env")
	fmt.Println("Go DB..")
	db_api()
}
