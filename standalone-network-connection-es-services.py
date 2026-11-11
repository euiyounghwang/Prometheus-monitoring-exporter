import os
import json

import argparse
from dotenv import load_dotenv
import os
from threading import Thread
import requests
import logging
import warnings
import socket
from elasticsearch import Elasticsearch
import pytz
import time, sys
import socket
from flask import Flask, render_template
from datetime import datetime, timedelta
import pandas as pd
import dotenv

warnings.filterwarnings("ignore")

load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger("Service-Port-Validation-Script")

es_service_infra = {
    "test": {
        "elasticsearch": [
            {"ES_Data_Nodes #1": "localhost:9200"},
            {"ES_Data_Nodes #2": "localhost:9201"},
            {"ES_Data_Nodes #3": "localhost:9202"}
        ],
        "logstash": [
            {"ES_Data_Nodes #2": "localhost:5043,5044,5045,5046,5047,5048"}
        ],
        "kibana": [
            {"ES_Data_Nodes #3": "http://localhost:5601"}
        ],
        "kafka": [
            {"Data_Transfer_Nodes #1": "localhost:9092"},
            {"Data_Transfer_Nodes #2": "localhost:9092"},
            {"Data_Transfer_Nodes #3": "localhost:9092"}
        ],
        "zookeeper": [
            {"Data_Transfer_Nodes #1": "localhost:2181"},
            {"Data_Transfer_Nodes #2": "localhost:2181"},
            {"Data_Transfer_Nodes #3": "localhost:2181"}
        ],
        "kafka_connect": [
            {"Data_Transfer_Nodes #1": "http://localhost:8083"},
            {"Data_Transfer_Nodes #2": "http://localhost:8083"},
            {"Data_Transfer_Nodes #3": "http://localhost:8083"}
        ],
        "spark_cluster": [
            {"Data_Transfer_Nodes #1": "http://localhost:8480"}
        ]
    },
    "test1": {
        "elasticsearch": [
            {"ES_Data_Nodes #1": "localhost:9200"},
            {"ES_Data_Nodes #2": "localhost:9201"},
            {"ES_Data_Nodes #3": "localhost:9202"}
        ],
         "logstash": [
            {"ES_Data_Nodes #2": "localhost:5043,5044,5045,5046,5047,5048"}
        ]
    }
}

es_service_infra_chk = {
    "Source_Host": [],
    "Direction" : [],
    "Env" : [],
    "Target_Host": [],
    "Ports": [],
    "Service": [],
    "Description": [],
    "Access": []
}


def is_port_open(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)  # Stop waiting after 1 second
        return s.connect_ex((host, port)) == 0
    

def get_access_api(env, s_name, info, service_url) -> str:
    logger.info(f"{env} - {s_name} - {info} - {service_url}")

    try:
        response = requests.get(url=service_url, headers=None, verify=False, timeout=10)
        if response.status_code == 200:
            es_service_infra_chk.get("Access").append(True)
            return "Ok"

    except Exception as e:
        logger.error(f"get_access_api : {e}")
        es_service_infra_chk.get("Access").append(False)
        return e

def get_rest_api(service_url) -> str:
    try:
        response = requests.get(url=service_url, headers=None, verify=False, timeout=10)
        if response.status_code == 200:
           return response.json()
        

    except Exception as e:
        logger.error(f"get_access_api : {e}")
        es_service_infra_chk.get("Access").append(False)
        return {"error" : e, "config": ""}



