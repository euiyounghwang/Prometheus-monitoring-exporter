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

// GET configuration from the particular env (GET http://localhost:8004/config/get_mail_config_from_env)
type ALERT_Configuration struct {
	MailList       string `json:"mail_list"`
	CcList         string `json:"cc_list"`
	SmsList        string `json:"sms_list"`
	DevMailList    string `json:"dev_mail_list"`
	DevSmsList     string `json:"dev_sms_list"`
	Env            string `json:"env"`
	ThreadInterval int    `json:"thread_interval"`
	IsMailing      bool   `json:"is_mailing"`
	IsSms          bool   `json:"is_sms"`
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
	Message string `json:"message"`
}

type SPARK_APP_Results struct {
	URL     string `json:"url"`
	Workers []struct {
		ID            string `json:"id"`
		Host          string `json:"host"`
		Port          int    `json:"port"`
		Webuiaddress  string `json:"webuiaddress"`
		Cores         int    `json:"cores"`
		Coresused     int    `json:"coresused"`
		Coresfree     int    `json:"coresfree"`
		Memory        int    `json:"memory"`
		Memoryused    int    `json:"memoryused"`
		Memoryfree    int    `json:"memoryfree"`
		State         string `json:"state"`
		Lastheartbeat int64  `json:"lastheartbeat"`
	} `json:"workers"`
	Activeapps []struct {
		Starttime      int64  `json:"starttime"`
		ID             string `json:"id"`
		Name           string `json:"name"`
		User           string `json:"user"`
		Memoryperslave int    `json:"memoryperslave"`
		Submitdate     string `json:"submitdate"`
		State          string `json:"state"`
		Duration       int    `json:"duration"`
	} `json:"activeapps"`
}

/*
Result Struct
*/
type ARG struct {
	ENV_NAME          string `json:"env_name"`
	API_HOST          string `json:"api_host"`
	ALERT_CONF_API    string `json:"alert_conf_api"`
	ES_URL            string `json:"es_url"`
	KIBANA_URL        string `json:"kibana_url"`
	LOGSTASH_URL      string `json:"logstash_url"`
	KAFKA_URL         string `json:"kafka_url"`
	ZOOKEEPER_URL     string `json:"zookeeper_url"`
	KAFKA_CONNECT_URL string `json:"kafka_connect_url"`
	SPARK_URL         string `json:"spark_url"`
	DB_URL            string `json:"db_url"`
	SQL               string `json:"sql"`
}

type SERVER_STATUS struct {
	ES                     string `json:"ES"`
	ES_NODES               int    `json:"ES_NODES"`
	KIBANA                 string `json:"KIBANA"`
	LOGSTASH               string `json:"LOGSTASH"`
	KAFKA                  string `json:"KAFKA"`
	KAFKA_NODES            int    `json:"KAFKA_NODES"`
	ZOOKEEPER              string `json:"ZOOKEEPER"`
	ZOOKEEPER_NODES        int    `json:"ZOOKEEPER_NODES"`
	KAFKA_CONNECT          string `json:"KAFKA_CONNECT"`
	KAFKA_CONNECT_NODES    string `json:"KAFKA_CONNECT_NODES"`
	SPARK                  string `json:"SPARK"`
	SPARK_APP              string `json:"SPARK_APP"`
	SPARK_CUSTOM_APPS      int    `json:"spark_custom_apps"`
	SPARK_CUSTOM_APPS_LIST string `json:"spark_custom_apps_list"`
	SERVER_ACTIVE          string `json:"SERVER_ACTIVE"`
	DATA_PIPELINE          string `json:"DATA_PIPELINE"`
}

type SERVER_ALERT struct {
	ES            string `json:"ES"`
	KIBANA        string `json:"KIBANA"`
	LOGSTASH      string `json:"LOGSTASH"`
	KAFKA         string `json:"KAFKA"`
	SPARK         string `json:"SPARK"`
	SERVER_ACTIVE string `json:"SERVER_ACTIVE"`
	DATA_PIPELINE string `json:"DATA_PIPELINE"`
}
