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
