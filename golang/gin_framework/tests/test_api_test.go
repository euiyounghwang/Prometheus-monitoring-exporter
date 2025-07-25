package test

import (
	"fmt"
	"io"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/stretchr/testify/assert"
)

/*
go test -v ./tests/test_api_test.go
*/
func Handler(w http.ResponseWriter, r *http.Request) {
	w.Header().Add("tracing-id", r.Header.Get("tracing-id"))
	// w.WriteHeader(401)
	w.WriteHeader(http.StatusOK)
	w.Header().Set("Content-Type", "application/json")

	io.WriteString(w, `{"message": "hello world!"}`)
}

func Test_default_endpoint_Handler(t *testing.T) {
	// Create a request to pass to our handler. We don't have any query parameters for now, so we'll
	rr := httptest.NewRecorder()

	req := httptest.NewRequest("GET", "/", nil)
	req.Header.Add("tracing-id", "123")

	Handler(rr, req)

	fmt.Println(req)
	fmt.Println(rr)

	if rr.Result().StatusCode != 200 {
		t.Errorf("Status code returned, %d, did not match expected code %d", rr.Result().StatusCode, 401)
	}
	if rr.Result().Header.Get("tracing-id") != "123" {
		t.Errorf("Header value for `tracing-id`, %s, did not match expected value %s", rr.Result().Header.Get("tracing-id"), "123")
	}

	// Check the response body is what we expect.
	expected := `{"message": "hello world!"}`
	assert.Equal(t, rr.Body.String(), expected)

}
