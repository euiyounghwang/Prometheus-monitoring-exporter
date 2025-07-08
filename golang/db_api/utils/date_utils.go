package utils

import (
	"log"
	"time"

	"db.com/m/repository"
)

func Get_time_difference(inputTime string) (string, float64) {
	time_gap := 0.51
	// Specific time zone
	nyLocation, _ := time.LoadLocation(repository.Global_local_time)
	currentTime := time.Now().In(nyLocation)
	// currentTime.Format("2006-01-02 15:04:05")
	log.Println("time_difference func - currentTime : ", currentTime)

	// date, error := time.Parse("2006-01-02 00:00:00", rows.ADDTS)
	// s := "2022-03-23T07:00:00+01:00"
	loc, _ := time.LoadLocation(repository.Global_local_time)
	date, error := time.ParseInLocation(time.DateTime, inputTime, loc)

	diff := currentTime.Sub(date)

	if error != nil {
		log.Println(error)
		return "Red", diff.Hours()
	}

	log.Println("time_difference func - inputTime", date)

	log.Printf("Body Json gap_time: %.3fh\n", diff.Hours())
	log.Printf("Body Json gap_time: %.1fmin\n", diff.Minutes())

	if time_gap > diff.Hours() {
		return "Green", diff.Hours()
	} else {
		return "Red", diff.Hours()
	}
}

func Get_two_date_time_difference(startTime string, endTime string) float64 {

	loc, _ := time.LoadLocation(repository.Global_local_time)

	startdate, error := time.ParseInLocation(time.DateTime, startTime, loc)
	enddate, error := time.ParseInLocation(time.DateTime, endTime, loc)

	log.Printf("startdate : %s, enddate : %s", startdate, enddate)

	diff := startdate.Sub(enddate)

	if error != nil {
		log.Println(error)
	}

	log.Printf("Body Json gap_time: %.3fh\n", diff.Hours())
	log.Printf("Body Json gap_time: %.1fmin\n", diff.Minutes())

	return diff.Hours()
}
