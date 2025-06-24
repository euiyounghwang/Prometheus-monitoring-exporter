package api

import (
	"bytes"
	"crypto/tls"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"

	"db.com/m/logging"
	"db.com/m/utils"
)

func API_Get(httpgeturl string) map[string]interface{} {
	log.Println("HTTP JSON GET URL:", httpgeturl)
	// requestURL := log.Sprintf("http://localhost:%d", serverPort)
	// requestURL := os.Getenv("CONFIGURATION")

	// Create a custom http.Transport
	tr := &http.Transport{
		TLSClientConfig: &tls.Config{InsecureSkipVerify: true}, // This line disables certificate verification
	}

	// Create an http.Client with the custom Transport
	client := &http.Client{Transport: tr}

	res, err := client.Get(httpgeturl)
	if err != nil {
		logging.Info(fmt.Sprintf("Error : %s", err))
		// return nil
		return nil
	}

	defer res.Body.Close()

	log.Printf("client: got response!\n")
	body, _ := ioutil.ReadAll(res.Body)
	// log.Println("response Body:", utils.PrettyString(string(body)))
	log.Printf("client: status code: %d\n", res.StatusCode)

	var jsonRes map[string]interface{} // declaring a map for key names as string and values as interface
	jsonRes = utils.Json_Parsing(string(body))

	return jsonRes

}

func API_Post(httpposturl string, post_json map[string]interface{}, db_type string) []byte {
	// """ POST """
	// httpposturl := "http://" + os.Getenv("ES_CONFIGURATION_HOST") + ":8002/db/get_db_query"
	// httpposturl := "http://" + host + ":8002/db/get_db_query"
	log.Println("HTTP JSON POST URL:", httpposturl)

	/*
		// u := Payload{
		// 	db_url: os.Getenv("DB_URL"),
		// 	sql:    os.Getenv("SQL"),
		// }

		// var jsonData = []byte(`{
		//       "db_url": "jdbc:oracle:thin:test/test@localhost:1234/DEVTEST",
		//       "sql": "SELECT * FROM TB"
		// }`)

		// u := map[string]interface{}{
		// 	// "db_url": os.Getenv("DB_URL"),
		// 	// "sql":    os.Getenv("SQL"),
		// 	"db_url": db_url,
		// 	"sql":    sql,
		// }
	*/
	jsonData, _ := json.Marshal(post_json)
	log.Println("Payload: ", string(jsonData))
	request, error := http.NewRequest("POST", httpposturl, bytes.NewBuffer(jsonData))
	if error != nil {
		// panic(error)
		logging.Info(fmt.Sprintf("Error : %s", error))
		return nil
	}
	request.Header.Set("Content-Type", "application/json; charset=UTF-8")

	client := &http.Client{}
	response, error := client.Do(request)
	if error != nil {
		// panic(error)
		logging.Info(fmt.Sprintf("Error : %s", error))
		return nil
	}
	defer response.Body.Close()

	log.Println("response Status:", response.Status)
	log.Println("response Headers:", response.Header)
	body, _ := ioutil.ReadAll(response.Body)
	log.Println("response Body:", utils.PrettyString(string(body)))

	var jsonRes map[string]interface{} // declaring a map for key names as string and values as interface
	jsonRes = utils.Json_Parsing(string(body))

	// log.Printf("Body type : %s", reflect.TypeOf(body))
	log.Printf("Body Json : %s", fmt.Sprintf("%f", jsonRes["running_time"]))

	return body
}
