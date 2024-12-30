import socket
import json
import subprocess
import logging
# from _thread import *
import threading
import os
import sys

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
                data = data.decode('utf-8')
                logging.info("Received data: {}".format(data))

                ''' get df -h /apps/ '''
            
                if not data:
                    break

                ''' send output'''
                connection.send(get_command_output(data).encode('utf-8'))

        except Exception as e:
            logging.info("# Interrupted..")

        finally:
            connection.close()



lock = threading.Lock()

class SocketManager(object):
    def __init__(self):
        self.is_client = True
        self.socket_client_list = []
        self.socket_emulator_list = []
        
    def add(self, client, is_client):
        lock.acquire()
        self.socket_client_list.append(client)
        logging.info('Add.. socket client size : {}'.format(len(self.socket_client_list)))
        lock.release()
        
    def remove(self, client, is_client):
        lock.acquire()
        self.socket_client_list.remove(client)
        logging.info('Remove.. socket client size : {}'.format(len(self.socket_client_list)))
        lock.release()



def threaded_client(connection, my_socket, is_client_type):
    try:
        # connection.sendall(str.encode('Welcome to the Servern'))
        
        while True:
            data = connection.recv(1024)
            if not data or data == 'q':
                break
            
            logging.info('Server received ... {}'.format(data))
            data = data.decode('utf-8')
            logging.info('response ... {}'.format(get_command_output(data)))

            ''' socket.send is a low-level method It can send less bytes than you requested, but returns the number of bytes sent'''
            ''' socket.sendall is a high-level Python-only method that sends the entire buffer you pass or throws an exception '''
            # connection.sendall(str.encode(reply))
            connection.sendall(get_command_output(data).encode('utf-8'))
            
            # common socket client send..
            # if len(my_socket.socket_client_list) > 0:
            #     for _client in my_socket.socket_client_list:
            #         _client.sendall(str.encode(reply))
        
    finally:
        # with clients_lock:
        my_socket.remove(connection, is_client_type)
        connection.close()


def server_socket_start(my_socket, _port, service_client):
    ''' service_client : client or emulator '''
    
    ServerSocket = socket.socket()
    ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
    ServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1);
    ServerSocket.settimeout(10000000)
    
    
    # host = '0.0.0.0'  (Docker Container: 0.0.0.0, local test : 127.0.0.1)
    host = os.getenv("HOST", "0.0.0.0")
    port = _port
    ThreadCount = 0
    # clients_lock = threading.Lock()

    try:
        ServerSocket.bind((host, port))
    except socket.error as e:
        print(str(e))

    logging.info('[{}] Waitiing for a Connection..'.format(_port))
    ServerSocket.listen(-1)
    
    try:
        while True:
            client, address = ServerSocket.accept()
            logging.info('New connection from: {} : {}'.format(address[0], str(address[1])))
            start_new_thread(threaded_client, (client, my_socket, service_client))
            
            # with clients_lock:
            my_socket.add(client, service_client)
            socket_list_cnt = str(len(my_socket.socket_client_list)) if service_client else str(len(my_socket.socket_emulator_list))
            logging.info('Current socket client size: {}'.format(socket_list_cnt))
                
    except KeyboardInterrupt as e:
        logging.error(e)
        sys.exit()
    finally:
        ServerSocket.close()

if __name__ == "__main__":
    try:
        server_listen()
        '''
        my_socket = SocketManager()
        # server_socket_start(my_socket)
        worker_client = threading.Thread(target=server_socket_start, args=(my_socket, 1234, True)).start()
        '''
        
    except Exception as e:
        logging.error(e)
        logging.info("# Interrupted..")
