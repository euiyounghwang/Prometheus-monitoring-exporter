
import paramiko
import logging
import os
from dotenv import load_dotenv
import json

''' pip install python-dotenv'''
load_dotenv() # will search for .env file in local folder and load variables 

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)



disk_space_memory_list= []

def ssh_connection_test(host, username, password, path, host_number):
    try:

        global disk_space_list

        # command = "df"

        # Update the next three lines with your
        # server's information

        client = paramiko.client.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host, username=username, password=password)
        _stdin, _stdout,_stderr = client.exec_command("df -h {}".format(path))
        response = _stdout.read().decode()
        # print("cmd : ", response, type(response))
        # print('split#1 ', str(response.split('\n')[1]))
        disk_space_list = [element for element in str(response.split('\n')[1]).split(' ') if len(element) > 0]
        # print('split#2 ', disk_space_list)
        # logging.info(f"Success : {host}")

        disk_space_dict = {}
        ''' split#2  disk_space_list - >  ['/dev/mapper/software-Vsfw', '100G', '17G', '84G', '17%', '/apps'] '''
        disk_space_dict.update({
                "name" : "supplychain-logging-kafka-node-{}".format(host_number),
                "diskTotal" : disk_space_list[1],
                "diskused" : disk_space_list[2],
                "diskAvail" : disk_space_list[3],
                "diskUsedPercent" : disk_space_list[4],
                "folder" : disk_space_list[5]
            }
        )

        disk_space_memory_list.append(disk_space_dict)        
        
    except Exception as error:
        logging.error(f"Failed : {host}")
    finally:
        client.close()


if __name__ == "__main__":
    
    # print(os.getenv("credentials_id"))
    server_list = ["localhost"]
    loop = 1
    for idx, each_server in enumerate(server_list):
        logging.info(f"{idx+1} : {each_server}")
        ssh_connection_test(str(each_server).strip(), os.getenv("credentials_id"), os.getenv("credentials_pw"), "/apps/", loop)
        loop +=1
    logging.info(f"disk space : {json.dumps(disk_space_memory_list, indent=2)}")
    
