import socket
import os, sys
from _thread import *
import threading
# sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), './'))

# from config.log_config import create_log
from dotenv import load_dotenv
import binascii
import subprocess
import logging

load_dotenv()


# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# logger = create_log()
lock = threading.Lock()
logger = logging.getLogger("socket-log")

class SocketManager(object):
    def __init__(self):
        self.is_client = True
        self.socket_client_list = []
        self.socket_emulator_list = []
        
    def add(self, client, is_client):
        lock.acquire()
        if is_client == True:
            self.socket_client_list.append(client)
            logger.warning(f'socket client size : { len(self.socket_client_list)}')
        else:
            self.socket_emulator_list.append(client)
            logger.warning(f'socket emulator size : { len(self.socket_emulator_list)}')
        lock.release()
        
    def remove(self, client, is_client):
        lock.acquire()
        if is_client == True:
            self.socket_client_list.remove(client)
            logger.warning(f'socket client size : { len(self.socket_client_list)}')
        else:
            self.socket_emulator_list.remove(client)
            logger.warning(f'socket emulator size : { len(self.socket_emulator_list)}')
        lock.release()
        


def threaded_client(connection, my_socket, is_client_type):
    try:
        connection.sendall(str.encode('Welcome to the Servern'))
        
        while True:
            data = connection.recv(1024)
            if not data or data == 'q':
                break

            data = data.decode('utf-8')
            logger.info("Received data: {}".format(data))
            
            '''
            reply = 'Server Says: ' + data.decode('utf-8')
            # logger.info(f'sending..')
            connection.sendall(str.encode(reply))
            '''

            ''' if client is connected to get the info of disk space'''
            if is_client_type:
                ''' send output'''
                connection.send(get_command_output(data).encode('utf-8'))
            else:
                ''' send output'''
                connection.send("Reply".encode('utf-8'))
            
            '''
            # common socket client send..
            if len(my_socket.socket_client_list) > 0:
                for _client in my_socket.socket_client_list:
                    _client.sendall(str.encode(reply))
            '''
        
    finally:
        # with clients_lock:
        my_socket.remove(connection, is_client_type)
        connection.close()


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


def server_socket_start(my_socket, _port, service_client):
    ''' service_client : client or emulator '''
    
    ServerSocket = socket.socket()
    ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
    ServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1);
    ServerSocket.settimeout(100000)
    
    # host = '0.0.0.0'  (Docker Container: 0.0.0.0, local test : 127.0.0.1)
    host = os.getenv("HOST", "127.0.0.1")
    port = _port
    ThreadCount = 0
    # clients_lock = threading.Lock()

    try:
        ServerSocket.bind((host, port))
    except socket.error as e:
        print(str(e))

    logger.info(f'[{_port}] Waitiing for a Connection..')
    ServerSocket.listen(-1)
    
    try:
        while True:
            client, address = ServerSocket.accept()
            is_client_type = 'Client' if service_client else 'Emulator'
            logger.info(f'New connection from: {address[0]} : {str(address[1])}')
            start_new_thread(threaded_client, (client, my_socket, service_client))
            
            # with clients_lock:
            my_socket.add(client, service_client)
            socket_list_cnt = str(len(my_socket.socket_client_list)) if service_client else str(len(my_socket.socket_emulator_list))
            logger.info(f'[{is_client_type}] Number: ' + socket_list_cnt)
                
    except KeyboardInterrupt as e:
        logger.error(e)
        sys.exit()
    finally:
        ServerSocket.close()


if __name__ == '__main__':
    my_socket = SocketManager()
    # server_socket_start(my_socket)
    ''' Server listen to provide the result of command like df-h'''
    worker_client = threading.Thread(target=server_socket_start, args=(my_socket, 1234, True)).start()
    ''' Server listen to provide the result of any tastks '''
    worker_emulator = threading.Thread(target=server_socket_start, args=(my_socket, 1233, False)).start()