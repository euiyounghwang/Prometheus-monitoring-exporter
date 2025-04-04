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

''' Prometheus metrics'''
cpu_usage_gauge_g = Gauge("cpu_usage_metric", 'cpu_usage_metric (percent)', ["server_job"])
memory_usage_gauge_g = Gauge("memory_usage_metric", 'memory_usage_metric (percent)', ["server_job"])
memory_total_gauge_g = Gauge("memory_total_metric", 'memory_total_metric (GB)', ["server_job"])
memory_used_gauge_g = Gauge("memory_used_metric", 'memory_used_metric (GB)', ["server_job"])
memory_available_gauge_g = Gauge("memory_available_metric", 'memory_available_metric (GB)', ["server_job"])

nodes_diskspace_gauge_g = Gauge("node_disk_space_metric", 'Metrics scraped from localhost', ["server_job", "category", "host", "diskfree", "disktotal", "diskusagepercent", "diskused", "ipaddress", "path"])

node_agent_status_gauge_g = Gauge("node_agent_status_metric", 'Metrics scraped from localhost', ["server_job"])
all_envs_status_gauge_g = Gauge("all_envs_status_metric", 'Metrics scraped from localhost', ["server_job", "type"])


class monitor:
    def __init__(self):
        self.all_env_status = []

    def get_service_port_alive(self, monitoring_metrics):
        ''' get_service_port_alive'''
        ''' 
        socket.connect_ex( <address> ) similar to the connect() method but returns an error indicator of raising an exception for errors returned by C-level connect() call.
        Other errors like host not found can still raise exception though
        '''
        exclude_port_detect = ['redis', 'configuration', 'loki_custom_promtail_agent_url', 'log_aggregation_agent_url', 'alert_monitoring_url']
        response_dict = {}
        for k, v in monitoring_metrics.items():
            response_dict.update({k : ""})
            response_sub_dict = {}
            url_lists = v.split(",")
            # logging.info("url_lists : {}".format(url_lists))
            totalcount = 0
            for idx, each_host in enumerate(url_lists):
                each_urls = each_host.split(":")
                # logging.info("urls with port : {}".format(each_urls))
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    result = sock.connect_ex((each_urls[0],int(each_urls[1])))
                    if result == 0:
                        # print("Port is open")
                        totalcount +=1
                        response_sub_dict.update({each_urls[0] + ":" + each_urls[1] : "OK"})
                        response_sub_dict.update({"GREEN_CNT" : totalcount})
                    else:
                        # print("Port is not open")
                        response_sub_dict.update({each_urls[0] + ":" + each_urls[1] : "FAIL"})
                        response_sub_dict.update({"GREEN_CNT" : totalcount})
                        ''' save failure node with a reason into saved_failure_dict'''
                        # if 'redis' not in str(k) and 'configuration' not in str(k) and 'loki_custom_promtail_agent_url' not in str(k) and 'log_aggregation_agent_url' not in str(k):
                        if str(k) not in exclude_port_detect:
                            saved_failure_dict.update({each_urls[0] + "_" + str(k).upper() + "_" + str(idx+1): "[Node #{}-{}] ".format(idx+1, str(k).upper()) + each_host + " Port closed"})
                    sock.close()
                except Exception as e:
                    print("Port is not open")
                    response_sub_dict.update({each_urls[0] + ":" + each_urls[1] : "FAIL"})
                    response_sub_dict.update({"GREEN_CNT" : totalcount})
                    ''' save failure node with a reason into saved_failure_dict'''
                    # if 'redis' not in str(k) and 'configuration' not in str(k) and 'loki_custom_promtail_agent_url' not in str(k) and 'log_aggregation_agent_url' not in str(k):
                    if str(k) not in exclude_port_detect:
                        saved_failure_dict.update({each_urls[0] + "_" + str(k).upper() + "_" + str(idx+1): "[Node #{}-{}] ".format(idx+1, str(k).upper()) + each_host + " Port closed"})
                    pass
                 
            response_dict.update({k : response_sub_dict})
            
        logging.info(json.dumps(response_dict, indent=2))
        return response_dict
    
    def set_all_envs_status(self, active_cnt, instance):
            ''' return all_envs_status status'''
            # logging.info(f'get_all_envs_status -> active_cnt : {active_cnt}, instance : {instance}')
            try:
                es_node_length = len(instance.get("es_url", "").split(","))
                # logging.info(f"instance active : {es_node_length}")

                if active_cnt == es_node_length:
                    ''' green'''
                    self.all_env_status.append(1)
                elif active_cnt > 0 and active_cnt < es_node_length:
                    ''' yellow'''
                    self.all_env_status.append(0)
                else:
                    ''' red'''
                    self.all_env_status.append(-1)
      
            except Exception as e:
                logging.error(e)

    
    def get_all_health_status(self):
        return self.all_env_status



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
    global remote_prometheus_json, is_over_free_Disk_space

    try:
        resp = requests.get(url="http://{}:2112/metrics".format(os.getenv("REMOTE_AGENT_HOST")), timeout=5)
                    
        if not (resp.status_code == 200):
            logging.error(f"get_exporter_apps api do not reachable")
            node_agent_status_gauge_g.labels(server_job=socket.gethostname()).set(0)
            return
        
        ''' update metrics for the remote nodes export apps to 1 as Green'''
        node_agent_status_gauge_g.labels(server_job=socket.gethostname()).set(1)

        remote_prometheus_json = {}
        remote_prometheus_json = transform_prometheus_txt_to_Json(resp)
        # logging.info(f"** {remote_prometheus_json.get('basiccpuModelInfoGauge')}")
        # logging.info(f"** {remote_prometheus_json}")
        # logging.info(f"** {remote_prometheus_json.get('diskUsageGauge')}")

        ''' cpu usage'''
        ''' [{'label': 'localhost', 'set_value': '13.969631'}] '''
        # logging.info(f"cpu_usage : {remote_prometheus_json.get('cpuUsage')}")
        cpu_usage_gauge_g.labels(socket.gethostname()).set(float(remote_prometheus_json.get("cpuUsage")[0].get('set_value')))
        ''' memory usage '''
        memory_usage_gauge_g.labels(socket.gethostname()).set(float(remote_prometheus_json.get("basicMemoryUsedPercentGauge")[0].get('set_value')))
        ''' memory used '''
        memory_total_gauge_g.labels(socket.gethostname()).set(float(remote_prometheus_json.get("basicMemoryTotalGauge")[0].get('set_value')))
        ''' memory used '''
        memory_used_gauge_g.labels(socket.gethostname()).set(float(remote_prometheus_json.get("basicMemoryUsedGauge")[0].get('set_value')))
        ''' memory available '''
        memory_available_gauge_g.labels(socket.gethostname()).set(float(remote_prometheus_json.get("basicMemoryAvailableGauge")[0].get('set_value')))

        ''' disk usage'''
        disk_usage_list = remote_prometheus_json.get('diskUsageGauge')
        for each_disk in disk_usage_list:
            del each_disk["set_value"]
            for v in each_disk.values():
                disk_infos = v.split(",")
                disk_infos_property_dict = {}
                for disk_property in disk_infos:
                    disk_infos_property_dict.update({disk_property.split("=")[0] : disk_property.split("=")[1]})
                # print(disk_infos_property_dict)
                
                current_disk_usages_path = disk_infos_property_dict.get("diskusagepercent")
                current_disk_usages_path = float(current_disk_usages_path.replace("%", ''))
                is_disk_fine = 0
                if current_disk_usages_path < disk_usage_threshold:
                    is_disk_fine = 1
                else:
                    is_over_free_Disk_space = True
                    ''' set alert log'''  
                    saved_failure_dict.update({"disk_alert_{}".format(disk_infos_property_dict.get("path")) : "[host : {}]".format(os.getenv("REMOTE_AGENT_HOST")) + " Disk Path : {},".format(disk_infos_property_dict.get("path")) + " Disk Used : " + str(current_disk_usages_path) + "%" + ", Disk Threshold : " + str(disk_usage_threshold) + "%" })

                ''' set metrics for all disk paths'''
                nodes_diskspace_gauge_g.labels(server_job=socket.gethostname(), category='Remote Node', host=os.getenv("REMOTE_AGENT_HOST"), 
                                                   diskfree=disk_infos_property_dict.get("diskfree"), disktotal=disk_infos_property_dict.get("disktotal"), diskusagepercent=disk_infos_property_dict.get("diskusagepercent"),
                                                   diskused=disk_infos_property_dict.get("diskused"), ipaddress=disk_infos_property_dict.get("ipaddress"), path=disk_infos_property_dict.get("path")
                                                   ).set(is_disk_fine)

    except Exception as e:
        ''' update metrics for the remote nodes export apps to 0 as Red'''
        node_agent_status_gauge_g.labels(server_job=socket.gethostname()).set(0)
        logging.error(e)
        

