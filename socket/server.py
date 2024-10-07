import socket
import json
import subprocess
import logging

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

''' get ProcessID'''
def get_command_output(path):
    ''' Get PID with process name'''
    try:
        call = subprocess.check_output("df -h {}".format(path), shell=True)
        response = call.decode("utf-8")
        # print(response)
        return response
    except subprocess.CalledProcessError:
        pass


def server_listen():
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind(("0.0.0.0", 1234))
    serversocket.listen(5) # become a server socket, maximum 5 connections

    logging.info("Wating a session..")


    while True:
        logging.info("Waiting for connection")
        connection, client = serversocket.accept()
        
        try:
            
            print("Connected to client IP: {}".format(client))
                
            # Receive and print data 1024 bytes at a time, as long as the client is sending something
            while True:
                data = connection.recv(1024)
                logging.info("Received data: {}".format(data))

                ''' get df -h /apps/ '''
            
                if not data:
                    break

                ''' send output'''
                connection.send(get_command_output(data))

        except Exception as e:
            logging.info("# Interrupted..")

        finally:
            connection.close()



if __name__ == "__main__":
    try:
        server_listen()
        
    except Exception as e:
        logging.error(e)
        logging.info("# Interrupted..")
