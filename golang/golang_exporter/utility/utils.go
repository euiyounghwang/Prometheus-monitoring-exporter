package utility

import (
	"bytes"
	"encoding/json"
	"fmt"
	"math"
	"strconv"
	"strings"
)

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

func PrettyString(str string) string {
	var prettyJSON bytes.Buffer
	if err := json.Indent(&prettyJSON, []byte(str), "", "    "); err != nil {
		return ""
	}
	return prettyJSON.String()
}

func RoundFloat(val float64, precision uint) float64 {
	ratio := math.Pow(10, float64(precision))
	return math.Round(val*ratio) / ratio
}
