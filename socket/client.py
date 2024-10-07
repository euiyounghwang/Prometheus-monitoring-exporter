import socket
import json


def make_dict_disk_space(message):

    print("message - ", message)

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
     

# Create a connection to the server application on port 81
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('localhost', 1234))
 
try:
    data = str.encode("/apps/")
    client_socket.sendall(data)

    received = client_socket.recv(1024)
    print("received.. ", received)
    make_dict_disk_space(received.decode('utf-8'))
 
finally:
    print("Closing socket")
    client_socket.close()