def gather_metrics_export(monitoring_metrics):
    ''' export metrics'''
    global remote_prometheus_json
    
    try:
        global saved_thread_alert, saved_thread_alert_message, save_thread_alert_history
        global saved_status_dict

        ''' create object for class'''
        monitor_obj = monitor()

        logging.info(f"env_name : {env_name}")
        logging.info(f"monitoring_metrics : {monitoring_metrics}")
        
        ''' check port is alive'''
        resp = monitor_obj.get_service_port_alive(monitoring_metrics)

        print(resp.get("es_url")['GREEN_CNT'], monitoring_metrics)

        ''' update serer active'''
        monitor_obj.set_all_envs_status(resp.get("es_url")['GREEN_CNT'], monitoring_metrics)
        ''' update status for alert'''
        MAX_NUMBERS = len(monitoring_metrics.get("es_url").split(","))
        if int(resp["es_url"]["GREEN_CNT"]) == MAX_NUMBERS:
            status = 'Green' 
        elif 0 < int(resp["es_url"]["GREEN_CNT"]) < MAX_NUMBERS:
            status = 'Yellow' 
        else:
            status = 'Red'
        service_status_dict.update({"es" : status})

        logging.info(f"monitor_obj.get_all_health_status() : {monitor_obj.get_all_health_status()}")

        ''' faiure log message '''
        logging.error(f"saved_failure_dict : {saved_failure_dict}")

        ''' ----------------------------------------------------- '''
        ''' Set Server Active Graph'''
        ''' set value for node instance '''
        if list(set(monitor_obj.get_all_health_status())) == [1]:
            ''' green '''
            all_envs_status_gauge_g.labels(server_job=socket.gethostname(), type='cluster').set(1)
            saved_status_dict.update({'server_active' : 'Green'})
        
        elif list(set(monitor_obj.get_all_health_status())) == [-1]:
            ''' red '''
            all_envs_status_gauge_g.labels(server_job=socket.gethostname(), type='cluster').set(3)
            ''' update gloabl variable for alert email'''
            saved_status_dict.update({'server_active' : 'Red'})

        else:
            ''' yellow '''
            all_envs_status_gauge_g.labels(server_job=socket.gethostname(), type='cluster').set(2)
            ''' update gloabl variable for alert email'''
            saved_status_dict.update({'server_active' : 'Yellow'})
        ''' ----------------------------------------------------- '''

        """ create alert audit message"""        
        failure_message = []

        """ create alert audit message & Update log metrics"""
        ''' merge'''
        for v in saved_failure_dict.values():
            failure_message.append(v)
        
         
        ''' one of services is inactive or any issue with data pieplines or any issue with Kakfa offset like out of range from the kafak offset'''
        # if not list(set(all_env_status_memory_list)) == [1] or saved_failure_db_dict or saved_failure_db_kafka_dict:
        if not list(set(monitor_obj.get_all_health_status())) == [1]:
            ''' if failure mesage has something'''
            if failure_message:
                saved_thread_alert = True
                saved_thread_alert_message = failure_message

                ''' Whenever app does check for the alerts every 10 minutes, sends the first alert, and then resends the alert after 1 hour.'''
                # get_alert_resend(False)
    
                ''' add history for alerting '''
                save_thread_alert_history.append(True)
        else:
            saved_thread_alert = False
            ''' add history for alerting '''
            save_thread_alert_history.append(False)
       

        ''' ------------------------------------------------------'''
        logging.info(f"saved_thread_alert - {saved_thread_alert}")
        logging.info(f"save_thread_alert_history - {save_thread_alert_history}")
        logging.info(f"saved_status_dict - {json.dumps(saved_status_dict, indent=2)}")
        logging.info(f"service_status_dict - {json.dumps(service_status_dict, indent=2)}")
        # logging.info(f"Mail Alert mail Configuration - {global_mail_configuration.get(hostname).get('is_mailing','')}, Mail Alert SMS Configuration : {global_mail_configuration.get(hostname).get('is_sms','')}")
        logging.info(f"current_alert_message : {saved_thread_alert_message}")
        
    except Exception as e:
        logging.error(e)


