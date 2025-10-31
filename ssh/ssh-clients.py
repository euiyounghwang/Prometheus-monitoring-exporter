
import paramiko
import sys
import argparse
from dotenv import load_dotenv
import logging
import warnings
warnings.filterwarnings("ignore")

''' pip install python-dotenv'''
load_dotenv() # will search for .env file in local folder and load variables 

# Configure basic logging to console with INFO level and a custom format
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    stream=sys.stdout)


def ssh_client(service, cmd):
    # Server details
    hostname = 'your_server_ip_or_hostname'
    port = 22
    username = 'your_username'
    password = 'your_password' # Or use key-based authentication

    # Create an SSH client object
    ssh_client = paramiko.SSHClient()

    # Set the policy for handling unknown host keys (e.g., automatically add)
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Connect to the server
        ssh_client.connect(hostname=hostname, port=port, username=username, password=password)
        
        # Execute a command
        stdin, stdout, stderr = ssh_client.exec_command(cmd)

        # Read and print the output
        print("STDOUT:")
        print(stdout.read().decode('utf-8'))
        print("STDERR:")
        print(stderr.read().decode('utf-8'))

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


if __name__ == '__main__':
    '''
    '''
    parser = argparse.ArgumentParser(description="Script that might allow us to access an instance via ssh")
    parser.add_argument('--service', dest='service', default="service", help='service')
    parser.add_argument('--cmd', dest='cmd', default="cmd", help='cmd')
    args = parser.parse_args()
    
    if args.service:
        service = args.service
        
    if args.cmd:
        cmd = args.cmd
        
    logging.info(f"Service: {service}, Cmd : {cmd}")

    ''' Call ssh client func'''
    # ssh_client(service, cmd)   
     
    logging.info(f"ssh client is running..")