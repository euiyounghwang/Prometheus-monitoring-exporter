package util

import (
	"bytes"
	"encoding/json"
	"math"
)

func PrettyString(str string) string {
	var prettyJSON bytes.Buffer
	if err := json.Indent(&prettyJSON, []byte(str), "", "    "); err != nil {
		return ""
	}
	return prettyJSON.String()
}

/* Rounding to a specific number of decimal places */
func RoundToDecimalPlaces(n float64, decimals int) float64 {
	factor := math.Pow(10, float64(decimals))
	return math.Round(n*factor) / factor
}
