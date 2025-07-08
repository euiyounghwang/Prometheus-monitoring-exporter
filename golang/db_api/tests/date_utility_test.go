package tests

import (
	"testing"

	"db.com/m/utils"
	"github.com/stretchr/testify/assert"
)

func Test_two_date_time_differencey(t *testing.T) {
	time_gap := 0.51
	expected_value := 1.000000

	diff_hours := utils.Get_two_date_time_difference("2025-07-08 01:00:00", "2025-07-08 00:00:00")
	assert.Equal(t, diff_hours, expected_value)

	not_processed := true
	if expected_value < time_gap {
		assert.Equal(t, not_processed, true)
	} else {
		assert.Equal(t, !not_processed, false)
	}
}
