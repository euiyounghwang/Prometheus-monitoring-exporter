package utility

import (
	"fmt"
	"io/ioutil"
	"net/http"
)

func Get(url string) {
	response, _ := http.Get(url)
	defer response.Body.Close()

	content, _ := ioutil.ReadAll(response.Body)
	fmt.Print(string(content))
}
