package repository

// Struct fields must start with upper case letter (exported) for the JSON package to see their value.
type Configuration struct {
	AlertExcludeTime string `json:"alert_exclude_time"`
	Test             struct {
		MailList       string `json:"mail_list"`
		CcList         string `json:"cc_list"`
		SmsList        string `json:"sms_list"`
		DevMailList    string `json:"dev_mail_list"`
		DevSmsList     string `json:"dev_sms_list"`
		Env            string `json:"env"`
		ThreadInterval int    `json:"thread_interval"`
		IsMailing      bool   `json:"is_mailing"`
		IsSms          bool   `json:"is_sms"`
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
