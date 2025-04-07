package tests

import (
	"fmt"
	"testing"

	"github.com/stretchr/testify/assert"
	"prometheus.com/utility"
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
