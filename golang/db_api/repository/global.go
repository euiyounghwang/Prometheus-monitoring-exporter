package repository

var (
	Global_local_time string = "America/New_York"

	/* Alert occurs */
	SAVED_THREAD_ALERT = false

	/* Alert Settings */
	ALERT_MAIL_ENABLED, ALERT_SMS_ENABLED = false, false

	/* Push alerts every 1 hour since the services have an issue. */
	PUSH_ALERT_TIME = "1900-01-01 00:00:00"

	/* Push alert interval  since the services have an issue. */
	PUSH_ALERT_INTERVAL_HOUR = 1.0
)
