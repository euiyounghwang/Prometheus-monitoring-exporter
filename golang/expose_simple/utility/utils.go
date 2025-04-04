package utility

import (
	"fmt"
	"strconv"
)

func String_to_float_giga(float_value uint64) float64 {
	ram_total := fmt.Sprintf("%.2f", float64(float_value)/1024/1024/1024)
	ram_total_type_float, err := strconv.ParseFloat(ram_total, 64)

	if err != nil {
		return -1
	}

	return ram_total_type_float
}
