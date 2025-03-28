import os
import requests
import time
from prometheus_client import start_http_server, Enum, Histogram, Counter, Summary, Gauge, CollectorRegistry
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from prometheus_client.core import (
    GaugeMetricFamily,
    CounterMetricFamily,
    REGISTRY
)
import datetime, time
import json
import argparse
from threading import Thread
import logging
import socket
from config.log_config import create_log
import subprocess
import json
import copy
import jaydebeapi # type: ignore
import jpype # type: ignore
import re
from collections import defaultdict
# import paramiko
import base64
import pytz
from dotenv import load_dotenv
import warnings
warnings.filterwarnings("ignore")


''' pip install python-dotenv'''
load_dotenv() # will search for .env file in local folder and load variables 


# Initialize & Inject with only one instance
logging = create_log()

''' global variable'''
remote_prometheus_json = {}


def transform_prometheus_txt_to_Json(response):
    ''' transform_prometheus_txt_to_Json '''
    '''  
    {
        "basicMemoryInfoGauge": [
        {
        "label": "ram_available=4794105856,ram_total=33974169600,ram_used=29180063744,ram_used_percent=85.000000,server_job=US-5CD4021CL1-L",
        "set_value": "1"
        }
    ],
    "go_gc_duration_seconds_sum": "0.0031466",
    ..
    }
  '''
    
    remake_prometheus_to_json = {}

    # filter_metrics_names = ['elasticsearch_process_cpu_percent', 'elasticsearch_jvm_memory_used_bytes']
    body_list = [body for body in response.text.split("\n") if not "#" in body and len(body)>0]
    # print(body_list)

    key_tmp_name = ""
    sub_key_list = []
    for idx, x in enumerate(body_list):
        # json_key_pairs = x.replace("}","").split(" ")
        if "}" in x:
            json_key_pairs = x.split("} ")
        else:
            json_key_pairs = x.split(" ")
        # print(json_key_pairs)
        key = json_key_pairs[0]
        value = json_key_pairs[1]
        # print(f"key : {key}, value : {value}")
        if "{" not in key:
            remake_prometheus_to_json.update({key : value})
        else:
            key_name = key.split("{")[0]
            value_name = key.split("{")[1].replace('"','')
            # print(f"key_name : {key_name}, value_name : {value_name}")
            # remake_prometheus_to_json.update({key_name : [{'label' : value_name, 'set_value' : value}]})
            if key_name not in remake_prometheus_to_json:
                sub_key_list = []
                # print(f"## key_name : {key_name}, key_tmp_name : {key_tmp_name}, value_name : {value_name}")
                remake_prometheus_to_json.update({key_name : [{'label' : value_name, 'set_value' : value}]})
                sub_key_list.append({'label' : value_name, 'set_value' : value})
            else:
                # print(f"** key_name : {key_name}, key_tmp_name : {key_tmp_name}, sub_key_list : {sub_key_list}")
                sub_key_list.append({'label' : value_name, 'set_value' : value})
                # print(f"final update: {key_name}, {sub_key_list}")
                remake_prometheus_to_json.update({key_name : sub_key_list})
      
    # logging.info(f"remake_prometheus_to_json  - {json.dumps(remake_prometheus_to_json, indent=2)}")
    return remake_prometheus_to_json
            


def get_exporter_apps():
    ''' get_exporter_apps''' 

    global remote_prometheus_json

    try:
        resp = requests.get(url="http://{}:2112/metrics".format(os.getenv("REMOTE_AGENT_HOST")), timeout=5)
                    
        if not (resp.status_code == 200):
            logging.error(f"get_exporter_apps api do not reachable")
            return
        
        remote_prometheus_json = {}
        remote_prometheus_json = transform_prometheus_txt_to_Json(resp)
        logging.info(f"** {remote_prometheus_json.get('basiccpuModelInfoGauge')}")
            
        
    except Exception as e:
            logging.error(e)
            # pass     


def gather_metrics_export():
    ''' export metrics'''
    global remote_prometheus_json
    try:
        # logging.info(remote_prometheus_json)
        pass

    except Exception as e:
        logging.error(e)


def work(port, interval):
    try:
        start_http_server(int(port))
        logging.info(f"\n\nStandalone Prometheus Exporter Server started..")
   
        StartedTime = datetime.datetime.now()
        while True:
            print(f"\n")
            logging.info(f"Prometheus Exporter Refreshed..")
            StartTime = datetime.datetime.now()

            ''' call fun'''
            ''' get resource from go exporter application'''
            get_exporter_apps()

            ''' Main export func'''
            gather_metrics_export()

            ''' export application processing time '''
            EndTime = datetime.datetime.now()
            Delay_Time = str((EndTime - StartTime).seconds) + '.' + str((EndTime - StartTime).microseconds).zfill(6)[:2]

            logging.info("# StartedTime Application - {}".format(str(StartedTime)))
            logging.info("# Export Application Running Time - {}\n\n".format(str(Delay_Time)))

            time.sleep(interval)
        
        '''
        for each_host in ['localhost', 'localhost']:
            while True:
                urls = urls.format(each_host)
                logging.info(urls)
                get_server_health(each_host)
                get_metrics_all_envs(each_host, urls)
                time.sleep(interval)
        '''

    except (KeyboardInterrupt, SystemExit):
        logging.info("#Interrupted..")
       


if __name__ == '__main__':
    '''
    https://taehyuklee.tistory.com/12 :  AttributeError: module 'resource' has no attribute 'getpagesize'
    '''
    parser = argparse.ArgumentParser(description="Script that might allow us to use it as an application of custom prometheus exporter")
    parser.add_argument('--env_name', dest='env_name', default="env_name", help='env_name')
    parser.add_argument('--port', dest='port', default=2113, help='Expose Port')
    parser.add_argument('--interval', dest='interval', default=30, help='Interval')
    args = parser.parse_args()

    if args.interval:
        interval = args.interval

    if args.port:
        port = args.port

    try:
        T = []
        main_th = Thread(target=work, args=(int(port), int(interval)))
        main_th.daemon = True
        main_th.start()
        T.append(main_th)

        # wait for all threads to terminate
        for t in T:
            while t.is_alive():
                t.join(0.5)

    except (KeyboardInterrupt, SystemExit):
        logging.info("# Interrupted..")
    
    logging.info("Standalone Prometheus Exporter Server exited..!")