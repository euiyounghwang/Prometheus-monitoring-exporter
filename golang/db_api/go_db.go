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
// There are a few major disadvantages to this approach, but there can be many - Security Issue, Code Management.
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

func Json_Parsing(body string) map[string]interface{} {
	var jsonRes map[string]interface{} // declaring a map for key names as string and values as interface
	resBytes := []byte(body)
	_ = json.Unmarshal(resBytes, &jsonRes) // Unmarshalling

	return jsonRes
}

func get_configuration() {
	// requestURL := fmt.Sprintf("http://localhost:%d", serverPort)
	requestURL := os.Getenv("CONFIGURATION")
	res, err := http.Get(requestURL)
	if err != nil {
		fmt.Printf("error making http request: %s\n", err)
		os.Exit(1)
	}

	defer res.Body.Close()

	fmt.Printf("client: got response!\n")
	body, _ := ioutil.ReadAll(res.Body)
	fmt.Println("response Body:", PrettyString(string(body)))
	fmt.Printf("client: status code: %d\n", res.StatusCode)

	var jsonRes map[string]interface{} // declaring a map for key names as string and values as interface
	jsonRes = Json_Parsing(string(body))

	fmt.Printf("Body Json : %s", jsonRes["alert_exclude_time"])
}

// Struct fields must start with upper case letter (exported) for the JSON package to see their value.
type API_Results struct {
	Running_time float32 `json:"running_time"`
	Request_dbid string  `json:"request_dbid"`
	Results      []struct {
		PROCESSNAME string `json:"processname"`
		STATUS      string `json:"status"`
		ADDTS       string `json:"addts"`
		COUNT       int    `json:"count"`
		DBID        string `json:"dbid"`
	} `json:"results"`
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

	var jsonRes map[string]interface{} // declaring a map for key names as string and values as interface
	jsonRes = Json_Parsing(string(body))

	fmt.Printf("Body Json : %s", fmt.Sprintf("%f", jsonRes["running_time"]))

	// using struct to parse the Json Format
	// Struct fields must start with upper case letter (exported) for the JSON package to see their value.
	response_map := API_Results{}
	if err := json.Unmarshal(body, &response_map); err != nil {
		// do error check
		fmt.Println(err)
	}
	fmt.Printf("Body Json : %s", response_map.Request_dbid)

	for i, rows := range response_map.Results {
		if i == 0 {
			fmt.Println("Body Json sequence : ", i+1)
			fmt.Println("Body Json records : ", rows.PROCESSNAME)
		}
	}
}

func main() {
	// Load the .env file in the current directory
	// godotenv.Load()
	// or
	godotenv.Load("../.env")

	fmt.Println("** HTTP GET **")
	get_configuration()
	fmt.Print("\n\n")

	fmt.Println("** HTTP POST ** ")
	db_api()
}
