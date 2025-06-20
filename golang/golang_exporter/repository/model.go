package repository

// Struct fields must start with upper case letter (exported) for the JSON package to see their value.
// The "omitempty" option specifies that the field should be omitted from the encoding if the field has an empty value, defined as false, 0, a nil pointer, a nil interface value, and any empty array, slice, map, or string.
// example : https://www.joinc.co.kr/w/man/12/golang/MarshalStructsTheRightWay#google_vignette
type Configuration struct {
	AlertExcludeTime string `json:"alert_exclude_time,omitempty"`
	Test             struct {
		MailList       string `json:"mail_list,omitempty"`
		CcList         string `json:"cc_list,omitempty"`
		SmsList        string `json:"sms_list,omitempty"`
		DevMailList    string `json:"dev_mail_list,omitempty"`
		DevSmsList     string `json:"dev_sms_list,omitempty"`
		Env            string `json:"env,omitempty"`
		ThreadInterval int    `json:"thread_interval,omitempty"`
		IsMailing      bool   `json:"is_mailing,omitempty"`
		IsSms          bool   `json:"is_sms,omitempty"`
	} `json:"test"`
}

// Struct fields must start with upper case letter (exported) for the JSON package to see their value.
type API_Results struct {
	Running_time float32 `json:"running_time"`
	Request_dbid string  `json:"request_dbid"`
	Results      []struct {
		PROCESSNAME string `json:"processname"`
		STATUS      string `json:"status"`
		ADDTS       string `json:"addts"`
		COUNT       int    `json:"count"`
		DBID        string `json:"dbid"`
	} `json:"results"`
}

/*
Result Struct
*/
type ARG struct {
	API_HOST   string `json:"api_host"`
	ES_URL     string `json:"es_url"`
	KIBANA_URL string `json:"kibana_url"`
	KAFKA_URL  string `json:"kafka_url"`
	DB_URL     string `json:"db_url"`
	SQL        string `json:"sql"`
}

type SERVER_STATUS struct {
	ES            string `json:"ES"`
	KIBANA        string `json:"KIBANA"`
	KAFKA         string `json:"KAFKA"`
	SERVER_ACTIVE string `json:"SERVER_ACTIVE"`
	DATA_PIPELINE string `json:"DATA_PIPELINE"`
}

type SERVER_ALERT struct {
	ES            string `json:"ES"`
	KIBANA        string `json:"KIBANA"`
	KAFKA         string `json:"KAFKA"`
	SERVER_ACTIVE string `json:"SERVER_ACTIVE"`
	DATA_PIPELINE string `json:"DATA_PIPELINE"`
}
