
import paramiko
import sys
import argparse
from dotenv import load_dotenv
import logging
import time
import json
import warnings
warnings.filterwarnings("ignore")

''' pip install python-dotenv'''
load_dotenv() # will search for .env file in local folder and load variables 

# Configure basic logging to console with INFO level and a custom format
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    stream=sys.stdout)


def load_json_config(config_path, env):
    try:
        with open(config_path, 'r') as f:
            data = json.loads(f)
            
        return data.get(env)
    except FileNotFoundError:
        logging.error("Error : 'data.json' not found. Please ensure the file exists")
    except json.JSONDecodeError:
        logging.error("Error : Could not decode Json from 'data.json'. Check file format")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        

def get_service_status_client(hostname, username, password, service, cmd):
    # Server details
    # hostname = 'your_server_ip_or_hostname'
    # port = 22
    # username = 'your_username'
    # password = 'your_password' # Or use key-based authentication

    # Create an SSH client object
    ssh_client = paramiko.SSHClient()

    # Set the policy for handling unknown host keys (e.g., automatically add)
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    logging.info(f"** Host: {hostname}, Service : {service}, cmd : {cmd}")

    try:
        # Connect to the server
        ssh_client.connect(hostname=hostname, username=username, password=password)
        
        # Execute a command
        stdin, stdout, stderr = ssh_client.exec_command(cmd)

        """
        # Read and print the output
        print("STDOUT:")
        print(stdout.read().decode('utf-8'))
        print("STDERR:")
        print(stderr.read().decode('utf-8'))
        """
        output = stdout.read().decode('utf-8')
        if output:
            if cmd == "start":
                print(f"\nPID as : {output}")
            else:
                print(f"\n{output}")
            return True
        else:
            logging.error(f"Error : {stderr.read().decode('utf-8')}")
            return False

    except paramiko.AuthenticationException:
        print("Authentication failed. Check your username and password or key.")
    except paramiko.SSHException as e:
        print(f"SSH error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Close the SSH session
        ssh_client.close()
        logging.info(f"Job is running correcty")


def get_service_infos(ssh_config, service):
    ''' lookup the service '''
    if service == "elasticsearch":
        print("f\n")
        logging.info(f"** Service : {service}, Service cmd : {cmd}")
        service = ssh_config.get('es').get("service")
        nodes_list = ssh_config.get('es').get("es_nodes")
        service_lookup_cmd = ssh_config.get('es').get("process_lookup_command")
        service_start_cmd = ssh_config.get('es').get("start_command")
        service_stop_cmd = ssh_config.get('es').get("stop_command")
        
    elif service == "logstash":
        print("f\n")
        logging.info(f"** Service : {service}, Service cmd : {cmd}")
        service = ssh_config.get(service).get("service")
        nodes_list = ssh_config.get(service).get("logstash_nodes")
        service_lookup_cmd = ssh_config.get(service).get("process_lookup_command")
        service_start_cmd = ssh_config.get(service).get("start_command")
        service_stop_cmd = ssh_config.get(service).get("stop_command")
        
    elif service == "kibana":
        print("f\n")
        logging.info(f"** Service : {service}, Service cmd : {cmd}")
        service = ssh_config.get(service).get("service")
        nodes_list = ssh_config.get(service).get("kibana_nodes")
        service_lookup_cmd = ssh_config.get(service).get("process_lookup_command")
        service_start_cmd = ssh_config.get(service).get("start_command")
        service_stop_cmd = ssh_config.get(service).get("stop_command")
        
    return service, nodes_list, service_lookup_cmd, service_start_cmd, service_stop_cmd
   

def work(ssh_config, service, cmd):
    ''' Perform the ssh access to start/stop service via ssh'''  
    command_msg = ''
    
    try:
        
        ''' lookup the service'''
        service, nodes_list, service_lookup_cmd, service_start_cmd, service_stop_cmd = get_service_infos(ssh_config, service)
        
        any_of_service_started, any_of_service_stopped = False, False
        for each_node in nodes_list:
            ALIVE = get_service_status_client(each_node, ssh_config.get("userid"), ssh_config.get("userpw"), service, service_lookup_cmd)
            print(f"\n")
            logging.info(f"** get_service_status_client [{service}] :  {ALIVE}\n")
            
            if ALIVE is None:
                # raise Exception)f"get_service_status_client is {ALIVE}")
                return {
                    "status" :  500,
                    "message" : "get_service_status_client is {}".format(ALIVE)
                }
                
            if ALIVE is not None and not ALIVE and cmd == "start":
                any_of_service_started = True
                logging.info("Trying to start the service..")
                ALIVE = get_service_infos(each_node, ssh_config.get("userid"), ssh_config.get("userpw"), service, service_start_cmd)
                logging.info(f"CMD Status : {ALIVE}")
                
                logging.info("Pausing for 3 seconds")
                time.sleep(3)
                
            elif ALIVE is not None and not ALIVE and cmd == "stop":
                any_of_service_stopped = True
                logging.info(f"Trying to stop the service with command \"{service_stop_cmd}\"")
                ALIVE = get_service_infos(each_node, ssh_config.get("userid"), ssh_config.get("userpw"), service, service_stop_cmd)
                logging.info(f"CMD Status : {ALIVE}")
                
                logging.info("Pausing for 3 seconds")
                time.sleep(3)
        
            else:
                logging.info("Please wait 30 seconds to check the service")
                
        ''' Update a message for the response'''
        if cmd == "start":
            command_msg = "Succeed to execute start commands" if any_of_service_started else "All {} services are active".format(service)
        elif cmd == "stop":
            command_msg = "Succeed to execute stop commands" if any_of_service_started else "All {} services are offline".format(service)
        
        return {
            "status" : 200,
            "message": "{}. {}".format(command_msg, "Please wait 30 seconds to check the service")
        }
        
    except Exception as e:   
        logging.error(f"An error occurred : {e}")
        command_msg = "Failed to execute commands"
        return {
            "status" : 500,
            "message": "{}. {}".format(command_msg, e)
        }
        

if __name__ == '__main__':
    '''
    '''
    parser = argparse.ArgumentParser(description="Script that might allow us to access an instance via ssh")
    parser.add_argument('--env', dest='env', default="env", help='env')
    parser.add_argument('--service', dest='service', default="service", help='service')
    parser.add_argument('--cmd', dest='cmd', default="cmd", help='cmd')
    args = parser.parse_args()
    
    if args.env:
        env = args.env
        
    if args.service:
        service = args.service
        
    if args.cmd:
        cmd = args.cmd
        
    ''' load ssh_config.json'''
    ssh_config = load_json_config("./ssh_config.json", env)
    
    try;
        ''' call to perform the ssh commands'''
        response = work(ssh_config, service, cmd)
        logging.info(f"response : {json.dumps(response, indent=2)}")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        logging.info("** Job is being performed..")

