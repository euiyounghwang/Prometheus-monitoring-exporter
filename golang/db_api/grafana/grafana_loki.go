package grafana

import (
	"fmt"

	"db.com/m/api"
	"db.com/m/logging"
)

func Push_alert_loki(api_host string, service string, logging_level string, env string, host string, host_name string, log_filename string, message string) {
	api_endpoint_host := "http://" + api_host + ":8010/log/push_to_loki"
	json_post := map[string]interface{}{
		"service":      service,
		"log_status":   logging_level,
		"env":          env,
		"host":         host,
		"host_name":    host_name,
		"log_filename": log_filename,
		"message":      message,
	}
	body := api.API_Post(api_endpoint_host, json_post)

	if body != nil {
		logging.Info(fmt.Sprintf("* [Push_alert_loki] body: %s", string(body)))
	}

}