def set_initialize():
    ''' initialize'''
    ''' clear logs '''
    saved_failure_dict.clear()
    ''' initialize metrics'''
    cpu_usage_gauge_g._metrics.clear()
    memory_usage_gauge_g._metrics.clear()
    memory_total_gauge_g._metrics.clear()
    memory_used_gauge_g._metrics.clear()
    memory_available_gauge_g._metrics.clear()
    nodes_diskspace_gauge_g._metrics.clear()

    all_envs_status_gauge_g._metrics.clear()
    node_agent_status_gauge_g._metrics.clear()


def alert_work(thread_interval):
    ''' alert work '''
    try:
        while True:
            logging.warn(f"saved_thread_alert : {saved_thread_alert}, saved_status_dict : {saved_status_dict}, service_status_dict : {service_status_dict}")
            ''' Call function to send an email'''
            if saved_thread_alert:
                logging.warn(f"saved_thread_alert_message : {saved_thread_alert_message}")
                logging.warn(f"Will send an alert..")
                
            time.sleep(60*thread_interval)

    except (KeyboardInterrupt, SystemExit):
        logging.info("#Interrupted..")

    except Exception as e:
        logging.info(e)
        pass
    

''' global variable '''
saved_failure_dict = {}


''' alert message to mail with interval?'''
saved_thread_alert = False
save_thread_alert_history = []
saved_thread_alert_message = []
saved_status_dict = {}
service_status_dict = {}
is_over_free_Disk_space = False
disk_usage_threshold = 10