def work() -> None:

    try:
        logger.info(f"Port checking")

        ''' Get a list of ES services Info across all env's'''
        logger.info(f"API URL : {os.getenv('API_URL')}")
        resp = get_rest_api(os.getenv('API_URL'))
        print(f"response.json() : {resp.get('config')}")

        ''' Set k, v into es_service_infra_chk using resp json values'''
        
        for k in es_service_infra.keys():
            for s_name in es_service_infra.get(k).keys():
                for es_nodes_json in es_service_infra.get(k).get(s_name):
                    ''' Check for one of logstash port range'''
                    if s_name not in ["logstash"]:
                        """ Update basic info """
                        es_service_infra_chk.get("Source_Host").append(socket.gethostname().split(".")[0])
                        es_service_infra_chk.get("Direction").append("-->")
                        es_service_infra_chk.get("Env").append(k.upper())
                    
                        es_service_infra_chk.get("Service").append(s_name.capitalize())
                        """"""
                        
                        for info, value in es_nodes_json.items():
                            es_service_infra_chk.get("Ports").append(value.rsplit(":", 1)[-1])
                            
                            ''' http reqeust for testing'''
                            if s_name in ["kibana", "kafka_connect", "spark_cluster"]:
                                es_service_infra_chk.get("Target_Host").append(value.split(":")[1].replace("//", ""))
                                # es_service_infra_chk.get("Ports").append(value.split(":")[2])
                                logger.info(get_access_api(k, s_name, info, value))
                            else:
                                # es_service_infra_chk.get("Ports").append(value.split(":")[1])
                                es_service_infra_chk.get("Target_Host").append(value.split(":")[0].replace("//", ""))
                                ''' Tcp socket for testing'''
                                if is_port_open(value.split(":")[0], int(value.split(":")[1])):
                                    es_service_infra_chk.get("Access").append(True)
                                else:
                                    es_service_infra_chk.get("Access").append(False)

                            es_service_infra_chk.get("Description").append(info)
                    else:
                        ''' Check for one of logstash port range'''
                        tmp_ports, access_one_of_them = [], []
                        for info, value in es_nodes_json.items():
                            str_ports = value.rsplit(":", 1)[-1]
                            # print(str_ports)
                            for each_port in str_ports.split(","):
                                if is_port_open(value.split(":")[0], int(each_port)):
                                    access_one_of_them.append(True)
                                    tmp_ports.append(tmp_ports)
                                    break
                                else:
                                    access_one_of_them.append(False)

                        """ Update basic info """
                        es_service_infra_chk.get("Source_Host").append(socket.gethostname().split(".")[0])
                        es_service_infra_chk.get("Direction").append("-->")
                        es_service_infra_chk.get("Env").append(k.upper())
                        es_service_infra_chk.get("Target_Host").append(value.split(":")[0].replace("//", ""))
                        es_service_infra_chk.get("Ports").append("".join(tmp_ports) or "-")
                        es_service_infra_chk.get("Service").append(s_name.capitalize())
                        es_service_infra_chk.get("Description").append(info)
                        es_service_infra_chk.get("Access").append(any(access_one_of_them))
                        """"""

        print("\n")
        # logger.info(json.dumps(es_service_infra_chk, indent=2))
        print("-"*100)
        print(f"Network Connection Test from {socket.gethostname().split('.')[0]} to all env's")
        print("-"*100)

        print("\n")
        df = pd.DataFrame(es_service_infra_chk)
        print(df)

    # except (KeyboardInterrupt, SystemExit) as e:
    except Exception as e:
        logger.error(f"work func : {e}")
        pass


if __name__ == "__main__":
    """
    Ingnore ssl pip - pip install numpy==1.26.4 --trusted-host pypi.org --trusted-host files.pythonhosted.org
    Running this service allows us to check and delete old ES indices
    python ./standalone-network-connection-es-services.py
    """
    parser = argparse.ArgumentParser(
        description="Running this service allows us to check the service ports using this script"
    )

    global gloabal_default_timezone

    gloabal_default_timezone = pytz.timezone("US/Eastern")

    # --
    # Only One process we can use due to 'Global Interpreter Lock'
    # 'Multiprocessing' is that we can use for running with multiple process
    # --
    try:

        T = []
        th1 = Thread(target=work, args=())
        th1.daemon = True
        th1.start()
        T.append(th1)

        for t in T:
            while t.is_alive():
                t.join(0.5)
        # work(target_server)

    except Exception as e:
        logger.error(e)
