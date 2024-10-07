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
import datetime
import json
import argparse
from threading import Thread
import logging
import socket
from config.log_config import create_log
import subprocess

# logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

# Initialize & Inject with only one instance
logging = create_log()


hitl_server_health_status = Enum("hitl_server_health_status", "PSQL connection health", states=["healthy", "unhealthy"])
# kafka_broker_health_status = Enum("kafka_broker_health_status", "Kafka connection health", states=["green","yellow","red"])
hitl_server_health_request_time = Histogram('hitl_server_health_request_time', 'Server connection response time (seconds)')

kafka_brokers_gauge = Gauge("kafka_brokers", "the number of kafka brokers")

''' gauge with dict type'''
es_nodes_gauge_g = Gauge("es_health_metric", 'Metrics scraped from localhost', ["server_job"])
kafka_nodes_gauge_g = Gauge("kafka_health_metric", 'Metrics scraped from localhost', ["server_job"])
kibana_instance_gauge_g = Gauge("kibana_health_metric", 'Metrics scraped from localhost', ["server_job"])
logstash_instance_gauge_g = Gauge("logstash_health_metric", 'Metrics scraped from localhost', ["server_job"])


class ProcessHandler():
    ''' Get the process by the processname'''

    def __init__(self) -> None:
        pass

    def isProcessRunning(self, name):
        ''' Get PID with process name'''
        try:
            call = subprocess.check_output("pgrep -f '{}'".format(name), shell=True)
            logging.info("Process IDs - {}".format(call.decode("utf-8")))
            return True
        except subprocess.CalledProcessError:
            return False


def transform_prometheus_txt_to_Json(response):
    ''' transform_prometheus_txt_to_Json '''
    body_list = [body for body in response.text.split("\n") if not "#" in body and len(body)>0]
    
    prometheus_json = {}
    loop = 0
    for x in body_list:
        json_key_pairs = x.split(" ")
        prometheus_json.update({json_key_pairs[0] : json_key_pairs[1]})
            
    # print(json.dumps(prometheus_json, indent=2))

    return prometheus_json


def get_server_health(host):

    with hitl_server_health_request_time.time():
        resp = requests.get(url="http://{}:9999".format(host))
    
    # print(resp.status_code)
            
    if not (resp.status_code == 200):
        hitl_server_health_status.state("unhealthy")
    else:
        hitl_server_health_status.state("healthy")


def get_metrics_all_envs(host, urls):
    ''' get metrics from custom export for the health of kafka cluster'''
    
    def get_Process_Id():
        process_name = "/logstash-"
        process_handler = ProcessHandler()
        logging.info("Prcess - {}".format(process_handler.isProcessRunning(process_name)))
        if process_handler.isProcessRunning(process_name):
            return 1
        return 0
    
    # logging.info("Test")
    with hitl_server_health_request_time.time():
        resp = requests.get(url=urls)
    
    logging.info(resp.status_code)
            
    if not (resp.status_code == 200):
        logging.info("NONOI")
        # kafka_brokers.set(int(response['kafka_brokers']))
    else:
        logging.info(resp)
        logging.info(resp.json())

        ''' response '''
        ''' {'kafka_url': {'localhost:9092': 'OK', 'GREEN_CNT': 3, 'localhost:9092': 'OK', 'localhost:9092': 'OK'}, 'es_url': {'localhost:9200': 'OK', 'GREEN_CNT': 4, 'localhost:9200': 'OK', 'localhost:9200': 'OK', 'localhost:9200': 'OK'}} '''

        ''' kafka_brokers_gauge.set(int(resp.json()["kafka_url"]["GREEN_CNT"])) '''
        '''es_nodes_localhost.set(int(resp.json()["es_url"]["GREEN_CNT"]))'''

        kafka_nodes_gauge_g.labels(socket.gethostname()).set(int(resp.json()["kafka_url"]["GREEN_CNT"]))
        es_nodes_gauge_g.labels(socket.gethostname()).set(int(resp.json()["es_url"]["GREEN_CNT"]))
        kibana_instance_gauge_g.labels(socket.gethostname()).set(int(resp.json()["kibana_url"]["GREEN_CNT"]))
        # logstash_instance_gauge_g.labels(socket.gethostname()).set(int(resp.json()["logstash_url"]))
        # -- local instance based
        logstash_instance_gauge_g.labels(socket.gethostname()).set(int(get_Process_Id()))
        
                        

def work(port, interval, host, urls):
    ''' Threading work'''
    '''
    # capture for HTTP URL for the status (example)
    cmd="curl -s lcoalhost/json/ "
    json=`$cmd | jq . > $test.json`
    activeApps=`jq .activeapps[]  $test.json `
    currentApp=`echo $activeApps  | jq 'select(.name=="tstaApp")' >  $test.json`
    currentAppStatus=`jq '.name  + " with Id " + .id + " is  " + .state' $test.json`
    echo $currentAppStatus

    # capture for the process (example)
    pid=`ps ax | grep -i 'logstash' | grep -v grep | awk '{print $1}'`
    if [ -n "$pid" ]
        then
        echo "logstash is Running as PID: $pid"
    else
        echo "logstash is not Running"
    fi
    '''
    try:
        start_http_server(int(port))
        print(f"Prometheus Exporter Server started..")

        while True:
            urls = urls.format(host)
            logging.info(urls)
            get_server_health(host)
            get_metrics_all_envs(host, urls)
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

    except KeyboardInterrupt:
        logging.info("#Interrupted..")
    
    start_http_server(int(port))
    print(f"Prometheus Exporter Server started..")



if __name__ == '__main__':
    '''
    ./es-service-all-client-export.sh status/stop/start
    python ./promethues_client_export.py
    python ./prometheus_client_export.py --host localhost --url "http://localhost:9999/health?kafka_url=localhost:29092,localhost:39092,localhost:49092&es_url=localhost:9200,localhost:9501,localhost:9503"
    '''
    parser = argparse.ArgumentParser(description="Script that might allow us to use it as an application of custom prometheus exporter")
    parser.add_argument('-t','--host', dest='host', default="localhost", help='Server host')
    parser.add_argument('-u', '--url', dest='url', default="http://{}:9999/health?kafka_url=localhost:29092,localhost:39092,localhost:49092&es_url=localhost:9200,localhost:9501,localhost:9503", help='Server URL')
    parser.add_argument('-p', '--port', dest='port', default=9115, help='Expose Port')
    parser.add_argument('-i', '--interval', dest='interval', default=5, help='Interval')
    args = parser.parse_args()

    if args.host:
        host = args.host

    if args.url:
        url = args.url

    if args.port:
        port = args.port

    if args.interval:
        interval = args.interval

    work(int(port), int(interval), host, url)
    '''
    T = []
    try:
        for host in ['localhost', 'localhost1']:
            th1 = Thread(target=work, args=(int(port), int(interval), host, url))
            th1.daemon = True
            th1.start()
            T.append(th1)
            # th1.join()
        [t.join() for t in T] # wait for all threads to terminate
    except (KeyboardInterrupt, SystemExit):
        logging.info("#Interrupted..")
    '''
    
   