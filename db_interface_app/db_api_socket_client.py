import socket
import json
import os
import dotenv
import logging
import sys


''' pip install python-dotenv'''
# load_dotenv() # will search for .env file in local folder and load variables 
# Reload the variables from your .env file, overriding existing ones
dotenv.load_dotenv(dotenv_path=f"{os.path.abspath(os.getcwd())}/.env", override=True)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    # format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    format='[%(asctime)s] [%(levelname)s] [%(module)s] [%(funcName)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

def make_dict_disk_space(message):

    logging.info("message - ", message)

    if message:
        disk_space_list = [element for element in str(message.split('\n')[1]).split(' ') if len(element) > 0]
        print("disk_space_list - ", disk_space_list)
        
        disk_space_dict = {}
        ''' split#2  disk_space_list - >  ['/dev/mapper/software-Vsfw', '100G', '17G', '84G', '17%', '/apps'] '''
        disk_space_dict.update({
                            "host" : None, 
                            "name" : "supplychain-logging-kafka-node-{}".format(1),
                            "diskTotal" : disk_space_list[1],
                            "diskused" : disk_space_list[2],
                            "diskAvail" : disk_space_list[3],
                            "diskUsedPercent" : disk_space_list[4].replace('%',''),
                            "folder" : disk_space_list[5]
            }
        )
        print(json.dumps(disk_space_dict, indent=2))
     


def receive_buffer(chunks):
    try:
        # Attempt to load the string as a JSON object
        data = json.loads(''.join(chunks))
        # print("## ", data, type(data))
    except (json.JSONDecodeError, TypeError) as e:
        # Catch the specific error raised for invalid JSON or incorrect input types (like None)
        # return False
        data = ''.join(chunks)

    if isinstance(data, (dict, list)):
        print("Json received.. ", json.dumps(data, indent=2), type(data))
    else:
        print("String received.. ", data)
        ''' check disk space and transform into Json'''
        # make_dict_disk_space(received.decode('utf-8'))

def run():
    logging.info("DB Socket clent..")

    # Create a connection to the server application on port 81
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 5044))
    
    try:
        # data = str.encode("/apps/")
        # data = str.encode("c://")
        # data = str.encode("pwd")
        # data = {'msg' : 'Json'}
        data = {"DB_URL" : os.getenv("DB_URL"), "SQL" : os.getenv("SQL")}
        client_socket.sendall(str.encode(json.dumps(data)))

        # Signal that no more data will be sent
        ''' This tells the server that the client has finished sending data, so eventually, conn.recv(1024) on the server will return an empty string, allowing the loop to break.'''
        client_socket.shutdown(socket.SHUT_WR)

        chunks = []

        while True:
            received = client_socket.recv(1024)

            if not received:
                # If recv returns b'', the client has closed the connection
                break
            chunks.append(received.decode('utf-8'))
            # print(f"chunks : {chunks}")

        ''' Json or text'''
        receive_buffer(chunks)      
        
    finally:
        logging.info("Closing socket")
        client_socket.close()

        
if __name__ == '__main__':
    ''' export PYTHONDONTWRITEBYTECODE=1 '''
    ''' Socket client to recevie the recores from DB'''

    try:
        run()
    except KeyboardInterrupt as e:
        logging.error(e)            

