package main

import (
	"fmt"
	"log"
	"net"
	"os"
	"os/exec"
	"sync"
)

/* get commands */
func get_commands(input string) string {

	// cmd := exec.Command("echo", "Hello, Go!")
	cmd := exec.Command(input)

	output, err := cmd.Output()

	if err != nil {
		fmt.Println("Error:", err)
		return err.Error()
	}

	// fmt.Println(string(output))
	return string(output)
}

/*
get commands for a list of directory using df commnad
To execute the df command with sudo privileges on a specific directory from a Go program, you can use the os/exec package to run a shell command.
*/
func get_commands_df(dir string) string {

	// Construct the command to run df with sudo for the specified directory
	// cmd := exec.Command("sudo", "df", "-h", targetDirectory)
	cmd := exec.Command("df", "-h", dir)

	output, err := cmd.Output()

	if err != nil {
		fmt.Println("Error:", err)
		return err.Error()
	}

	// fmt.Println(string(output))
	return string(output)
}

const (
	CONN_HOST = ""
	CONN_PORT = "1234"
	CONN_TYPE = "tcp"
)

var (
	/* To count the number of connected clients to a Golang socket server, a common approach involves maintaining a counter variable */
	connectedClients      int
	connectedClients_disk int
	/* Declare a global or package-level integer variable, typically protected by a sync.Mutex to ensure thread-safe access in a concurrent environment. */
	mu sync.Mutex
)

// Handles incoming requests.
func handleRequest(conn net.Conn, listen_info string, client_type string) {
	var currentConnected int
	/* Defer is used to ensure that a function call is performed later in a program's execution */
	defer func() {
		mu.Lock()
		if client_type == "disk" {
			connectedClients_disk--
			currentConnected = connectedClients_disk
		} else {
			connectedClients--
			currentConnected = connectedClients
		}

		fmt.Printf("[%s] Client disconnected. Total clients: %d\n", listen_info, currentConnected)
		mu.Unlock()
		conn.Close()
	}()

	// defer conn.Close() // Ensure the connection is closed when the goroutine exits

	mu.Lock()
	if client_type == "disk" {
		connectedClients_disk++
		currentConnected = connectedClients_disk
	} else {
		connectedClients++
		currentConnected = connectedClients
	}
	fmt.Printf("[%s] Client connected. Total clients: %d\n", listen_info, currentConnected)
	mu.Unlock()

	// Make a buffer to hold incoming data.
	buf := make([]byte, 1024)
	// Read the incoming connection into the buffer.
	n, err := conn.Read(buf)
	if err != nil {
		fmt.Printf("[%s] Error reading: %s", listen_info, err)
		return
	}
	message := string(buf[:n])
	log.Printf("[%s] Received from client %s: %s", listen_info, conn.RemoteAddr(), message)

	// Send a response back to person contacting us.
	if client_type == "disk" {
		_, err = conn.Write([]byte(get_commands_df(message)))
	} else {
		// _, err = conn.Write([]byte("message return.."))
		_, err = conn.Write([]byte(get_commands(message)))
	}

	if err != nil {
		fmt.Printf("[%s] Error writing to client: %v\n", listen_info, err)
		return
	}
}

func server_work(conn_type string, listen_info string, client_type string) {
	// Listen for incoming connections.
	// listener, err := net.Listen("tcp", ":8080")
	// l, err := net.Listen(CONN_TYPE, CONN_HOST+":"+CONN_PORT)
	l, err := net.Listen(conn_type, listen_info)
	if err != nil {
		log.Println("Error Server listening:", err.Error())
		os.Exit(1)
	}
	// Close the listener when the application closes.
	defer l.Close()

	log.Println("Server Listening on " + CONN_HOST + ":" + listen_info)
	for {
		// Listen for an incoming connection.
		conn, err := l.Accept()
		if err != nil {
			log.Println("Error accepting connection: ", err.Error())
			// os.Exit(1)
			continue
		}

		log.Printf("New client connected: %s", conn.RemoteAddr())

		// Handle connections in a new goroutine.
		go handleRequest(conn, listen_info, client_type)
	}
}

/*
cliet : Prometheus-monitoring-exporter/socket/client.py
return disk usages from the host to the monitoring app
sudo netstat -nlp | grep :1234
*/
func main() {

	/*
		// Commands Run
		log.Println(get_commands("ls"))
		log.Println(get_commands())
		fmt.Println(get_commands("C://"))
		fmt.Println(get_commands_df("/apps"))
	*/

	/*
		// To create a Go (Golang) socket server that listens on multiple ports,
		// you need to create a separate net.Listener for each port you want to listen on.
		// Each listener will then accept incoming connections on its respective port.
		// You can handle each listener and its connections concurrently using Goroutines.

		ports := []string{"8080", "8081", "8082"} // Define the ports to listen on

		for _, port := range ports {
			go startListener(port) // Start a listener for each port in a new Goroutine
		}
	*/

	/* The server initiates a net.Listen call to establish a listener on a specific network address and port */
	go server_work("tcp", ":1234", "disk")
	/* Server Listen with other port */
	go server_work("tcp", ":1233", "socket")

	// Keep the main Goroutine alive so the listeners continue running
	select {}
}
