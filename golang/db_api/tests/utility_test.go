package tests

import (
	"fmt"
	"testing"

	utility "db.com/m/utils"
	"github.com/stretchr/testify/assert"
)

func Test_PrettyJSon(t *testing.T) {
	query := `{"track_total_hits" : true,"query": {"match_all" : {}},"size": 2}`

	var transformed_query_string string = utility.PrettyString(query)
	fmt.Println(query)
	var expected_query string = `{
		"track_total_hits": true,
		"query": {
			"match_all": {}
		},
		"size": 2
	}`
	// assert.Equal(t, transformed_query_string, strings.Replace(expected_query, "\t\t", " ", -1))
	expected_query = utility.ReplaceStr(expected_query)
	transformed_query_string = utility.ReplaceStr(transformed_query_string)

	// fmt.Println(expected_query)
	assert.Equal(t, transformed_query_string, expected_query)
}

func Test_Round_Float(t *testing.T) {
	// assert := assert.New(t)

	expected_round_float := 90.567
	assert.Equal(t, utility.RoundFloat(90.56666, 3), expected_round_float)

	expected_round_float = -12
	assert.Equal(t, utility.RoundFloat(-12.3456789, 0), expected_round_float)

	expected_round_float = -12.3
	assert.Equal(t, utility.RoundFloat(-12.3456789, 1), expected_round_float)

	expected_round_float = -12.3456789
	assert.Equal(t, utility.RoundFloat(-12.3456789, 10), expected_round_float)
}

func Test_Build_split_string_array(t *testing.T) {
	input_value := "111,222"
	expected_value := `"111","222"`
	assert.Equal(t, utility.Build_split_string_array(input_value), expected_value)

	input_value = "111, 222"
	expected_value = `"111","222"`
	assert.Equal(t, utility.Build_split_string_array(input_value), expected_value)
}

func Test_Build_transform_strings_array_to_html(t *testing.T) {
	// var strs = []string{"test1", "test2"}
	strs := []string{"test1", "test2"}
	expected_value := "test1<BR/>test2<BR/>"
	assert.Equal(t, utility.Transform_strings_array_to_html(strs, true), expected_value)

	expected_value = "test1test2"
	assert.Equal(t, utility.Transform_strings_array_to_html(strs, false), expected_value)
}
