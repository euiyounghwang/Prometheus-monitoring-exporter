
import os
from dotenv import load_dotenv
import time
import json
import argparse
import logging
import sys
import datetime, time
import warnings
from ssh_client import utils, work

warnings.filterwarnings("ignore")


''' pip install python-dotenv'''
load_dotenv() # will search for .env file in local folder and load variables 

# Configure basic logging to console with INFO level and a custom format
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    stream=sys.stdout)



if __name__ == '__main__':
    ''' Service checking using the command remotely'''
    parser = argparse.ArgumentParser(description="Script that might allow us to run the commands")
    parser.add_argument('--env', dest='env', default="env", help='env name')
    parser.add_argument('--service', dest='service', default="kibana", help='service name')
    parser.add_argument('--cmd', dest='cmd', default="cmd", help='start/stop')
    args = parser.parse_args()

    if args.env:
        env = args.env

    if args.service:
        service = args.service
            
    if args.cmd:
        cmd = args.cmd

    ''' load ssh_config.json'''
    ssh_config = utils.load_json_config("./ssh_config.json", env)
    logging.info(json.dumps(ssh_config, indent=2))

    ''' multiple services'''
    service_list = service.split(",")
    response_list_dict = []

    try:

        for service in service_list:
            logging.info(f"service : {service}\n")
            ''' call to perform the ssh commands'''
            response = work(ssh_config, service, cmd)
            # logging.info(f"response : {json.dumps(response, indent=2)}\n")
            response_list_dict.append(response)

            ''' Move to the next services to start it if status is 200'''
            if response.get("status") == 200:
                continue
            else:
                break
        logging.info(f"response_list_dict : {json.dumps(response_list_dict, indent=2)}\n")

    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        logging.info(f"** [{env}] Job is being performed..")