def work(port, interval, monitoring_metrics):
    try:
        start_http_server(int(port))
        logging.info(f"Standalone Prometheus Exporter Server started..")

        StartedTime = datetime.datetime.now()
        while True:
            print(f"\n")
            logging.info(f"Prometheus Exporter Refreshed..")
            StartTime = datetime.datetime.now()

            ''' initialize prometheus metrics type'''
            set_initialize()

            ''' call fun'''
            ''' get resource from go exporter application'''
            get_exporter_apps()

            ''' Main export func'''
            gather_metrics_export(monitoring_metrics)

            ''' export application processing time '''
            EndTime = datetime.datetime.now()
            Delay_Time = str((EndTime - StartTime).seconds) + '.' + str((EndTime - StartTime).microseconds).zfill(6)[:2]

            logging.info("# Running Prometheus Export Application - {}".format("http://{}:{}".format(socket.gethostname(), str(port))))
            logging.info("# StartedTime Application - {}".format(str(StartedTime)))
            logging.info("# Export Application Running Time - {}\n".format(str(Delay_Time)))

            time.sleep(interval)
      
    except (KeyboardInterrupt, SystemExit):
        logging.info("#Interrupted..")
       


if __name__ == '__main__':
    '''
    https://taehyuklee.tistory.com/12 :  AttributeError: module 'resource' has no attribute 'getpagesize'
    '''
    parser = argparse.ArgumentParser(description="Script that might allow us to use it as an application of custom prometheus exporter")
    parser.add_argument('--env_name', dest='env_name', default="env_name", help='env_name')
    parser.add_argument('--es_url', dest='es_url', default="localhost:9200,localhost:9501,localhost:9503", help='es hosts')
    parser.add_argument('--port', dest='port', default=2113, help='Expose Port')
    parser.add_argument('--interval', dest='interval', default=30, help='Interval')
    args = parser.parse_args()

    # global global_env_name

    if args.env_name:
        env_name = args.env_name

    if args.es_url:
        es_url = args.es_url

    if args.interval:
        interval = args.interval

    if args.port:
        port = args.port


    monitoring_metrics = {
        "es_url" : es_url
    }

    ''' alert interval'''
    thread_interval = 1
    
    try:
        T = []

        ''' main active monitoring logic '''
        main_th = Thread(target=work, args=(int(port), int(interval), monitoring_metrics))
        main_th.daemon = True
        main_th.start()
        T.append(main_th)

        ''' alert through mailx'''
        mail_th = Thread(target=alert_work, args=(thread_interval,))
        mail_th.daemon = True
        mail_th.start()
        T.append(mail_th)


        # wait for all threads to terminate
        for t in T:
            while t.is_alive():
                t.join(0.5)

    except (KeyboardInterrupt, SystemExit):
        logging.info("# Interrupted..")
    
    logging.info("Standalone Prometheus Exporter Server exited..!")