package utility

import (
	"os"
)

func ReadFile(fileName string) {
	file, _ := os.Open(fileName)
	buffer := make([]byte, 100)
	file.Read(buffer)
	print(string(buffer))

}
