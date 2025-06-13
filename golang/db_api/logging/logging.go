package logging

import (
	"fmt"
	"log"
	"os"
)

var (
	WarningLogger *log.Logger
	InfoLogger    *log.Logger
	ErrorLogger   *log.Logger
)

func init() {
	file, err := os.OpenFile("./logger/logs.txt", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0666)
	if err != nil {
		log.Fatal(err)
	}

	InfoLogger = log.New(file, "INFO: ", log.Ldate|log.Ltime|log.Lshortfile)
	WarningLogger = log.New(file, "WARNING: ", log.Ldate|log.Ltime|log.Lshortfile)
	ErrorLogger = log.New(file, "ERROR: ", log.Ldate|log.Ltime|log.Lshortfile)
}

func Info(message string) {
	InfoLogger.Println(message)
	log.Println(message)
}

func Error(message string) {
	ErrorLogger.Println(message)
	s := fmt.Sprintf("Error : %s", message)
	log.Println(s)
}

func Warn(message string) {
	WarningLogger.Println(message)
	s := fmt.Sprintf("Error : %s", message)
	log.Println(s)
}
