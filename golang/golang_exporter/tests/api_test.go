package tests

import (
	"fmt"
	"net/http/httptest"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestHealthCheckHandler(t *testing.T) {
	// Create a request to pass to our handler. We don't have any query parameters for now, so we'll
	// pass 'nil' as the third parameter.
	// req, err := http.NewRequest("GET", "/", nil)
	// if err != nil {
	//     t.Fatal(err)
	// }
	rr := httptest.NewRecorder()
	req := httptest.NewRequest("GET", "/metrics", nil)

	fmt.Println(req)
	fmt.Println(rr)

	// expected := `{"alive": true}`
	assert.Equal(t, rr.Result().StatusCode, 200)

}
