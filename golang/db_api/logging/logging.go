package logging

import (
	"log"
	"os"
	"time"

	"db.com/m/repository"
)

var (
	WarningLogger *log.Logger
	InfoLogger    *log.Logger
	ErrorLogger   *log.Logger
)

/* https://signoz.io/guides/golang-log/ */
func init() {
	/*
		file, err := os.OpenFile("./logger/logs.txt", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0666)
		if err != nil {
			log.Fatal(err)
		}

		InfoLogger = log.New(file, "INFO: ", log.Ldate|log.Ltime|log.Lshortfile)
		WarningLogger = log.New(file, "WARNING: ", log.Ldate|log.Ltime|log.Lshortfile)
		ErrorLogger = log.New(file, "ERROR: ", log.Ldate|log.Ltime|log.Lshortfile)
	*/

	loc, _ := time.LoadLocation(repository.Global_local_time)
	// handle err
	time.Local = loc // -> this is setting the global timezone

	InfoLogger = log.New(os.Stdout, "INFO: ", log.Ldate|log.Ltime|log.Lshortfile)
	WarningLogger = log.New(os.Stdout, "WARNING: ", log.Ldate|log.Ltime|log.Lshortfile)
	ErrorLogger = log.New(os.Stdout, "ERROR: ", log.Ldate|log.Ltime|log.Lshortfile)
}

func Info(message string) {
	InfoLogger.Println(message)
	// log.Println(message)
}

func Error(message string) {
	ErrorLogger.Println(message)
	/*
		s := fmt.Sprintf("Error : %s", message)
		log.Println(s)
	*/
}

func Warn(message string) {
	WarningLogger.Println(message)
	/*
		s := fmt.Sprintf("Error : %s", message)
		log.Println(s)
	*/
}
