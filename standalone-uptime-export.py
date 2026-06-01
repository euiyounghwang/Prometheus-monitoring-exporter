import os
import requests
import time
from flask import Flask, render_template
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
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import logging
import warnings
import sys
from elasticsearch import Elasticsearch
import threading
warnings.filterwarnings("ignore")

# Create a global lock object
lock = threading.Lock()


''' pip install python-dotenv'''
load_dotenv() # will search for .env file in local folder and load variables 


# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    # format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    format='[%(asctime)s] [%(levelname)s] [%(module)s] [%(funcName)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)



app = Flask(__name__)

@app.route('/')
def hello():
    # labels = ['January', 'February', 'March', 'April', 'May', 'June']
    # data = [0, 10, 15, 8, 22, 18, 25]
    # return render_template('./chartjs-example.html', labels=labels, data=data)
    return render_template('./uptime.html', host_name=socket.gethostname().split(".")[0], linked_port=port)
    
    # return "Hello"


class Util:

    def __init__(self):
        pass
                
    @staticmethod
    def get_json_load(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data
    
    @staticmethod
    def get_datetime():
        return datetime.datetime.now(tz=pytz.timezone('US/Eastern'))
    

''' Create exporter'''
uptime_export_usage_gauge_g = Gauge("uptime_elapsed_response_time_metrics", 'Response time (seconds)', ["server_job", "env", "service_name", "url", "status_code"])
uptime_service_health_gauge_g = Gauge("uptime_service_health_metrics", 'Service health check (1: Green, 2: Yellow, 3 : Red)', ["server_job", "env", "service_name"])
cpu_gauge_g = Gauge("uptime_cpu_usage_metrics", 'Elasticsearch CPU Usage', ["server_job", "env", "service_name"])
jvm_gauge_g = Gauge("uptime_jvm_usage_metrics", 'Elasticsearch JVM Usage', ["server_job", "env", "service_name"])

# Nodes CPU/Memory/Resource Metrics
cpu_cores_logical_metrics = Gauge("cpu_cores_logical_metrics", 'CPU Cores Logical', ["server_job", "env", "service_name"])
cpu_cores_physical_metrics = Gauge("cpu_cores_physical_metrics", 'CPU Cores Physical', ["server_job", "env", "service_name"])
cpu_usage_percent_metrics = Gauge("cpu_usage_percent_metrics", 'CPU Usage Percent', ["server_job", "env", "service_name"])
ram_usage_percent_metrics = Gauge("ram_usage_percent_metrics", 'RAM Usage Percent', ["server_job", "env", "service_name"])
total_memory_metrics = Gauge("total_memory_metrics", 'Total RAM (GB)', ["server_job", "env", "service_name"])
        
   
class Prometheus_Service_Export:

    def __init__(self, loaded_config_json):
        self.service_json = loaded_config_json
        
    
    def get_header(self, basic_auth):
        """
        :param basic_auth: encoded basic auth value (i.e base64encoded(user:pass))
        """
        header =  {
            'Content-type': 'application/json', 
            # 'Authorization' : 'Basic {}'.format(os.environ.get('BASIC_AUTH', '')),
            'Authorization' : 'Basic {}'.format(basic_auth),
            'Connection': 'close'
        }
            
        return header

    
    def service_health_check(self, health_chk, service_json):
        ''' health '''
        '''
        service_health_value = 1 --> Green 
        service_health_value = 2 --> Yellow
        service_health_value = 3 --> Red
        '''
        service_health_value = -1
        if all(health_chk):
            service_health_value = 1
        elif any(health_chk):
            service_health_value = 2
        else:
            service_health_value = 3

        # lock.acquire()
        uptime_service_health_gauge_g.labels(
                        server_job=socket.gethostname(), 
                        env=self.service_json.get("env"), 
                        service_name="{}_{}".format(self.service_json.get("env"), service_json.get("service_name"))
                        )\
                    .set(service_health_value)
        # lock.release()

    # // set
	# // lscpu
	# // grep -c processor /proc/cpuinfo
	# // free -g
	# // df -kH /apps
    def service_uptime(self):
        logging.info(f"service_json loading : {json.dumps(self.service_json, indent=2)}")
        for service_json in self.service_json.get("service"):
            service_list = service_json.get("service").split(",")
            health_chk = []
            for idx, service_url in enumerate(service_list):
            # for idx, service_url in range(1):    
                try:
                  
                    StartTime = time.perf_counter()

                    if service_json.get("service_client").lower() == 'es':
                        logging.info(f"{service_url} Request")
                        logging.info(f"service_list : {service_list}")
                        
                        es_client = Elasticsearch(hosts="{}".format(service_url), headers=self.get_header(service_json.get("basic_auth")), timeout=5, verify_certs=False)

                        if not es_client.ping():
                            status_code = 500
                            health_chk.append(False)
                            continue

                        status_code = 200
                        # health_chk.append(True)
                    
                        """
                        # Execute an operation (e.g., a search query)
                        # You can also set a request_timeout for individual requests
                        response = es_client.search(
                                index=os.getenv("es_index_name"),
                                body={"query": {"match_all": {}}},
                                request_timeout=10 # example of request-specific timeout
                        )

                        # Get Elasticsearch's internal "took" time from the response
                        # This measures server-side execution time
                        server_took_time = response['took']
                        logging.info(f"Server-side 'took' time: {server_took_time} milliseconds")
                        """
                            
                        node_stats = es_client.nodes.stats()
                        # logging.info(f"node_stats: {json.dumps(node_stats, indent=4)}")
                        # Access specific stats, for example, total number of successful nodes
                        successful_nodes = node_stats['_nodes']['successful']
                        logging.info(f"Successfully retrieved stats from {successful_nodes} nodes.")

                        EndTime = time.perf_counter()

                        # response_time = str((EndTime - StartTime).seconds) + '.' + str((EndTime - StartTime).microseconds).zfill(6)[:2]
                        response_time = EndTime - StartTime
                        # logging.info(f"[{service_json.get('service_client')}][{service_url} Request completed in {response_time:.4f} seconds")

                        for node_name in node_stats.get("nodes").keys():
                            logging.info(f"node name : {node_stats.get('nodes').get(node_name).get('name')}")

                            if node_stats.get('nodes').get(node_name).get('indices').get('search').get('query_total') > 0:
                                response_time = (float(node_stats.get('nodes').get(node_name).get('indices').get('search').get('query_time_in_millis'))  
                                                    / (node_stats.get('nodes').get(node_name).get('indices').get('search').get('query_total')))
                            # convert to seconds
                            response_time = float(response_time/1000.0)

                            logging.info(f"[{service_json.get('service_client')}][{service_url} Request completed in {response_time:.4f} seconds")

                            ''' response time'''
                            # lock.acquire()
                            uptime_export_usage_gauge_g.labels(
                                server_job=socket.gethostname(), 
                                env=self.service_json.get("env"), 
                                service_name="{}_{}".format(self.service_json.get("env"), node_stats.get('nodes').get(node_name).get('name')), 
                                url=service_url,
                                # status_code=str(resp.status_code)
                                status_code=str(status_code)
                                )\
                            .set(response_time)

                            cpu_gauge_g.labels(
                                server_job=socket.gethostname(), 
                                env=self.service_json.get("env"), 
                                service_name="{}_{}".format(self.service_json.get("env"), node_stats.get('nodes').get(node_name).get('name'))
                            ).set(node_stats.get('nodes').get(node_name).get('process').get('cpu').get('percent')) 
                            # .set(node_stats.get('nodes').get(node_name).get('os').get('cpu').get('percent')) 

                            jvm_gauge_g.labels(
                                server_job=socket.gethostname(), 
                                env=self.service_json.get("env"), 
                                service_name="{}_{}".format(self.service_json.get("env"), node_stats.get('nodes').get(node_name).get('name'))
                            ).set(node_stats.get('nodes').get(node_name).get('jvm').get('mem').get('heap_used_percent')) 

                            status = es_client.cluster.health()['status']
                            if status == 'green':
                                print("The cluster is healthy and fully operational (all primary and replica shards are assigned).")
                                service_health_value = 1
                            elif status == 'yellow':
                                print("The cluster is partially functional (all primary shards are assigned, but some replicas are not).")
                                service_health_value = 2
                            elif status == 'red':
                                print("The cluster is in a critical state (one or more primary shards are unassigned). Some data may be unavailable.")
                                service_health_value = 3
                            else:
                                print(f"Unknown cluster status: {status}")
                                service_health_value = 3
    
                            uptime_service_health_gauge_g.labels(
                            server_job=socket.gethostname(), 
                            env=self.service_json.get("env"), 
                            service_name="{}_{}".format(self.service_json.get("env"), node_stats.get('nodes').get(node_name).get('name'))
                            )\
                            .set(service_health_value)
                            
                        break
   

                    elif service_json.get("service_client").lower() == 'http':

                        # -- make a call to cluster for checking the disk space on all nodes in the cluster
                        # s = requests.Session()
                        resp = requests.get(url="{}".format(service_url), headers=self.get_header(service_json.get("basic_auth")), verify=False, timeout=5)
                        
                        # if not (resp.status_code == 200):
                        #     return None
                            
                        response_time = resp.elapsed.total_seconds()
                                        
                        logging.info(f"[{service_json.get('service_client')}][{service_url} Request completed in {response_time:.4f} seconds")

                        status_code = resp.status_code

                        health_chk.append(True)

                        ''' response time'''
                        # lock.acquire()
                        uptime_export_usage_gauge_g.labels(
                            server_job=socket.gethostname(), 
                            env=self.service_json.get("env"), 
                            service_name="{}_{}_#{}".format(self.service_json.get("env"), service_json.get("service_name"), idx+1), 
                            url=service_url,
                            # status_code=str(resp.status_code)
                            status_code=str(status_code)
                            )\
                        .set(response_time)

                    elif service_json.get("service_client").lower() == 'json':

                        # -- make a call to cluster for checking the disk space on all nodes in the cluster
                        # s = requests.Session()
                        resp = requests.get(url="{}".format(service_url), headers=self.get_header(service_json.get("basic_auth")), verify=False, timeout=5)
                        
                        # if not (resp.status_code == 200):
                        #     return None
                            
                        response_time = resp.elapsed.total_seconds()
                                        
                        logging.info(f"[{service_json.get('service_client')}][{service_url} Request completed in {response_time:.4f} seconds")
                        logging.info(f"JSON Request : {resp.json()}")

                        if service_json.get('service_name') == 'Data Transfer Nodes Resource':
                            '''
                            {
                                "app": "server_metrics.py",
                                "metrics": [
                                    {
                                        "message": "server_metrics.py",
                                        "tracking": {
                                            "cpu_cores_logical": 12,
                                            "cpu_cores_physical": 10,
                                            "cpu_usage_percent": 28.8,
                                            "ram_usage_percent": 81.7,
                                            "total_memory": "31.64 GB"
                                        }
                                    }
                                ],
                                "started_time": "Mon, 01 Jun 2026 12:08:33 GMT"
                                }
                            '''
                            logging.info("Resource Collecting..")
                            cpu_cores_logical_metrics.labels(
                                server_job=socket.gethostname(), 
                                env=self.service_json.get("env"), 
                                service_name="{}_{}_#{}".format(self.service_json.get("env"), service_json.get("service_name"), idx+1)
                            )\
                            .set(resp.json().get("metrics")[0].get("tracking").get("cpu_cores_logical"))

                            cpu_cores_physical_metrics.labels(
                                server_job=socket.gethostname(), 
                                env=self.service_json.get("env"), 
                                service_name="{}_{}_#{}".format(self.service_json.get("env"), service_json.get("service_name"), idx+1)
                            )\
                            .set(resp.json().get("metrics")[0].get("tracking").get("cpu_cores_physical"))

                            cpu_usage_percent_metrics.labels(
                                server_job=socket.gethostname(), 
                                env=self.service_json.get("env"), 
                                service_name="{}_{}_#{}".format(self.service_json.get("env"), service_json.get("service_name"), idx+1)
                            )\
                            .set(resp.json().get("metrics")[0].get("tracking").get("cpu_usage_percent"))

                            ram_usage_percent_metrics.labels(
                                server_job=socket.gethostname(), 
                                env=self.service_json.get("env"), 
                                service_name="{}_{}_#{}".format(self.service_json.get("env"), service_json.get("service_name"), idx+1)
                            )\
                            .set(resp.json().get("metrics")[0].get("tracking").get("ram_usage_percent"))

                            total_memory_metrics.labels(
                                server_job=socket.gethostname(), 
                                env=self.service_json.get("env"), 
                                service_name="{}_{}_#{}".format(self.service_json.get("env"), service_json.get("service_name"), idx+1)
                            )\
                            .set(resp.json().get("metrics")[0].get("tracking").get("total_memory_gb"))

                except Exception as e:
                    logging.error(e)
                    health_chk.append(False)
                    ''' initialize '''
                    cpu_gauge_g.clear()
                    jvm_gauge_g.clear()
                    pass
                                        
                time.sleep(1) # Wait a second between checks

            if not service_json.get("service_client").lower() == 'es':
                ''' Set service health check'''
                self.service_health_check(health_chk, service_json)


def work(interval, config_each_json):
    ''' main logic'''

    ''' initialize '''
    uptime_service_health_gauge_g.clear()
    # cpu_gauge_g.clear()
    # jvm_gauge_g.clear()

    generated_exporter = Prometheus_Service_Export(config_each_json)

    while True:
        try:
            ''' Performing'''
            generated_exporter.service_uptime()

        except (KeyboardInterrupt, SystemExit):
            logging.info("#Interrupted..")
        except Exception as e:
            logging.error(e)
        
        time.sleep(interval)


if __name__ == '__main__':
    '''
    python standalone-uptime-export.py
    '''
    parser = argparse.ArgumentParser(description="Script that might allow us to get the response time fromm the service on prometheus exporter")
    parser.add_argument('--port', dest='port', default=5001, help='Expose Port')
    parser.add_argument('--interval', dest='interval', default=30, help='Thread Interval')
    args = parser.parse_args()
    
    if args.port:
        port = args.port

    if args.interval:
        interval = args.interval

    logging.info("Standalone Prometheus Exporter Server Started..! [{}]".format(Util.get_datetime()))
    
    try:
        T = []

        ''' Prometehus start server '''
        ''' *** '''
        start_http_server(int(port))
        ''' *** '''

        for config_each_json in Util.get_json_load("./standalone-uptime-config.json"):
            main_th = Thread(target=work, args=(interval, config_each_json))
            main_th.daemon = True
            main_th.start()
            T.append(main_th)
            
                
        ''' Expose this app to acesss index.html (./templates/index.html)'''
        ''' Flask at first run: Do not use the development server in a production environment '''
        ''' For deploying an application to production, one option is to use Waitress, a production WSGI server. '''
        # app.run(host="0.0.0.0", port=int(port)-4000)
        from waitress import serve
        _flask_port = port+1
        serve(app, host="0.0.0.0", port=_flask_port)
        logging.info(f"# Flask App's Port : {_flask_port}")

        # wait for all threads to terminate
        for t in T:
            while t.is_alive():
                t.join(0.5)

    except (KeyboardInterrupt, SystemExit):
        logging.info("# Interrupted..")

    finally:
        logging.info("Standalone Prometheus Exporter Server exited..!")
    
    