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
import jaydebeapi
import jpype
import re
from collections import defaultdict
# import paramiko
import base64
from dotenv import load_dotenv
import warnings
warnings.filterwarnings("ignore")


''' pip install python-dotenv'''
load_dotenv() # will search for .env file in local folder and load variables 


# logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

""" ---------------- """
""" Grafana Loki """
import logging
import logging_loki
logging_loki.emitter.LokiEmitter.level_tag = "level"
# assign to a variable named handler 
handler = logging_loki.LokiHandler(
   url="http://{}:3100/loki/api/v1/push".format(os.getenv("LOKI_HOST")),
   version="1",
)
# create a new logger instance, name it whatever you want
logger = logging.getLogger("prometheus-logger")
logger.addHandler(handler)
""" ---------------- """


# Initialize & Inject with only one instance
logging = create_log()


hitl_server_health_status = Enum("hitl_server_health_status", "PSQL connection health", states=["healthy", "unhealthy"])
# kafka_broker_health_status = Enum("kafka_broker_health_status", "Kafka connection health", states=["green","yellow","red"])
hitl_server_health_request_time = Histogram('hitl_server_health_request_time', 'Server connection response time (seconds)')

kafka_brokers_gauge = Gauge("kafka_brokers", "the number of kafka brokers")

''' export application performance metric'''
es_service_jobs_performance_gauge_g = Gauge("es_service_jobs_performance_running_metrics", 'Metrics scraped from localhost', ["server_job"])

''' gauge with dict type'''

''' es_exporter_plugin'''
es_exporter_cpu_usage_gauge_g = Gauge("es_exporter_cpu_metrics", 'Metrics scraped from localhost', ["server_job", "type", "name", "cluster"])
es_exporter_jvm_usage_gauge_g = Gauge("es_exporter_jvm_metrics", 'Metrics scraped from localhost', ["server_job", "type", "name", "cluster"])

''' type : cluster/data_pipeline'''
all_envs_status_gauge_g = Gauge("all_envs_status_metric", 'Metrics scraped from localhost', ["server_job", "type"])
nodes_diskspace_gauge_g = Gauge("node_disk_space_metric", 'Metrics scraped from localhost', ["server_job", "category", "host", "name", "ip", "disktotal", "diskused", "diskavail", "diskusedpercent"])
nodes_free_diskspace_gauge_g = Gauge("node_free_disk_space_metric", 'Metrics scraped from localhost', ["server_job", "category", "name" ,"diskusedpercent"])
nodes_max_disk_used_gauge_g = Gauge("node_disk_used_metric", 'Metrics scraped from localhost', ["server_job", "category"])
es_nodes_gauge_g = Gauge("es_node_metric", 'Metrics scraped from localhost', ["server_job"])
es_nodes_basic_info_docs_gauge_g = Gauge("es_node_basic_docs_metric", 'Metrics scraped from localhost', ["server_job"])
es_nodes_basic_info_indices_gauge_g = Gauge("es_node_basic_indices_metric", 'Metrics scraped from localhost', ["server_job"])
es_nodes_health_gauge_g = Gauge("es_health_metric", 'Metrics scraped from localhost', ["server_job"])
kafka_nodes_gauge_g = Gauge("kafka_health_metric", 'Metrics scraped from localhost', ["server_job"])
kafka_connect_nodes_gauge_g = Gauge("kafka_connect_nodes_metric", 'Metrics scraped from localhost', ["server_job"])
kafka_connect_nodes_health_gauge_g = Gauge("kafka_connect_nodes_health_metric", 'Metrics scraped from localhost', ["server_job"])
kafka_connect_listeners_gauge_g = Gauge("kafka_connect_listeners_metric", 'Metrics scraped from localhost', ["server_job", "host", "name", "running"])
kafka_connect_health_gauge_g = Gauge("kafka_connect_health_metric", 'Metrics scraped from localhost', ["server_job"])
kafka_isr_list_gauge_g = Gauge("kafka_isr_list_metric", 'Metrics scraped from localhost', ["server_job", "topic", "partition", "leader", "replicas", "isr"])
zookeeper_nodes_gauge_g = Gauge("zookeeper_health_metric", 'Metrics scraped from localhost', ["server_job"])
spark_nodes_gauge_g = Gauge("spark_health_metric", 'Metrics scraped from localhost', ["server_job"])
kibana_instance_gauge_g = Gauge("kibana_health_metric", 'Metrics scraped from localhost', ["server_job"])
redis_instance_gauge_g = Gauge("redis_health_metric", 'Metrics scraped from localhost', ["server_job"])
es_configuration_instance_gauge_g = Gauge("es_configuration_writing_job_health_metric", 'Metrics scraped from localhost', ["server_job"])
es_configuration_api_instance_gauge_g = Gauge("es_configuration_api_health_metric", 'Metrics scraped from localhost', ["server_job"])
log_db_instance_gauge_g = Gauge("log_db_health_metric", 'Metrics scraped from localhost', ["server_job"])
alert_monitoring_ui_gauge_g = Gauge("alert_monitoring_ui_health_metric", 'Metrics scraped from localhost', ["server_job"])
loki_ui_gauge_g = Gauge("loki_ui_health_metric", 'Metrics scraped from localhost', ["server_job"])
loki_api_instance_gauge_g = Gauge("loki_api_health_metric", 'Metrics scraped from localhost', ["server_job"])
loki_agent_instance_gauge_g = Gauge("loki_agent_health_metric", 'Metrics scraped from localhost', ["server_job", "category"])
log_agent_instance_gauge_g = Gauge("log_agent_health_metric", 'Metrics scraped from localhost', ["server_job", "category"])
alert_state_instance_gauge_g = Gauge("alert_state_metric", 'Metrics scraped from localhost', ["server_job"])
logstash_instance_gauge_g = Gauge("logstash_health_metric", 'Metrics scraped from localhost', ["server_job"])
spark_jobs_gauge_g = Gauge("spark_jobs_running_metrics", 'Metrics scraped from localhost', ["server_job", "host", "id", "cores", "memoryperslave", "submitdate", "duration", "activeapps", "state"])
# db_jobs_gauge_g = Gauge("db_jobs_running_metrics", 'Metrics scraped from localhost', ["server_job", "processname", "cnt", "status", "addts", "dbid", "db_info"])
db_jobs_gauge_wmx_g = Gauge("db_jobs_wmx_running_metrics", 'Metrics scraped from localhost', ["server_job", "processname", "cnt", "status", "addts", "dbid", "db_info"])
db_jobs_gauge_kafka_offset_wmx_g = Gauge("db_jobs_wmx_kafka_offset_running_metrics", 'Metrics scraped from localhost', ["server_job", "topic",  "partition_num", "offset", "addts", "addwho", "editts", "editwho", "dbid"])
db_jobs_gauge_omx_g = Gauge("db_jobs_omx_running_metrics", 'Metrics scraped from localhost', ["server_job", "processname", "cnt", "status", "addts", "dbid", "db_info"])
db_jobs_performance_WMx_gauge_g = Gauge("db_jobs_performance_running_metrics", 'Metrics scraped from localhost', ["server_job"])
db_jobs_performance_OMx_gauge_g = Gauge("db_jobs_performance2_running_metrics", 'Metrics scraped from localhost', ["server_job"])
db_jobs_wmx_sql_data_pipeline_gauge_g = Gauge("wmx_data_pipeline_sql_running_time_metrics", 'Metrics scraped from localhost', ["server_job"])
db_jobs_omx_sql_data_pipeline_gauge_g = Gauge("omx_data_pipeline_sql_running_time_metrics", 'Metrics scraped from localhost', ["server_job"])
db_jobs_backlogs_WMx_gauge_g = Gauge("db_jobs_backlog_wmx_running_metrics", 'Metrics scraped from localhost', ["server_job"])
db_jobs_backlogs_OMx_gauge_g = Gauge("db_jobs_backlog_omx_running_metrics", 'Metrics scraped from localhost', ["server_job"])

''' export failure instance list metric'''
es_service_jobs_failure_gauge_g = Gauge("es_service_jobs_failure_running_metrics", 'Metrics scraped from localhost', ["server_job", "host", "reason"])



class oracle_database:

    def __init__(self, db_url) -> None:
        self.db_url = db_url
        self.set_db_connection()
        

    def set_init_JVM(self):
        '''
        Init JPYPE StartJVM
        '''

        if jpype.isJVMStarted():
            return
        
        jar = r'./ojdbc8.jar'
        args = '-Djava.class.path=%s' % jar

        # print('Python Version : ', sys.version)
        # print('JAVA_HOME : ', os.environ["JAVA_HOME"])
        # print('JDBC_Driver Path : ', JDBC_Driver)
        # print('Jpype Default JVM Path : ', jpype.getDefaultJVMPath())

        # jpype.startJVM("-Djava.class.path={}".format(JDBC_Driver))
        jpype.startJVM(jpype.getDefaultJVMPath(), args, '-Xrs')


    def set_init_JVM_shutdown(self):
        jpype.shutdownJVM() 
   

    def set_db_connection(self):
        ''' DB Connect '''
        print('connect-str : ', self.db_url)
        
        StartTime = datetime.datetime.now()

        # -- Init JVM
        self.set_init_JVM()
        # --
        
        # - DB Connection
        self.db_conn = jaydebeapi.connect("oracle.jdbc.driver.OracleDriver", self.db_url)
        # --
        EndTime = datetime.datetime.now()
        Delay_Time = str((EndTime - StartTime).seconds) + '.' + str((EndTime - StartTime).microseconds).zfill(6)[:2]
        print("# DB Connection Running Time - {}".format(str(Delay_Time)))

    
    def set_db_disconnection(self):
        ''' DB Disconnect '''
        self.db_conn.close()
        print("Disconnected to Oracle database successfully!") 

    
    def get_db_connection(self):
        return self.db_conn
    

    def excute_oracle_query(self, sql):
        '''
        DB Oracle : Excute Query
        '''
        print('excute_oracle_query -> ', sql)
        # Creating a cursor object
        cursor = self.get_db_connection().cursor()

        # Executing a query
        cursor.execute(sql)
        
        # Fetching the results
        results = cursor.fetchall()
        cols = list(zip(*cursor.description))[0]
        # print(type(results), cols)

        json_rows_list = []
        for row in results:
            # print(type(row), row)
            json_rows_dict = {}
            for i, row in enumerate(list(row)):
                json_rows_dict.update({cols[i] : row})
            json_rows_list.append(json_rows_dict)

        cursor.close()

        # logging.info(json_rows_list)
        
        return json_rows_list
    


class ProcessHandler():
    ''' Get the process by the processname'''

    def __init__(self) -> None:
        pass

    ''' get ProcessID'''
    def isProcessRunning(self, name):
        ''' Get PID with process name'''
        try:
            call = subprocess.check_output("pgrep -f '{}'".format(name), shell=True)
            logging.info("Process IDs - {}".format(call.decode("utf-8")))
            return True
        except subprocess.CalledProcessError:
            return False
        
    
    ''' get command result'''
    def get_run_cmd_Running(self, cmd):
        ''' Get PID with process name'''
        try:
            logging.info("get_run_cmd_Running - {}".format(cmd))
            call = subprocess.check_output("{}".format(cmd), shell=True)
            output = call.decode("utf-8")
            # logging.info("CMD - {}".format(output))
            # logging.info(output.split("\n"))
            
            output = [element for element in output.split("\n") if len(element) > 0]

            return output
        except subprocess.CalledProcessError:
            return None   


def transform_prometheus_txt_to_Json(response, metrics):
    ''' transform_prometheus_txt_to_Json '''
    
    # filter_metrics_names = ['elasticsearch_process_cpu_percent', 'elasticsearch_jvm_memory_used_bytes']
    body_list = [body for body in response.text.split("\n") if not "#" in body and len(body)>0]

    '''
    filterd_list = []
    for each_body in body_list:
        for filtered_metric in filter_metrics_names:
            if filtered_metric in each_body:
                filterd_list.append(str(each_body).replace(filtered_metric, ''))
    '''
    
    # logging.info(f"transform_prometheus_txt_to_Json - {body_list}")

    prometheus_list_json = []
    # loop = 0
    for x in body_list:
        json_key_pairs = x.split(" ")
        # prometheus_json.update({json_key_pairs[0] : json_key_pairs[1]})

        if metrics == 'es':
            logging.info('es')
        
        elif metrics == 'cpu_jvm':
            if 'elasticsearch_process_cpu_percent' in json_key_pairs[0]:
                json_key_pairs[0] = json_key_pairs[0].replace('elasticsearch_process_cpu_percent','')
                extract_keys = json_key_pairs[0].replace("{","").replace("}","").replace("\"","").split(",")
                json_keys_list = {each_key.split("=")[0] : each_key.split("=")[1] for each_key in extract_keys}

                prometheus_list_json.append({'cluster' : json_keys_list.get('cluster'), 'name' : json_keys_list.get('name'), 'cpu_usage_percentage' : json_key_pairs[1], "category" : "cpu_usage"})

            elif 'elasticsearch_jvm_memory_used_bytes' in json_key_pairs[0] and 'non-heap' not in json_key_pairs[0]:
                json_key_pairs[0] = json_key_pairs[0].replace('elasticsearch_jvm_memory_used_bytes','')
                extract_keys = json_key_pairs[0].replace("{","").replace("}","").replace("\"","").split(",")
                json_keys_list = {each_key.split("=")[0] : each_key.split("=")[1] for each_key in extract_keys}

                prometheus_list_json.append({'cluster' : json_keys_list.get('cluster'), 'name' : json_keys_list.get('name'), 'jvm_memory_used_bytes' : json_key_pairs[1], "category" : "jvm_memory_used_bytes"})

            elif 'elasticsearch_jvm_memory_max_bytes' in json_key_pairs[0]:
                json_key_pairs[0] = json_key_pairs[0].replace('elasticsearch_jvm_memory_max_bytes','')
                extract_keys = json_key_pairs[0].replace("{","").replace("}","").replace("\"","").split(",")
                json_keys_list = {each_key.split("=")[0] : each_key.split("=")[1] for each_key in extract_keys}

                prometheus_list_json.append({'cluster' : json_keys_list.get('cluster'), 'name' : json_keys_list.get('name'), 'jvm_memory_max_bytes' : json_key_pairs[1], "category" : "jvm_memory_max_bytes"})

                '''
                [
                    {
                        "name": "logging-dev-node-4",
                        "cluster : "dev",
                        "cpu_usage_percentage": "4",
                        "category": "cpu_usage"
                    },
                    {
                        "name": "logging-dev-node-1",
                        "cluster : "dev",
                        "cpu_usage_percentage": "2",
                        "category": "cpu_usage"
                    },
                    {
                        "name": "logging-dev-node-2",
                        "cluster : "dev",
                        "cpu_usage_percentage": "8",
                        "category": "cpu_usage"
                    },
                    {
                        "name": "logging-dev-node-3",
                        "cluster : "dev",
                        "cpu_usage_percentage": "4",
                        "category": "cpu_usage"
                    }
                ]

                '''
    print(json.dumps(prometheus_list_json, indent=2))

    return prometheus_list_json




''' save failure nodes into dict'''
saved_failure_dict, saved_failure_tasks_dict = {}, {}
''' expose this metric to see maximu disk space among ES/Kafka nodes'''
max_disk_used, max_es_disk_used, max_kafka_disk_used = 0, 0, 0
each_es_instance_cpu_history, each_es_instance_jvm_history = {}, {}


def get_metrics_all_envs(monitoring_metrics):
    ''' get metrics from custom export for the health of kafka cluster'''
    
    global saved_failure_dict, max_disk_used, max_es_disk_used, max_kafka_disk_used
    global each_es_instance_cpu_history, each_es_instance_jvm_history
    global service_status_dict
    global is_dev_mode

    ''' initialize global variables '''
    max_disk_used, max_es_disk_used, max_kafka_disk_used = 0, 0, 0

    def get_service_port_alive(monitoring_metrics):
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
        logging.info(response_dict)
        return response_dict


    def get_kafka_connector_listeners(node_list_str):
        ''' get the state of each node's listener'''
        ''' 1) http://localhost:8083/connectors/  -> ["test_api",..]'''
        ''' 
            2) http://localhost:8083/connectors/test_api/status 
            -> 
            "localhost" : [
                    {
                        "name": "test_api",
                        "connector": {
                            "state": "RUNNING",
                            "worker_id": "127.0.0.1:8083"
                        },
                        "tasks": [
                            {
                            "state": "RUNNING",
                            "id": 0,
                            "worker_id": "127.0.0.1:8083"
                            }
                        ]
                    }
              ]
        '''
        global saved_failure_tasks_dict

        ''' clear '''
        saved_failure_tasks_dict.clear()

        try:
            if not node_list_str:
                return None, False
            logging.info(f"get_kafka_connector_listeners - {node_list_str}")
            
            master_node = node_list_str.split(",")[0].split(":")[0]
            logging.info(f"get_kafka_connector_listeners #1- {master_node}")

            node_hosts = node_list_str.split(",")
            nodes_list = [node.split(":")[0] for node in node_hosts]
            
            active_listner_list = {}
            active_listner_connect = []
            
            for each_node in nodes_list:
                try:
                    # -- make a call to master node to get the information of activeapps
                    logging.info(each_node)
                    resp = requests.get(url="http://{}:8083/connectors".format(each_node), timeout=5, verify=False)
                        
                    # logging.info(f"activeapps - {resp}, {resp.status_code}, {resp.json()}")
                    logging.info(f"activeconnectors/listeners - {resp}, {resp.status_code}")
                    if not (resp.status_code == 200):
                        continue
                    else:
                    #    active_listner_connect.update({each_node : resp.json()})
                        active_listner_connect = resp.json()
                        break
                except Exception as e:
                    pass

            logging.info(f"active_listener_list - {json.dumps(active_listner_connect, indent=2)}")

            ''' add tracking logs and save failure node with a reason into saved_failure_dict'''
            if not active_listner_connect:
                saved_failure_dict.update({",".join(nodes_list): "http://{}:8083/connectors API do not reachable".format(nodes_list)})
                return None, False
            
            '''
            # Master node
            # -- make a call to master node to get the information of activeapps
            resp = requests.get(url="http://{}:8083/connectors".format(master_node), timeout=5)
            if not (resp.status_code == 200):
                return None
            else:
                # logging.info("OK~@#")
                active_listner_connect.update({master_node : resp.json()})
            logging.info(f"active_listner_connect #1 - {json.dumps(active_listner_connect.get(master_node), indent=2)}")
            '''

            #-- with listeners_list
            listener_apis_dict = {}
            failure_check = False
            all_listeners_is_empty = []
            node_lists_loop = 0
            for node in nodes_list:
                listener_apis_dict.update({node : {}})
                listeners_list = []
                loop = 1
                for listener in active_listner_connect:
                    try:
                        # loop +=1
                        """
                        resp_each_listener = requests.get(url="http://{}:8083/connectors/{}".format(node, listener), timeout=5)
                        # logging.info(f"len(resp_each_listener['tasks']) - {node} -> { len(list(resp_each_listener.json()['tasks']))}")
                        ''' If the “task” details are missing from the listener, then we probably are not processing data.'''
                        if len(list(resp_each_listener.json()["tasks"])) > 0:
                            # logging.info(f"listener_apis_dict make a call - {node} -> {listener}")
                            resp_listener = requests.get(url="http://{}:8083/connectors/{}/status".format(node, listener), timeout=5)
                            # logging.info(f"listeners - {resp_listener}, {resp_listener.json()}")
                            listeners_list.append(resp_listener.json())
                        else:
                            ''' save failure node with a reason into saved_failure_dict'''
                            saved_failure_dict.update({"{}_{}".format(node, str(loop)) : "http://{}:8083/connectors/{} tasks are missing".format(node, listener)})
                        """
                        resp_tasks = requests.get(url="http://{}:8083/connectors/{}".format(node, listener), timeout=5, verify=False)
                        
                        if not (resp_tasks.status_code == 200):
                            continue

                        logging.info(f"get_kafka_connector_listeners [tasks] : {resp_tasks.json().get('tasks')}")
                        if len(list(resp_tasks.json().get('tasks'))) < 1:
                            ''' save failure node with a reason into saved_failure_dict'''
                            logging.info(f"no [tasks] : {resp_tasks.json().get('tasks')}")
                            
                            ''' It works find if the status of listeners in base node is green'''
                            if node_lists_loop == 0:
                                saved_failure_dict.update({"{}_{}".format(node, str(loop))  : "http://{}:8083/connectors/{} tasks are missing".format(node, listener)})
                            else:
                                ''' Except from audit message'''
                                saved_failure_tasks_dict.update({"{}_{}".format(node, str(loop))  : "http://{}:8083/connectors/{} tasks are missing".format(node, listener)})

                            ''' tasks are empty on only base node'''
                            if node_lists_loop == 0:
                                all_listeners_is_empty.append(True)
                            continue
                        else:
                            ''' tasks are empty on only base node'''
                            if node_lists_loop == 0:
                                all_listeners_is_empty.append(False)

                        resp_listener = requests.get(url="http://{}:8083/connectors/{}/status".format(node, listener), timeout=5, verify=False)
                        listeners_list.append(resp_listener.json())
                        
                        loop +=1
                    except Exception as e:
                        ''' save failure node with a reason into saved_failure_dict'''
                        saved_failure_dict.update({"{}_{}".format(node, str(loop))  : "http://{}:8083/connectors/[listeners]/status json API do not reachable".format(node, listener)})
                        # saved_failure_dict.update({"{}_{}".format(node, str(loop))  : "http://{}:8083/connectors/{}/status json API do not reachable".format(node, listener)})
                        # saved_failure_dict.update({"{}_{}".format(node, str(loop))  : "http://{}:8083/connectors/{}/status API{}".format(node, listener, str(e))})
                        ''' master kafka connect is runnning correctly, it doesn't matter'''
                        if loop > 1:
                            failure_check = True
                        # failure_check = True
                        pass
                listener_apis_dict.update({node : listeners_list})
                node_lists_loop +=1

            # logging.info(f"listener_apis_dict - {json.dumps(listener_apis_dict, indent=2)}")
            logging.info(f"listener_apis_dict - {listener_apis_dict}")
            ''' result '''
            '''
            {
                "localhost1": [{
                    "test_jdbc": {
                    "name": "test_jdbc",
                    "connector": {
                        "state": "RUNNING",
                        "worker_id": "localhost:8083"
                    },
                    "tasks": [
                        {
                        "state": "RUNNING",
                        "id": 0,
                        "worker_id": "localhost:8083"
                        }
                    ]
                    }
                },
                "localhost2": {},
                "localhost3": {}
            }]

            '''
            failure_check = all(all_listeners_is_empty) or failure_check
            # failure_check = all(all_listeners_is_empty)

            return listener_apis_dict, failure_check
            
            
        except Exception as e:
            logging.error(e)


    def get_spark_jobs(node):
        ''' get_spark_jobs '''
        ''' get_spark_jobs - localhost:9092,localhost:9092,localhost:9092 '''
        ''' first node of --kafka_url argument is a master node to get the number of jobs using http://localhost:8080/json '''
        try:

            ''' clear spark nodes health'''
            spark_nodes_gauge_g.clear()

            if not node:
                return None
            logging.info(f"get_spark_jobs - {node}")
            master_node = node.split(",")[0].split(":")[0]
            logging.info(f"get_spark_jobs #1- {master_node}")

            # -- make a call to master node to get the information of activeapps
            resp = requests.get(url="http://{}:8080/json".format(master_node), timeout=60, verify=False)
            logging.info(f"get_spark_jobs - response {resp.status_code}")
            
            if not (resp.status_code == 200):
                spark_nodes_gauge_g.labels(server_job=socket.gethostname()).set(0)
                saved_failure_dict.update({node : "Spark cluster - http://{}:8080/json API do not reachable".format(master_node)})
                return None
            
            ''' expose metrics spark node health is active'''
            spark_nodes_gauge_g.labels(server_job=socket.gethostname()).set(1)

            # logging.info(f"activeapps - {resp}, {resp.json()}")
            resp_working_job = resp.json().get("activeapps", "")
            # response_activeapps = []
            if resp_working_job:
                logging.info(f"activeapps - {resp_working_job}")
                if len(resp_working_job)  < 1:
                    saved_failure_dict.update({"{}:8080".format(master_node) : "Spark cluster - No Spark Custom Apps".format(master_node)})   
                logging.info(f"get_active_jobs [Yes] {resp_working_job}") 
                return resp_working_job
            else:
                logging.info(f"get_active_jobs [No] {resp_working_job}") 
                saved_failure_dict.update({"{}:8080".format(master_node) : "Spark cluster - http://{}:8080/json, no active jobs. Please run 'Spark Custom Apps'".format(master_node)})

            # return resp.json().get("completedapps", "")
            return []

        except Exception as e:
            ''' add tracking logs and save failure node with a reason into saved_failure_dict'''
            saved_failure_dict.update({node : "Spark cluster - http://{}:8080/json API do not reachable".format(master_node)})
            spark_nodes_gauge_g.labels(server_job=socket.gethostname()).set(0)
            logging.error(e)
            return []
            


    def get_Process_Id():
        ''' get_Process_Id'''
        process_name = "/logstash-"
        process_handler = ProcessHandler()
        logging.info("Prcess - {}".format(process_handler.isProcessRunning(process_name)))
        if process_handler.isProcessRunning(process_name):
            return 1
        
        ''' save failure node with a reason into saved_failure_dict'''
        saved_failure_dict.update({socket.gethostname() : "Logstash is not running.."})
        return 0
    

    def get_header():
        ''' get header for security pack'''
        header =  {
            'Content-type': 'application/json', 
            'Authorization' : '{}'.format(os.getenv('BASIC_AUTH')),
            'Connection': 'close'
        }
            
        return header
    
    def get_elasticsearch_health(monitoring_metrics):
        ''' get cluster health with basic infomration such as the number of docs'''
        ''' return health json if one of nodes in cluster is acitve'''

        def get_unassigned_shards_lookup(es_cluster_call_protocal, each_es_host):
            """
            https://www.elastic.co/guide/en/elasticsearch/reference/current/diagnose-unassigned-shards.html
            http://localhost:9200/_cat/shards?format=json&v=true&h=index,shard,prirep,state,node,unassigned.reason&s=state
                [
                    {
                        "index": "test_reindex_wx_order_02072022_22_2_1",
                        "shard": "0",
                        "prirep": "r",
                        "state": "UNASSIGNED",
                        "node": null,
                        "unassigned.reason": "REPLICA_ADDED"
                    },
                    {
                        "index": "test_reindex_wx_order_02072022_22_2_1",
                        "shard": "3",
                        "prirep": "r",
                        "state": "INITIALIZING",
                        "node": "supplychain-logging-dev-node-2",
                        "unassigned.reason": "REPLICA_ADDED"
                    },
                ]
            """
            try:
                 # -- make a call to cluster for checking the disk space on all nodes in the cluster
                resp = requests.get(url="{}://{}/_cat/shards?format=json&v=true&h=index,shard,prirep,state,node,unassigned.reason&s=state".format(es_cluster_call_protocal, each_es_host), headers=get_header(), verify=False, timeout=5)
                    
                if not (resp.status_code == 200):
                    ''' save failure node with a reason into saved_failure_dict'''
                    # saved_failure_dict.update({each_es_host.split(":")[0] : each_es_host + " Port closed"})
                    return None
                    
                ''' Saved Gauge metrics'''
                logging.info(f"# get_unassigned_shards_lookup")
                unassgned_indics_list = []
                for each_json in resp.json():
                    if "UNASSIGNED" == str(each_json.get("state")).upper():
                        if each_json.get("index") not in unassgned_indics_list:
                            unassgned_indics_list.append(each_json.get("index"))

                logging.info(f"UNASSGNED SHARDS INDEX : {unassgned_indics_list}")

                return unassgned_indics_list
                
                    
            except Exception as e:
                logging.error(e)
                pass

        
        def retry_set_unassigned_shard(es_cluster_call_protocal, each_es_host, unassign_index_list):
            """
            https://www.elastic.co/guide/en/elasticsearch/reference/current/diagnose-unassigned-shards.html
            http://localhost:9200/_cat/shards?format=json&v=true&h=index,shard,prirep,state,node,unassigned.reason&s=state

            -- reset the numer of replicas to 0 and retry set to 1
            PUT test/_settings
            {
                "number_of_replicas": 0  --> "number_of_replicas": 1
            }
            """
            NUMBER_OF_REPLICAS = [0, 1]
            for unassgned_indic in unassign_index_list:
                try:
                    logging.info(f"UNASSGNED SHARDS INDEX [RESET REPLICAS]: {unassgned_indic}")
                    for number_of_replicas in NUMBER_OF_REPLICAS:
                        # -- make a call to cluster
                        payload = {
                            "number_of_replicas": int(number_of_replicas)
                        }
                        resp = requests.put(url="{}://{}/{}/_settings".format(es_cluster_call_protocal, each_es_host, unassgned_indic), headers=get_header(), json=payload, verify=False, timeout=5)
                        logging.info(f"# set_unassigned_shard : {es_cluster_call_protocal}://{each_es_host}/{unassgned_indic}/_settings")

                        if not (resp.status_code == 200):
                            ''' save failure node with a reason into saved_failure_dict'''
                            # saved_failure_dict.update({each_es_host.split(":")[0] : each_es_host + " Port closed"})
                            logging.info(f"# set_unassigned_shard not 200 STATUS CODE")
                            logging.info(f"{resp.json()}")
                            return None
                        
                        logging.info(resp.status_code, resp.json())                
                        
                except Exception as e:
                    logging.error(e)
                    pass


        try:
            es_url_hosts = monitoring_metrics.get("es_url", "")
            logging.info(f"get_elasticsearch_health hosts - {es_url_hosts}")
            es_url_hosts_list = es_url_hosts.split(",")

            ''' default ES configuration API'''
            es_cluster_call_protocal, disk_usage_threshold_es_config_api = get_es_configuration_api()

            global global_es_shards_tasks_end_occurs_unassgined
            
            for each_es_host in es_url_hosts_list:

                es_basic_info = {}
                try:
                    # -- make a call to node
                    ''' export es metrics from ES cluster with Search Guard'''
                    resp = requests.get(url="{}://{}/_cluster/health".format(es_cluster_call_protocal, each_es_host), headers=get_header(), timeout=5, verify=False)
                    
                    if not (resp.status_code == 200):
                        ''' save failure node with a reason into saved_failure_dict'''
                        # saved_failure_dict.update({each_es_host.split(":")[0] : each_es_host + " Port closed"})
                        continue
                    
                    logging.info(f"activeES - {resp}, {resp.json()}")
                    ''' log if one of ES nodes goes down'''
                    if int(resp.json().get("relocating_shards")) > 0 or int(resp.json().get("initializing_shards")) > 0 or int(resp.json().get("unassigned_shards")) > 0:
                        saved_failure_dict.update({"{}_1".format(socket.gethostname()) : "[Elasticsearch] {} relocating_shards, {} unassigned shards, {} initializing shards".format(
                            resp.json().get("relocating_shards"),
                            resp.json().get("unassigned_shards"),
                            resp.json().get("initializing_shards"))
                            }
                        )

                    ''' update status for the number of replicas'''
                    if int(resp.json().get("relocating_shards")) == 0 and int(resp.json().get("initializing_shards")) == 0:
                        ''' still ES cluster has unassgned shards'''
                        if int(resp.json().get("unassigned_shards")) > 0:
                            if int(resp.json().get("number_of_nodes")) == len(es_url_hosts_list):
                                global_es_shards_tasks_end_occurs_unassgined = True
                                ''' nedd to update '''
                                """
                                PUT test/_settings
                                {
                                "number_of_replicas": 0  --> "number_of_replicas": 1
                                }
                                """
                                unassgned_indics_list = get_unassigned_shards_lookup(es_cluster_call_protocal, each_es_host)
                                ''' Insrted log'''
                                inserted_post_log(status="ES_RESET_REPLICA", message="[ES] Reset the number of replica to INDEX [{}]".format(",".join(unassgned_indics_list)))
                                ''' PUT the number of replicas to 0 and set it back to 1'''
                                # retry_set_unassigned_shard(es_cluster_call_protocal, each_es_host, unassgned_indics_list)
                                ''' update the message for the failed a list of index name'''
                                saved_failure_dict.update({"{}_2".format(socket.gethostname())  : "[Elasticsearch] Reset the number of replica to INDEX ['{}']".format(",".join(unassgned_indics_list))})
                            else:
                                global_es_shards_tasks_end_occurs_unassgined = False
                        else:
                            global_es_shards_tasks_end_occurs_unassgined = False


                    ''' Call to get more information '''
                    resp_info = requests.get(url="{}://{}/_cat/indices?format=json".format(es_cluster_call_protocal, each_es_host), headers=get_header(), timeout=5, verify=False)
                    '''
                    [
                        {
                            "health": "green",
                            "status": "open",
                            "index": "wx_mbol_10052020_20_6_1",
                            "uuid": "2goOnXUpQNmV_w0WWKtg4w",
                            "pri": "5",
                            "rep": "1",
                            "docs.count": "172220",
                            "docs.deleted": "0",
                            "store.size": "228.2mb",
                            "pri.store.size": "117.8mb",
                            "dataset.size": "117.8mb"
                        },
                        ...
                    ]
                    '''
                    # logging.info(f"resp_basic_info - {resp_info}, {resp_info.json()}")
                    total_docs, total_indices = 0, 0
                    for each_json_info in list(resp_info.json()):
                        total_docs += int(each_json_info.get("docs.count"))
                        total_indices += 1
                            
                    es_basic_info.update({"docs" : total_docs, "indices" : total_indices})

                    return resp.json(), es_basic_info
                
                except Exception as e:
                    pass
                
            return None, None

        except Exception as e:
            logging.error(e)
            pass


    def get_float_number(s):
        ''' get float/numbder from string'''
        p = re.compile("\d*\.?\d+")
        return float(''.join(p.findall(s)))
    

    def get_es_configuration_api():
        ''' default ES configuration API'''
        # logging.info(f"global configuration : {json.dumps(gloabl_configuration, indent=2)}")
        
        disk_usage_threshold_es_config_api = 90
        if gloabl_configuration:
            disk_usage_threshold_es_config_api = gloabl_configuration.get("config").get("disk_usage_percentage_threshold")
            logging.info(f"global configuration [disk_usage_threshold as default] : {disk_usage_threshold_es_config_api}")

        ''' default ES configuration API'''
        es_cluster_call_protocal = "http"
        if gloabl_configuration:
            if gloabl_configuration.get("config").get("es_cluster_call_protocol_https"):
                es_https_list = gloabl_configuration.get("config").get("es_cluster_call_protocol_https").split(",")
                logging.info(f"socket.gethostname().split('.')[0] : {socket.gethostname().split('.')[0]}")
                logging.info(f"es_https_list : {es_https_list}")
                if socket.gethostname().split(".")[0] in es_https_list:
                    es_cluster_call_protocal = "https"
    
        logging.info(f"global configuration [es_cluster_call_protocol as default] : {es_cluster_call_protocal}")

        return es_cluster_call_protocal, disk_usage_threshold_es_config_api

    
    
    def get_elasticsearch_disk_audit_alert(monitoring_metrics):
        ''' get nodes health/check the some metrics for delivering audit alert via email '''
        ''' https://www.elastic.co/guide/en/elasticsearch/reference/current/cat-nodes.html'''

        try:
            global max_disk_used, max_es_disk_used

            es_url_hosts = monitoring_metrics.get("es_url", "")
            logging.info(f"get_elasticsearch_audit_alert hosts - {es_url_hosts}")
            es_url_hosts_list = es_url_hosts.split(",")
            
            ''' default ES configuration API'''
            es_cluster_call_protocal, disk_usage_threshold_es_config_api = get_es_configuration_api()
            logging.info(f"get_elasticsearch_disk_audit_alert : es_cluster_call_protocal - {es_cluster_call_protocal}")

            ''' get hostname without domain'''
            hostname = socket.gethostname().split(".")[0]
            
            for each_es_host in es_url_hosts_list:
                try:
                    # -- make a call to cluster for checking the disk space on all nodes in the cluster
                    resp = requests.get(url="{}://{}/_cat/nodes?format=json&h=name,ip,h,diskTotal,diskUsed,diskAvail,diskUsedPercent".format(es_cluster_call_protocal, each_es_host), headers=get_header(), verify=False, timeout=5)
                    
                    if not (resp.status_code == 200):
                        ''' save failure node with a reason into saved_failure_dict'''
                        # saved_failure_dict.update({each_es_host.split(":")[0] : each_es_host + " Port closed"})
                        continue
                    
                    logging.info(f"get_elasticsearch_disk_audit_alert - {resp}, {resp.json()}")

                    ''' Saved Gauge metrics'''
                    logging.info(f"# Metrics Check for ES Disk")
                    loop = 1
                    ''' expose this varible to Server Active'''
                    is_over_free_Disk_space = False
                    for element_dict in resp.json():
                        for k, v in element_dict.items():
                            # logging.info(f"# k - {k}, # v for ES - {v}")
                            nodes_free_diskspace_gauge_g.labels(server_job=socket.gethostname(), category="Elastic Node", name=element_dict.get("name",""), diskusedpercent=element_dict.get("diskUsedPercent","")+"%").set(element_dict.get("diskUsedPercent",""))
                            ''' disk usages is greater than 90%'''
                            # if float(element_dict.get("diskUsedPercent","-1")) >= int(os.environ["NODES_DISK_AVAILABLE_THRESHOLD"]):

                            ''' just None for host name if app doesn't have host name from es-configuration api'''
                            if hostname not in gloabl_configuration.keys():
                                get_host_name = None
                            else:
                                get_host_name = gloabl_configuration.get(hostname).get(element_dict.get("name"))

                            if float(element_dict.get("diskUsedPercent","-1")) >= int(disk_usage_threshold_es_config_api):
                                nodes_diskspace_gauge_g.labels(server_job=socket.gethostname(), category="Elastic Node", host="{}{}".format(str(global_env_name).lower(), get_host_name), name=element_dict.get("name",""), ip=element_dict.get("ip",""), disktotal=element_dict.get("diskTotal",""), diskused=element_dict.get("diskUsed",""), diskavail=element_dict.get("diskAvail",""), diskusedpercent=element_dict.get("diskUsedPercent","")+"%").set(0)
                            else:
                                nodes_diskspace_gauge_g.labels(server_job=socket.gethostname(), category="Elastic Node", host="{}{}".format(str(global_env_name).lower(), get_host_name), name=element_dict.get("name",""), ip=element_dict.get("ip",""), disktotal=element_dict.get("diskTotal",""), diskused=element_dict.get("diskUsed",""), diskavail=element_dict.get("diskAvail",""), diskusedpercent=element_dict.get("diskUsedPercent","")+"%").set(1)

                            if k == "diskUsedPercent":
                                logging.info(f"ES Disk Used : {get_float_number(v)}")
                                if max_disk_used < get_float_number(v):
                                    max_disk_used = get_float_number(v)
                                if max_es_disk_used < get_float_number(v):
                                    max_es_disk_used = get_float_number(v)
                                # if get_float_number(v) >= int(os.environ["NODES_DISK_AVAILABLE_THRESHOLD"]):
                                if get_float_number(v) >= int(disk_usage_threshold_es_config_api):
                                    ''' save failure node with a reason into saved_failure_dict'''
                                    saved_failure_dict.update({"{}_{}".format(each_es_host.split(":")[0], str(loop)) : "[host : {}, name : {}]".format(each_es_host.split(":")[0], element_dict.get("name","")) + " Disk Used : " + element_dict.get("diskUsedPercent","") + "%" + ", Disk Threshold : " + str(disk_usage_threshold_es_config_api) + "%" })
                                    is_over_free_Disk_space = True
                                loop += 1
                            
                    return is_over_free_Disk_space
                    
                except Exception as e:
                    logging.error(e)
                    pass
            
        except Exception as e:
            logging.error(e)


    disk_space_memory_list = []
    def get_kafka_disk_audit_alert(monitoring_metrics):
        ''' get kafka nodes' disk space for delivering audit alert via email '''
        ''' du -hs */ | sort -n | head '''
        
        """
        def ssh_connection(host, username, password, path, host_number):
            try:

                global disk_space_list
                
                client = paramiko.client.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(host, username=username, password=base64.b64decode(password))
                print(f"create new session ssh..")
                        
                ''' excute command line'''
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
                        "host" : host, 
                        "name" : "supplychain-logging-kafka-node-{}".format(host_number),
                        "diskTotal" : disk_space_list[1],
                        "diskused" : disk_space_list[2],
                        "diskAvail" : disk_space_list[3],
                        "diskUsedPercent" : disk_space_list[4].replace('%',''),
                        "folder" : disk_space_list[5]
                    }
                )

                disk_space_memory_list.append(disk_space_dict)        
                
            except Exception as error:
                logging.error(f"Failed : {host}")
            finally:
                client.close()
                print(f"close session ssh..")
        """
        
        def socket_connection(host, path, host_number):
            ''' gather metrics from Kafka each node'''

            global disk_space_list
            
            # Create a connection to the server application on port 81
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((host, 1234))
            
            try:
                data = str.encode(path)
                client_socket.sendall(data)

                received = client_socket.recv(1024)
                print(f"# socket client received.. {received.decode('utf-8')}")
                
                disk_space_list = [element for element in str(received.decode('utf-8').split('\n')[1]).split(' ') if len(element) > 0]
                # print('split#2 ', disk_space_list)
                # logging.info(f"Success : {host}")

                disk_space_dict = {}
                ''' split#2  disk_space_list - >  ['/dev/mapper/software-Vsfw', '100G', '17G', '84G', '17%', '/apps'] '''
                disk_space_dict.update({
                        "host" : host, 
                        "name" : "supplychain-logging-kafka-node-{}".format(host_number),
                        "ip" : socket.gethostbyname(host),
                        "diskTotal" : disk_space_list[1],
                        "diskused" : disk_space_list[2],
                        "diskAvail" : disk_space_list[3],
                        "diskUsedPercent" : disk_space_list[4].replace('%',''),
                        "folder" : disk_space_list[5]
                    }
                )

                disk_space_memory_list.append(disk_space_dict)

            except Exception as e:
                logging.error(e)
                pass
            
            finally:
                print("Closing socket")
                client_socket.close()
        
        try:

            global max_disk_used, max_kafka_disk_used

            ''' get hostname without domain'''
            hostname = socket.gethostname().split(".")[0]

            kafka_url_hosts = monitoring_metrics.get("kafka_url", "")
            logging.info(f"get_kafka_disk_autdit_alert hosts - {kafka_url_hosts}")
            kafka_url_hosts_list = kafka_url_hosts.split(",")
            logging.info(f"kafka_url_hosts_list - {kafka_url_hosts_list}")

            loop = 1
            for idx, each_server in enumerate(kafka_url_hosts_list):
                logging.info(f"{idx+1} : {each_server}")
                try:
                    # ssh_connection(str(each_server).split(":")[0].strip(), os.getenv("credentials_id"), os.getenv("credentials_pw"), "/apps/", loop)
                    socket_connection(str(each_server).split(":")[0].strip(), "/apps/", loop)
                except Exception as e:
                    pass
                loop +=1
            logging.info(f"disk space : {json.dumps(disk_space_memory_list, indent=2)}")
            
            ''' default ES configuration API'''
            es_cluster_call_protocal, disk_usage_threshold_es_config_api = get_es_configuration_api()

            ''' expose this varible to Server Active'''
            is_over_free_Disk_space = False
            ''' expose metrics for each Kafka disk space'''
            for element_dict in disk_space_memory_list:
                for k, v in element_dict.items():
                    # logging.info(f"# k - {k}, # v for ES - {v}")
                    nodes_free_diskspace_gauge_g.labels(server_job=socket.gethostname(), category="Kafka Node", name=element_dict.get("name",""), diskusedpercent=element_dict.get("diskUsedPercent","")+"%").set(element_dict.get("diskUsedPercent",""))
                    ''' disk usages is greater than 90%'''
                    # if float(element_dict.get("diskUsedPercent","-1")) >= int(os.environ["NODES_DISK_AVAILABLE_THRESHOLD"]):

                    ''' just None for host name if app doesn't have host name from es-configuration api'''
                    if hostname not in gloabl_configuration.keys():
                        get_host_name = None
                    else:
                        get_host_name = gloabl_configuration.get(hostname).get(element_dict.get("name"))

                    if float(element_dict.get("diskUsedPercent","-1")) >= int(disk_usage_threshold_es_config_api):
                        nodes_diskspace_gauge_g.labels(server_job=socket.gethostname(), category="Kafka Node", host="{}{}".format(str(global_env_name).lower(), get_host_name), name=element_dict.get("name",""), ip=element_dict.get("ip",""), disktotal=element_dict.get("diskTotal",""), diskused=element_dict.get("diskused",""), diskavail=element_dict.get("diskAvail",""), diskusedpercent=element_dict.get("diskUsedPercent","")+"%").set(0)
                    else:
                        nodes_diskspace_gauge_g.labels(server_job=socket.gethostname(), category="Kafka Node", host="{}{}".format(str(global_env_name).lower(), get_host_name), name=element_dict.get("name",""), ip=element_dict.get("ip",""), disktotal=element_dict.get("diskTotal",""), diskused=element_dict.get("diskused",""), diskavail=element_dict.get("diskAvail",""), diskusedpercent=element_dict.get("diskUsedPercent","")+"%").set(1)

                    if k == "diskUsedPercent":
                        logging.info(f"Kafka Disk Used : {get_float_number(v)}")
                        if max_disk_used < get_float_number(v):
                            max_disk_used = get_float_number(v)
                        if max_kafka_disk_used < get_float_number(v):
                            max_kafka_disk_used = get_float_number(v)
                        # if get_float_number(v) >= int(os.environ["NODES_DISK_AVAILABLE_THRESHOLD"]):
                        if get_float_number(v) >= int(disk_usage_threshold_es_config_api):
                            ''' save failure node with a reason into saved_failure_dict'''
                            saved_failure_dict.update({"{}_{}".format(element_dict.get("name",""), str(loop)) : "[host : {}, name : {}]".format(element_dict.get("host",""), element_dict.get("name","")) + " Disk Used : " + element_dict.get("diskUsedPercent","") + "%" + ", Disk Threshold : " + str(disk_usage_threshold_es_config_api) + "%" })
                            is_over_free_Disk_space = True
                            loop += 1
                    # print('max_kafka_disk_used', max_kafka_disk_used)

            return is_over_free_Disk_space
            
        except Exception as e:
            logging.error(e)


    def get_kafka_ISR_lists():
        ''' get kafka ISR lists'''
        process_handler = ProcessHandler()
        GET_KAFKA_ISR_LIST = os.environ["GET_KAFKA_ISR_LIST"]

        # kafka_topic_isr = '/home/biadmin/monitoring/custom_export/kafka_2.11-0.11.0.0/bin/kafka-topics.sh --describe --zookeeper  {} --topic ELASTIC_PIPELINE_QUEUE'.format(ZOOKEEPER_URLS)
        response = process_handler.get_run_cmd_Running(GET_KAFKA_ISR_LIST)

        # logging.info(f"Kafka ISR : {response}")
        ''' ['Topic:ELASTIC_PIPELINE_QUEUE\tPartitionCount:16\tReplicationFactor:3\tConfigs:', '\ '''

        kafk_offsets_dict = defaultdict()
        for idx in range(1, len(response)):
            each_isr = [element for element in response[idx].split("\t") if len(element) > 0]
            logging.info(each_isr)
            kafk_offsets_dict.update({"{}_{}".format(each_isr[0],str(idx-1)) : each_isr})

        logging.info(f"get_kafka_ISR_lists - {json.dumps(kafk_offsets_dict, indent=2)}")

        return kafk_offsets_dict


    def get_kafka_ISR_metrics():
        ''' get Kafka Offset_ISR by using Kafka Job Interface API or Local Kafka cluster (It required to have a kafak folder to run the command)'''
        try:
            """
            ''' Kafka ISR command result using local kafak cluster installed'''
            saved_kafka_isr_lists_dict = get_kafka_ISR_lists()
            '''
                "Topic: ELASTIC_PIPELINE_QUEUE_12": [
                    "Topic: ELASTIC_PIPELINE_QUEUE",
                    "Partition: 11",
                    "Leader: 2",
                    "Replicas: 2,1,3",
                    "Isr: 1,2"
                ],

            '''
            """
            # -- make a call to node
            ZOOKEEPER_URLS = os.environ["ZOOKEEPER_URLS"]
            KAFKA_JOB_INTERFACE_API = os.environ["KAFKA_JOB_INTERFACE_API"]
            ''' request to Kafak Job interface api'''
            resp = requests.get(url="http://{}/kafka/get_kafka_isr_list?broker_list={}".format(KAFKA_JOB_INTERFACE_API, ZOOKEEPER_URLS), timeout=5)
                    
            if not (resp.status_code == 200):
                return None
                    
            logging.info(f"get_kafka_ISR_metrics from Kafka Job Interface API - {resp}, {resp.json()}")
            saved_kafka_isr_lists_dict = resp.json()["results"]
                
            ''' If saved_kafka_isr_lists_dict is not None '''
            ''' Sometimes we have an NoneType Object from the function called when Kafka cluster went down during the security patching'''
            if saved_kafka_isr_lists_dict:
                kafka_isr_dict = {}
                for k, v in saved_kafka_isr_lists_dict.items():
                    key = k.split(":")[1].lower().strip()
                    kafka_isr_dict.update({key:{element.split(":")[0] : element.split(":")[1].strip() for element in v}})
                    
                    
                    kafka_isr_list_gauge_g._metrics.clear()  
                    logging.info(f"temp_kafka_isr_dict = {kafka_isr_dict}")  
                    for k, v in kafka_isr_dict.items():
                        logging.info(f"# k - {k}, # v - {v}")
                        kafka_isr_list_gauge_g.labels(server_job=socket.gethostname(), topic=v.get("Topic",""), partition=v.get("Partition",""), leader=v.get("Leader",""), replicas=v.get("Replicas",""), isr=v.get("Isr","")).set(1)
            

        except Exception as e:
            logging.error(e)


    def get_cpu_jvm_metrics(monitoring_metrics):
        ''' get elasticsearch exporter integration''' 

        try:
            logging.info(f"is_dev_mode - {is_dev_mode}")
            es_exporter_host = monitoring_metrics.get("kibana_url", "").split(":")[0]
            resp = requests.get(url="http://{}:9114/metrics".format(es_exporter_host), timeout=5)
                    
            if not (resp.status_code == 200):
                ''' save failure node with a reason into saved_failure_dict'''
                logging.error(f"es_config_interface api do not reachable")
                saved_failure_dict.update({socket.gethostname(): "[{}] elasticsearch exporter api do not reachable".format(es_exporter_host)})
                    
            # logging.info(f"get_mail_config - {resp}, {json.dumps(resp.json(), indent=2)}")
            # logging.info(f"get_cpu_jvm_metrics - {resp}")
            
            get_json_metrics_from_es_exporter = transform_prometheus_txt_to_Json(resp, "cpu_jvm")
            # logging.info(f"get_cpu_jvm_metrics.json - {json.dumps(get_json_metrics_from_es_exporter, indent=2)}")

            es_exporter_cpu_usage_gauge_g._metrics.clear()
            es_exporter_jvm_usage_gauge_g._metrics.clear()
            '''
                [
                    {
                        "name": "logging-dev-node-4",
                        "cluster : "dev",
                        "cpu_usage_percentage": "4",
                        "category": "cpu_usage"
                    },
                    {
                        "name": "logging-dev-node-1",
                        "cluster : "dev",
                        "cpu_usage_percentage": "2",
                        "category": "cpu_usage"
                    },
                    {
                        "name": "logging-dev-node-2",
                        "cluster : "dev",
                        "cpu_usage_percentage": "8",
                        "category": "cpu_usage"
                    },
                    {
                        "name": "logging-dev-node-3",
                        "cluster : "dev",
                        "cpu_usage_percentage": "4",
                        "category": "cpu_usage"
                    }
                ]
            '''
            jvm_heap_dict = {}
            cluster_name = ''

            total_timing_history_cnt = 0
            for each_json in get_json_metrics_from_es_exporter:
                ''' expose metrics for CPU Usage on each node'''
                if 'cpu_usage_percentage' in each_json:
                    es_exporter_cpu_usage_gauge_g.labels(server_job=socket.gethostname(), type='cpu_usage', name=each_json.get("name"), cluster=each_json.get("cluster")).set(each_json.get("cpu_usage_percentage"))
                    
                    ''' set memory for checking'''
                    # cpu_memory_buffer.append({each_json.get("name") : each_json.get("cpu_usage_percentage")})
                    if each_json.get("name") not in each_es_instance_cpu_history.keys():
                        each_es_instance_cpu_history[each_json.get("name")] = [each_json.get("cpu_usage_percentage")]
                    else:
                        each_es_instance_cpu_history[each_json.get("name")] = each_es_instance_cpu_history.get(each_json.get("name")) + [each_json.get("cpu_usage_percentage")]
    
                    # logging.info(f"each_es_instance_cpu_history [check]  : {each_es_instance_cpu_history}")
                    total_timing_history_cnt = len(each_es_instance_cpu_history.get(each_json.get("name"))) 

                if 'jvm_memory_used_bytes' in each_json or 'jvm_memory_max_bytes' in each_json:
                    if 'jvm_memory_used_bytes' in each_json:
                        if each_json.get("name") not in jvm_heap_dict.keys():
                            jvm_heap_dict[each_json.get("name")] = {"jvm_memory_used_bytes" : each_json.get("jvm_memory_used_bytes"), "jvm_memory_max_bytes" : 0}
                        else:
                            jvm_heap_dict[each_json.get("name")]['jvm_memory_used_bytes'] = each_json.get("jvm_memory_used_bytes")
                    elif 'jvm_memory_max_bytes' in each_json:
                        if each_json.get("name") not in jvm_heap_dict.keys():
                            jvm_heap_dict[each_json.get("name")] = {"jvm_memory_used_bytes" : 0, "jvm_memory_max_bytes" : each_json.get("jvm_memory_max_bytes")}
                        else:
                            jvm_heap_dict[each_json.get("name")]['jvm_memory_max_bytes'] = each_json.get("jvm_memory_max_bytes")
                
                cluster_name = each_json.get("cluster")
                
            # logging.info(f"each_es_instance_cpu_history  : {each_es_instance_cpu_history}")
            
            jvm_heap_percentage_dict = {}
            for k, v in jvm_heap_dict.items():
                jvm_usages_percentage = round((float(v.get("jvm_memory_used_bytes")) / float(v.get("jvm_memory_max_bytes")))*100.0,2)
                jvm_heap_percentage_dict.update({k : jvm_usages_percentage})

                ''' set memory for checking'''
                if each_json.get("name") not in each_es_instance_jvm_history.keys():
                    each_es_instance_jvm_history[k] = [str(jvm_usages_percentage)]
                else:
                    each_es_instance_jvm_history[k] = each_es_instance_jvm_history.get(k) + [str(jvm_usages_percentage)]
    

            # logging.info(f"get_cpu_jvm_metrics - jvm_heap_percentage_dict : {jvm_heap_percentage_dict}")
            '''
            jvm_heap_percentage_dict : {'logging-dev-node-4': 7.75, 'logging-dev-node-1': 6.99, 'logging-dev-node-2': 4.36, 'logging-dev-node-3': 7.18}
            '''
            for k, v in jvm_heap_percentage_dict.items():
                es_exporter_jvm_usage_gauge_g.labels(server_job=socket.gethostname(), type='jvm_usage', name=k, cluster=cluster_name).set(v)

            ''' get global configuration'''
            ''' initializde configuration'''
            if "config" in gloabl_configuration:
                es_cpu_percentage_threshold = gloabl_configuration.get("config").get("es_cpu_percentage_threshold")
                es_jvm_percentage_threshold = gloabl_configuration.get("config").get("es_jvm_percentage_threshold")
            else:
                es_cpu_percentage_threshold, es_jvm_percentage_threshold = 85, 85

            logging.info(f"es_cpu_percentage_threshold : {es_cpu_percentage_threshold}, es_jvm_percentage_threshold : {es_jvm_percentage_threshold}")
            logging.info(f"total_timing_history_cnt  : {total_timing_history_cnt}, each_es_instance_cpu_history : {each_es_instance_cpu_history}, each_es_instance_jvm_history : {each_es_instance_jvm_history}")


            def check_cpu_jvm_metrics(each_es_instance_history, _type):
                ''' Validate CPU/JVM Usage for the recent 5 mintues pattern'''

                usage_threashold = es_cpu_percentage_threshold if _type == "cpu" else es_jvm_percentage_threshold
                logging.info(f"check_cpu_jvm_metrics[usage_threashold] : {usage_threashold}")
                alert_nodes_dict = {}
                is_validate_all_nodes_boolean = []
                for k , v_list in each_es_instance_history.items():
                    all_usage_check = []
                    for v in v_list:
                        if is_dev_mode:
                            if float(v) > 0:
                                all_usage_check.append(True)
                            else:
                                all_usage_check.append(False)
                        else:
                            if float(v) > float(usage_threashold):
                                all_usage_check.append(True)
                            else:
                                all_usage_check.append(False)

                    if all(all_usage_check):
                        ''' save failure node with a reason into saved_failure_dict'''
                        if _type == 'cpu':
                            saved_failure_dict.update({"{}_{}".format(k, _type) : "The cpu usage of {} is {}% in Elasticsearch Cluster".format(k, "%>".join(v_list), k)})
                        else:
                            saved_failure_dict.update({"{}_{}".format(k, _type) : "The jvm usage of {} is {}% in Elasticsearch Cluster".format(k, "%> ".join(v_list), k)})
                        is_validate_all_nodes_boolean.append(True)
                        alert_nodes_dict.update({k : True})
                    else:
                        is_validate_all_nodes_boolean.append(False)
                        alert_nodes_dict.update({k : False})

                    ''' old one delete'''
                    if _type == 'cpu':
                        if len(each_es_instance_cpu_history) > 1:
                            each_es_instance_cpu_history.get(k).pop(0)
                    else:
                        if len(each_es_instance_jvm_history) > 1:
                            each_es_instance_jvm_history.get(k).pop(0)

                return any(is_validate_all_nodes_boolean), alert_nodes_dict
                            
        
            ''' initialize if lenthe of cpu_memory_buffer is greater thatn 5 minutes'''
            ''' alert check'''
            is_expected_to_cpu_down, is_expected_to_jvm_down = False, False
            
            if is_dev_mode:
                MAX_LIMIT_TIMING = 2*1
            else:
                MAX_LIMIT_TIMING = 2*5
            
            if total_timing_history_cnt > MAX_LIMIT_TIMING:
                ''' 
                {'logging-dev-node-4': '3'}
                {'logging-dev-node-1': '2'}
                {'logging-dev-node-2': '3'}
                {'logging-dev-node-3': '2'}
                '''
                ''' Validate CPU Usage for the recent 5 mintues pattern'''
                is_expected_to_cpu_down, alert_nodes_dict = check_cpu_jvm_metrics(each_es_instance_cpu_history, _type="cpu")
                logging.info(f"is_expected_to_cpu_down - {is_expected_to_cpu_down}, alert_nodes_cpu_dict : {alert_nodes_dict}")
                is_expected_to_jvm_down, alert_nodes_dict = check_cpu_jvm_metrics(each_es_instance_jvm_history, _type="jvm")
                logging.info(f"is_expected_to_jvm_down - {is_expected_to_jvm_down}, alert_nodes_jvm_dict : {alert_nodes_dict}")
                  
            return True if is_expected_to_cpu_down or is_expected_to_jvm_down else False

        except Exception as e:
            logging.error(e)
            # pass


    def get_all_envs_status(all_env_status, value, types=None, instance=None):
        ''' return all_envs_status status'''
        logging.info('type : {}, get_all_envs_status"s value - {} -> merged list : {}'.format(types, value, all_env_status))
        try:
            if types == 'kafka':
                # if value >= 2:
                if value == 3:
                    ''' green'''
                    all_env_status.append(1)
                elif value > 0 and value <1:
                    ''' yellow'''
                    all_env_status.append(0)
                else:
                    ''' red'''
                    all_env_status.append(-1)
            elif types == 'zookeeper':
                if value == 3:
                    ''' green'''
                    all_env_status.append(1)
                elif value > 0 and value <3:
                    ''' yellow'''
                    all_env_status.append(0)
                else:
                    ''' red'''
                    all_env_status.append(-1)
            elif types == 'es':
                es_node_length = len(instance.get("es_url", "").split(","))
                logging.info(f"instance : {es_node_length}")
                if value == es_node_length:
                    ''' green'''
                    all_env_status.append(1)
                elif value > 0 and value < es_node_length:
                    ''' yellow'''
                    all_env_status.append(0)
                else:
                    ''' red'''
                    all_env_status.append(-1)
            else:
                if value == 1:
                   ''' green'''
                   all_env_status.append(1)
                else:
                   ''' red'''
                   all_env_status.append(-1)
            
            return all_env_status

        except Exception as e:
            logging.error(e)

    try: 
        ''' all_envs_status : 0 -> red, 1 -> yellow, 2 --> green '''
        all_env_status_memory_list = []

        ''' clear logs'''
        saved_failure_dict.clear()

        ''' get hostname without domain'''
        hostname = socket.gethostname().split(".")[0]

        ''' if server status is yellow or red'''
        global saved_thread_alert, saved_thread_alert_message, save_thread_alert_history, saved_thread_green_alert
        global saved_status_dict, saved_failure_db_dict, saved_failure_db_kafka_dict
        global ALERT_RESENT
        global global_env_name
        global WMx_backlog, OMx_backlog

        ES_CLUSTER_RED = False

        #-- es node cluster health
        ''' http://localhost:9200/_cluster/health '''
        
        ''' The cluster health API returns a simple status on the health of the cluster. '''
        ''' get the health of the cluseter and set value based on status/get the number of nodes in the cluster'''
        ''' The operation receives cluster health results from only one active node among several nodes. '''
        resp_es_health, resp_es_basic_info = get_elasticsearch_health(monitoring_metrics)
        logging.info(f"resp_es_basic_info - {resp_es_basic_info}")
        
        if resp_es_health:
            ''' get es nodes from _cluster/health api'''
            es_nodes_gauge_g.labels(socket.gethostname()).set(int(resp_es_health['number_of_nodes']))
            es_nodes_basic_info_docs_gauge_g.labels(server_job=socket.gethostname()).set(int(resp_es_basic_info['docs']))
            es_nodes_basic_info_indices_gauge_g.labels(server_job=socket.gethostname()).set(int(resp_es_basic_info['indices']))
            if resp_es_health['status'] == 'green':
                ''' update cluster status if we have all nodes running'''
                all_env_status_memory_list = get_all_envs_status(all_env_status_memory_list,1)
                ''' save service_status_dict for alerting on all serivces'''
                service_status_dict.update({"es" : 'Green'})
                es_nodes_health_gauge_g.labels(socket.gethostname()).set(2)
                
            elif resp_es_health['status'] == 'yellow':
                ''' update cluster status if we have all nodes running'''
                all_env_status_memory_list = get_all_envs_status(all_env_status_memory_list, 0)
                ''' save service_status_dict for alerting on all serivces'''
                service_status_dict.update({"es" : 'Yellow'})
                es_nodes_health_gauge_g.labels(socket.gethostname()).set(1)
            else:
                ''' update cluster status if we have all nodes running'''
                all_env_status_memory_list = get_all_envs_status(all_env_status_memory_list, -1)
                ''' save service_status_dict for alerting on all serivces'''
                service_status_dict.update({"es" : 'Red'})
                es_nodes_health_gauge_g.labels(socket.gethostname()).set(0)

                ''' update ES status is RED'''
                ES_CLUSTER_RED = True
                   
        else:
            es_nodes_health_gauge_g.labels(socket.gethostname()).set(0)
            es_nodes_gauge_g.labels(socket.gethostname()).set(0)
            ''' update cluster status if we have empty nodes running or the status of cluster with red '''
            all_env_status_memory_list = get_all_envs_status(all_env_status_memory_list, -1)
            ''' save service_status_dict for alerting on all serivces'''
            service_status_dict.update({"es" : 'Red'})

            ''' update ES status is RED'''
            ES_CLUSTER_RED = True
        #--

        ''' Check CPU/JVM for ES'''
        is_expected_to_cpu_down = get_cpu_jvm_metrics(monitoring_metrics)
        global saved_critcal_sms_alert

        ''' alert for sms if saved_critcal_sms_alert is true'''
        if is_expected_to_cpu_down:
            all_env_status_memory_list = get_all_envs_status(all_env_status_memory_list, -1)
            saved_critcal_sms_alert = True
        else:
            saved_critcal_sms_alert = False

        ''' Clear the disk space for ES through audit alert'''
        nodes_diskspace_gauge_g._metrics.clear()
        nodes_free_diskspace_gauge_g._metrics.clear()

        ''' Check the disk space for ES through audit alert'''
        is_audit_alert_es = get_elasticsearch_disk_audit_alert(monitoring_metrics)
        if is_audit_alert_es:
            all_env_status_memory_list = get_all_envs_status(all_env_status_memory_list, -1)

        ''' Check the disk space for Kafka through audit alert'''
        is_audit_alert_kafka = get_kafka_disk_audit_alert(monitoring_metrics)
        if is_audit_alert_kafka:
            all_env_status_memory_list = get_all_envs_status(all_env_status_memory_list, -1)

        ''' export maximum disk used'''
        logging.info(f"max_disk_used - {max_disk_used}")
        nodes_max_disk_used_gauge_g._metrics.clear()

        ''' export max all nodes with es/kafka'''
        # nodes_max_disk_used_gauge_g.labels(server_job=socket.gethostname()).set(float(max_disk_used))

        ''' expose each max disk usage'''
        nodes_max_disk_used_gauge_g.labels(server_job=socket.gethostname(), category="max_es_disk_used").set(float(max_es_disk_used))
        nodes_max_disk_used_gauge_g.labels(server_job=socket.gethostname(), category="max_kafka_disk_used").set(float(max_kafka_disk_used))
        

        ''' check the status of nodes on all kibana/kafka/connect except es nodes by using socket '''
        ''' The es cluster is excluded because it has already been checked in get_elasticsearch_health function'''
        monitoring_metrics_cp = copy.deepcopy(monitoring_metrics)
        # del monitoring_metrics_cp["es_url"]
        logging.info("monitoring_metrics_cp - {}".format(json.dumps(monitoring_metrics_cp, indent=2)))

        ''' socket.connect_ex( <address> ) similar to the connect() method but returns an error indicator of raising an exception for errors '''
        ''' The error indicator is 0 if the operation succeeded, otherwise the value of the errno variable. '''
        ''' Kafka/Kafka connect/Spark/Kibana'''
        
        response_dict = get_service_port_alive(monitoring_metrics_cp)
        logging.info(f"response_dict - {response_dict}")

        ''' Kafka Health'''
        kafka_nodes_gauge_g.labels(socket.gethostname()).set(int(response_dict["kafka_url"]["GREEN_CNT"]))

        '''
        # printout Kafka_Connect
        response_dict["kafka_connect_url"]  {'localhost1:8083': 'OK', 'GREEN_CNT': 3, 'localhost2:8083': 'OK', 'localhost3:8083': 'OK'}
        '''
        ''' extract master node from kafka hosts'''
        master_kafka = monitoring_metrics.get("kafka_url").split(",")[0]
        master_kafka = master_kafka.split(':')[0]
        is_flag_active_primary_node_for_kafka_connect = True
        ''' Get the status of primary node from the Kafka connect such as OK or FAIL'''
        if "{}:8083".format(master_kafka) in response_dict["kafka_connect_url"]:
            master_kafka_active = response_dict["kafka_connect_url"]["{}:8083".format(master_kafka)]

        else:
            master_kafka_active = "FAIL"
            is_flag_active_primary_node_for_kafka_connect = False

        # print('\n\n\n\n')
        # print('response_dict["kafka_connect_url"] ', response_dict["kafka_connect_url"])
        # print('Master of Kafka connect : {}'.format(master_kafka_active))
        # print('\n\n\n\n')
        
        ''' Kafka connect node update'''
        ''' As long as Kafka Connect is running on the primary node, this is fine since it’s not mandatory for Connect to be running on nodes 2,3.'''
        kafka_connect_nodes_gauge_g.labels(socket.gethostname()).set(int(response_dict["kafka_connect_url"]["GREEN_CNT"]))
        ''' update health of Kafka connect'''
        if master_kafka_active == "OK":
            ''' If Kafka Connect is not running on node #2 or node #3 or a combination of both nodes #2 and #3, then the color code check should show as yellow if Kafka Connect is running on the primary node (node 1).'''
            kafka_connect_nodes_health_gauge_g.labels(socket.gethostname()).set(int(response_dict["kafka_connect_url"]["GREEN_CNT"]))
        else:
            ''' If Kafka Connect is not running on the primary node, then the color code check should show as “red” since this means data is not being processed for our ES pipeline queue for WMx and OMx. '''
            kafka_connect_nodes_health_gauge_g.labels(socket.gethostname()).set(0)
            
        ''' zookeeper node update'''
        zookeeper_nodes_gauge_g.labels(socket.gethostname()).set(int(response_dict["zookeeper_url"]["GREEN_CNT"]))
        
        ''' Update the status of kibana instance by using socket.connect_ex'''
        # es_nodes_gauge_g.labels(socket.gethostname()).set(int(response_dict["es_url"]["GREEN_CNT"]))
        kibana_instance_gauge_g.labels(socket.gethostname()).set(int(response_dict["kibana_url"]["GREEN_CNT"]))

        ''' alert state'''
        if global_mail_configuration.get(hostname).get('is_mailing',''):
            alert_state_instance_gauge_g.labels(server_job=socket.gethostname()).set(1)
        else:
            alert_state_instance_gauge_g.labels(server_job=socket.gethostname()).set(0)

        ''' Update the status of Redis service by using socket.connect_ex only Dev'''
        if 'redis_url' in monitoring_metrics:
            active_cnt = int(response_dict["redis_url"]["GREEN_CNT"])
            ''' Red is 2'''
            if active_cnt < 1:
                active_cnt = 2
            redis_instance_gauge_g.labels(socket.gethostname()).set(active_cnt)

        ''' Update the status of ES Confiuration write job service by using socket.connect_ex only Dev'''
        if 'configuration_job_url' in monitoring_metrics:
            active_cnt = int(response_dict["configuration_job_url"]["GREEN_CNT"])
            ''' Red is 2'''
            if active_cnt < 1:
                active_cnt = 2
            es_configuration_instance_gauge_g.labels(socket.gethostname()).set(active_cnt)

        ''' Update the status of ES Confiuration API service by using socket.connect_ex only Dev'''
        if 'es_configuration_api_url' in monitoring_metrics:
            active_cnt = int(response_dict["es_configuration_api_url"]["GREEN_CNT"])
            ''' Red is 2'''
            if active_cnt < 1:
                active_cnt = 2
            es_configuration_api_instance_gauge_g.labels(socket.gethostname()).set(active_cnt)

        ''' Update the status of LOG DB URL by using socket.connect_ex only Dev'''
        if 'log_db_url' in monitoring_metrics:
            active_cnt = int(response_dict["log_db_url"]["GREEN_CNT"])
            ''' Red is 2'''
            if active_cnt < 1:
                active_cnt = 2
            log_db_instance_gauge_g.labels(socket.gethostname()).set(active_cnt)

        ''' Update the status of Alert Monitoring URL by using socket.connect_ex only Dev'''
        if 'alert_monitoring_url' in monitoring_metrics:
            active_cnt = int(response_dict["alert_monitoring_url"]["GREEN_CNT"])
            ''' Red is 2'''
            if active_cnt < 1:
                active_cnt = 2
            alert_monitoring_ui_gauge_g.labels(socket.gethostname()).set(active_cnt)

        # ''' Update the status of Apache Loki URL by using socket.connect_ex only Dev'''
        # if 'loki_url' in monitoring_metrics:
        #     active_cnt = int(response_dict["loki_url"]["GREEN_CNT"])
        #     ''' Red is 2'''
        #     if active_cnt < 1:
        #         active_cnt = 2
        #     loki_ui_gauge_g.labels(socket.gethostname()).set(active_cnt)

        # ''' Update the status of Loki interface API service by using socket.connect_ex only Dev'''
        # if 'loki_api_url' in monitoring_metrics:
        #     active_cnt = int(response_dict["loki_api_url"]["GREEN_CNT"])
        #     ''' Red is 2'''
        #     if active_cnt < 1:
        #         active_cnt = 2
        #     loki_api_instance_gauge_g.labels(socket.gethostname()).set(active_cnt)

        ''' Update the status of loki_custom_promtail_agent_url agent by using socket.connect_ex only Dev'''
        # if 'loki_custom_promtail_agent_url' in monitoring_metrics:
        #     active_cnt = int(response_dict["loki_custom_promtail_agent_url"]["GREEN_CNT"])
        #     ''' 'loki_custom_promtail_agent_url': {'localhost1:2000': 'FAIL', 'GREEN_CNT': 0, 'localhost2:2000': 'FAIL', 'localhost3:2000': 'FAIL'}} '''
        #     ''' expose each max disk usage'''
        #     ''' loki_agent_instance_gauge_g = Gauge("loki_agent_health_metric", 'Metrics scraped from localhost', ["server_job", "category"]) '''
        #     loki_agent_instance_gauge_g.clear()
        #     for k, v in response_dict["loki_custom_promtail_agent_url"].items():
        #         if k != 'GREEN_CNT':
        #             loki_agent_instance_gauge_g.labels(server_job=socket.gethostname(), category=str(k)).set(1 if v == 'OK' else 2)
        
        ''' Update the status of log_aggregation_agent_url agent by using socket.connect_ex only Dev'''
        if 'log_aggregation_agent_url' in monitoring_metrics:
            active_cnt = int(response_dict["log_aggregation_agent_url"]["GREEN_CNT"])
            ''' 'log_aggregation_agent_url': {'localhost1:2000': 'FAIL', 'GREEN_CNT': 0, 'localhost2:2000': 'FAIL', 'localhost3:2000': 'FAIL'}} '''
            ''' log_agent_instance_gauge_g = Gauge("log_agent_health_metric", 'Metrics scraped from localhost', ["server_job", "category"]) '''
            log_agent_instance_gauge_g.clear()
            """
            for k, v in response_dict["log_aggregation_agent_url"].items():
                if k != 'GREEN_CNT':
                    log_agent_instance_gauge_g.labels(server_job=socket.gethostname(), category=str(k)).set(1 if v == 'OK' else 2)
            """

            list_of_data_transfer_nodes = monitoring_metrics.get("log_aggregation_agent_url").split(",")
            for each_dt in list_of_data_transfer_nodes:
                socket_dt = str(each_dt).split(":")[0]

                try:
                    logging.info(f"log_aggregation_agent_url socket client : {each_dt}")
                    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    client_socket.settimeout(1)
                    client_socket.connect((socket_dt, 2000))

                    ''' Gather the status of filebeat on each data transfer node'''
                    data = str.encode("ps ax | grep -i '/filebeat.yml' | grep -v grep | awk '{print $1}'")
                    # data = str.encode("test")
                    client_socket.sendall(data)

                    received = client_socket.recv(1024)
                    received = str(received.decode('utf-8'))
                    print(f"# socket client received.. {received}")
                    log_agent_instance_gauge_g.labels(server_job=socket.gethostname(), category=str(each_dt)).set(1 if received else 2)
                            
                except Exception as e:
                    logging.error(f"log_aggregation_agent_url error : {e}")
                    log_agent_instance_gauge_g.labels(server_job=socket.gethostname(), category=str(each_dt)).set(2)
                    pass
                        
                finally:
                    print("Closing socket")
                    client_socket.close()
                 

        ''' ********* Server Active Graph ******************** '''

        ''' first node of --kafka_url argument is a master node to get the number of jobs using http://localhost:8080/json '''
        ''' To receive spark job lists, JSON results are returned from master node 8080 port. ''' 
        ''' From the results, we get the list of spark jobs in activeapps key and transform them to metrics for exposure. '''
        # -- Get spark jobs
        response_spark_jobs = get_spark_jobs(monitoring_metrics.get("kafka_url", ""))

        ''' save service_status_dict for alerting on all serivces'''
        spark_status = 'Green' if response_spark_jobs else 'Red'
        service_status_dict.update({"spark" : spark_status})
        service_status_dict.update({"spark_custom_apps" : len(response_spark_jobs) if response_spark_jobs else 0})

        ''' update the name of active jobs in spark cluster '''
        custom_apps = [each_apps_json.get("name") for each_apps_json in response_spark_jobs]
        service_status_dict.update({"spark_custom_apps_list" : ",".join(custom_apps) if custom_apps else ""})

        ''' extract master node from spark hosts'''
        master_spark = monitoring_metrics.get("kafka_url").split(",")[0]
        master_spark = master_spark.split(':')[0]

        ''' update a list of spark custom apps to table grid in grafana'''
        spark_jobs_gauge_g._metrics.clear()
        if response_spark_jobs: 
            ''' list of spark jobs shows'''
            # spark_jobs_gauge_g
            for each_job in response_spark_jobs:
                duration = str(round(float(each_job["duration"])/(60.0*60.0*1000.0),2)) + " h" if 'duration' in each_job else -1
                # logging.info(duration)
                for k, v in each_job.items():
                    if k  == 'state':
                        if v.upper() == 'RUNNING':
                            spark_jobs_gauge_g.labels(server_job=socket.gethostname(), host="{}{}".format(str(global_env_name).lower(), master_spark), id=each_job.get('id',''), cores=each_job.get('cores',''), memoryperslave=each_job.get('memoryperslave',''), submitdate= each_job.get('submitdate',''), duration=duration, activeapps=each_job.get('name',''), state=each_job.get('state','')).set(1)
                        else:
                            spark_jobs_gauge_g.labels(server_job=socket.gethostname(), host="{}{}".format(str(global_env_name).lower(), master_spark), id=each_job.get('id',''), cores=each_job.get('cores',''), memoryperslave=each_job.get('memoryperslave',''), submitdate= each_job.get('submitdate',''), duration=duration, activeapps=each_job.get('name',''), state=each_job.get('state','')).set(0)
                    
        else:
            ''' all envs update for current server active'''
            ''' all_env_status_memory_list -1? 0? 1? at least one?'''
            ''' master node spark job is not running'''
            all_env_status_memory_list = get_all_envs_status(all_env_status_memory_list, -1, types='spark')

        # -- Get connect listeners
        '''
            {
                "localhost1": [
                  {
                    "name": "test_jdbc",
                    "connector": {
                        "state": "RUNNING",
                        "worker_id": "localhost:8083"
                    },
                    "tasks": [
                        {
                        "state": "RUNNING",
                        "id": 0,
                        "worker_id": "localhost:8083"
                        }
                    ]
                  }
                ],
                "localhost2": {},
                "localhost3": {}
            }
        '''

        ''' First, this operation receives results from one active node to find out the listenen list through 8083 port with connectos endpoint (http://localhost:8083/connectors/) '''
        ''' then, each kafka node receives json results from port 8083 to check the status of kafka listener. '''
        ''' As a result, it is checked whether each listener is running normally. '''
        ''' Prometheus periodically takes exposed metrics and exposes them on the graph. '''
        response_listeners, failure_check = get_kafka_connector_listeners(monitoring_metrics.get("kafka_url", ""))
        kafka_connect_listeners_gauge_g._metrics.clear()
        is_running_one_of_kafka_listner = False
        any_failure_listener = True
        host_list = []
        ''' kafka Connect health'''
        kafka_state_list = []
        if response_listeners: 
            for host in response_listeners.keys():
                loop = 0
                host_list.append(host)
                for element in response_listeners[host]:
                    if 'error_code' in element:
                        kafka_state_list.append(-1)
                        continue
                    else:
                        if len(element['tasks']) > 0:
                            if element['tasks'][0]['state'].upper() == 'RUNNING':
                                kafka_state_list.append(1)
                                is_running_one_of_kafka_listner = True
                                kafka_connect_listeners_gauge_g.labels(server_job=socket.gethostname(), host="{}{}".format(str(global_env_name).lower(), host), name=element.get('name',''), running=element['tasks'][0]['state']).set(1)
                            else:
                                kafka_state_list.append(-1)
                                kafka_connect_listeners_gauge_g.labels(server_job=socket.gethostname(), host="{}{}".format(str(global_env_name).lower(), host), name=element.get('name',''), running=element['tasks'][0]['state']).set(0)
                                ''' add tracking logs'''
                                if 'trace' in  element['tasks'][0]:
                                    saved_failure_dict.update({"{}_{}".format(host, str(loop)) : "http://{}:8083 - ".format(host) + element.get('name','') + "," + element['tasks'][0]['trace']})
                                else:
                                    saved_failure_dict.update({"{}_{}".format(host, str(loop)) : "http://{}:8083 - ".format(host) + element.get('name','') + "," + element['tasks'][0]['state'].upper()})
                                any_failure_listener = False
                                loop += 1

        else:
            ''' all envs update for current server active'''
            ''' all_env_status_memory_list -1? 0? 1? at least one?'''
            ''' master node spark job is not running'''
            all_env_status_memory_list = get_all_envs_status(all_env_status_memory_list, -1, types='kafka_listner')

        if failure_check:
            all_env_status_memory_list = get_all_envs_status(all_env_status_memory_list, -1, types='kafka_listner')


        logging.info(f"is_running_one_of_kafka_listner - {is_running_one_of_kafka_listner}, host_list : {host_list}")

        ''' get all kafka hosts'''
        kafka_node_hosts = monitoring_metrics.get("kafka_url", "").split(",")
        logging.info(f"kafka_node_hosts - {kafka_node_hosts}")

        if kafka_node_hosts:
            kafka_nodes_list = [node.split(":")[0] for node in kafka_node_hosts]
        else:
            kafka_nodes_list = ""

        logging.info(f"get all kafka hosts - {kafka_nodes_list}")
        ''' add tracking'''
        if not is_running_one_of_kafka_listner:
            ''' all envs update for current server active'''
            ''' all_env_status_memory_list -1? 0? 1? at least one?'''
            all_env_status_memory_list = get_all_envs_status(all_env_status_memory_list, -1, types='kafka_listner')
            saved_failure_dict.update({",".join(kafka_nodes_list) : "[KAFKA CONNECT] All Kafka Listeners are not running.."})

        ''' add tracking'''
        ''' if one of listener is not running with running status'''
        if not any_failure_listener:
            all_env_status_memory_list = get_all_envs_status(all_env_status_memory_list, -1, types='kafka_listner')


        '''  kafka Connect health Set if listeners are working on all nodes with state of RUNNING'''
        '''  Kafka_Health : [1, 1, 1, 1, 1, 1] '''
        """
        logging.info(f"Kafka_Health : {kafka_state_list}")
        if list(set(kafka_state_list)) == [1]:
            kafka_connect_health_gauge_g.labels(server_job=socket.gethostname()).set(3)
        elif list(set(kafka_state_list)) == [-1] or len(kafka_state_list) < 1:
            kafka_connect_health_gauge_g.labels(server_job=socket.gethostname()).set(0)
        else:
            kafka_connect_health_gauge_g.labels(server_job=socket.gethostname()).set(1)
        """

        ''' get Kafka ISR metrics'''
        # get_kafka_ISR_metrics()

      
        ''' pgrep -f logstash to get process id'''
        ''' set 1 if process id has value otherwise set 0'''
        # -- local instance based
        logstash_instance_gauge_g.labels(socket.gethostname()).set(int(get_Process_Id()))

        ''' all envs update for current server active'''
        ''' all_env_status_memory_list -1? 0? 1? at least one?'''
        logging.info(f"all_envs_status #ES : {all_env_status_memory_list}")

        ''' Update alert infomration for nodes'''
        ''' --- ES Health ---'''
        ''' update server active status for ES using Port Scan (It can't be exact the number of nodes through ES Cluster API when first node went down)'''
        all_env_status_memory_list = get_all_envs_status(all_env_status_memory_list,int(response_dict["es_url"]["GREEN_CNT"]), types='es', instance=monitoring_metrics)
        ''' update es_nodes'''
        service_status_dict.update({"es_nodes" : int(response_dict["es_url"]["GREEN_CNT"])})
        ''' --- '''
        MAX_NUMBERS = len(monitoring_metrics.get("kafka_url").split(","))
        ''' update server active status for Kafka'''
        all_env_status_memory_list = get_all_envs_status(all_env_status_memory_list, int(response_dict["kafka_url"]["GREEN_CNT"]), types='kafka')
        ''' save service_status_dict for alerting on all serivces'''
        if int(response_dict["kafka_url"]["GREEN_CNT"]) == MAX_NUMBERS:
            kafka_status = 'Green' 
        elif 0 < int(response_dict["kafka_url"]["GREEN_CNT"]) < MAX_NUMBERS:
            kafka_status = 'Yellow' 
        else:
            kafka_status = 'Red'
        service_status_dict.update({"kafka" : kafka_status})
        ''' update kafka_nodes'''
        service_status_dict.update({"kafka_nodes" : int(response_dict["kafka_url"]["GREEN_CNT"])})
        
        '''  ******  Kafka Connect Health ****************'''
        MAX_NUMBERS = len(monitoring_metrics.get("kafka_connect_url").split(","))

        ''' Update Server Active status for Kafka Connect'''
        ''' *** if this line is enabled, it will be checked the status if all Kafak nodes are active based on the number of active nodes'''
        # all_env_status_memory_list = get_all_envs_status(all_env_status_memory_list, int(response_dict["kafka_connect_url"]["GREEN_CNT"]), types='kafka')
        
        ''' Update Server Active status for Kafka Connect'''
        kafka_connect_status_primary_node = 'Green'
        if is_flag_active_primary_node_for_kafka_connect:
            ''' Update the status of Kafka connect to Server active for alert -> set the value as three nodes if master node is active'''
            all_env_status_memory_list = get_all_envs_status(all_env_status_memory_list, len(monitoring_metrics.get("kafka_url").split(",")), types='kafka')
        else:
            kafka_connect_status_primary_node = 'Red'
            all_env_status_memory_list = get_all_envs_status(all_env_status_memory_list, int(response_dict["kafka_connect_url"]["GREEN_CNT"]), types='kafka')
        
        service_status_dict.update({"kafka_connect_primary_node" : kafka_connect_status_primary_node})

        ''' save service_status_dict for alerting on all serivces'''
        if int(response_dict["kafka_connect_url"]["GREEN_CNT"]) == MAX_NUMBERS:
            kafka_connect_status = 'Green' 
        elif 0 < int(response_dict["kafka_connect_url"]["GREEN_CNT"]) < MAX_NUMBERS and is_flag_active_primary_node_for_kafka_connect:
            kafka_connect_status = 'Yellow' 
        elif 0 < int(response_dict["kafka_connect_url"]["GREEN_CNT"]) < MAX_NUMBERS and not is_flag_active_primary_node_for_kafka_connect:
            kafka_connect_status = 'Red' 
        else:
            kafka_connect_status = 'Red'
        service_status_dict.update({"kafka_connect" : kafka_connect_status})
        ''' update kafka_connect_nodes'''
        service_status_dict.update({"kafka_connect_nodes" : int(response_dict["kafka_connect_url"]["GREEN_CNT"])})
        '''  ******  Kafka Connect Health ****************'''

        ''' update server active status for Zookeeper'''
        MAX_NUMBERS = len(monitoring_metrics.get("zookeeper_url").split(","))
        all_env_status_memory_list = get_all_envs_status(all_env_status_memory_list, int(response_dict["zookeeper_url"]["GREEN_CNT"]), types='zookeeper')
        
        ''' save service_status_dict for alerting on all serivces'''
        ''' two of zookeepr can support the service'''
        if int(response_dict["zookeeper_url"]["GREEN_CNT"]) == MAX_NUMBERS:
            zookeeper_status = 'Green' 
        elif 0 < int(response_dict["zookeeper_url"]["GREEN_CNT"]) < MAX_NUMBERS:
            zookeeper_status = 'Yellow' 
        else:
            zookeeper_status = 'Red'
        service_status_dict.update({"zookeeper" : zookeeper_status})
        ''' update zookeeper_nodes'''
        service_status_dict.update({"zookeeper_nodes" : int(response_dict["zookeeper_url"]["GREEN_CNT"])})

        ''' update server active status for Kibana'''
        all_env_status_memory_list = get_all_envs_status(all_env_status_memory_list, int(response_dict["kibana_url"]["GREEN_CNT"]), types='kibana')
        ''' save service_status_dict for alerting on all serivces'''
        kibana_status = 'Green' if int(response_dict["kibana_url"]["GREEN_CNT"]) > 0 else 'Red'
        service_status_dict.update({"kibana" : kibana_status})

        ''' update server active status for Logstash'''
        all_env_status_memory_list = get_all_envs_status(all_env_status_memory_list, int(get_Process_Id()), types='logstash')
        ''' save service_status_dict for alerting on all serivces'''
        logstash_status = 'Green' if int(get_Process_Id()) > 0 else 'Red'
        service_status_dict.update({"logstash" : logstash_status})

        logging.info(f"all_envs_status #All : {all_env_status_memory_list}")
        ''' --- '''

        ''' ----------------------------------------------------- '''
        ''' Set Server Active Graph'''
        ''' set value for node instance '''
        global_service_active = False

        if list(set(all_env_status_memory_list)) == [1]:
            ''' green '''
            all_envs_status_gauge_g.labels(server_job=socket.gethostname(), type='cluster').set(1)
            saved_status_dict.update({'server_active' : 'Green'})
            global_service_active = True
            logging.info(f"SERVER ACTIVE : Green")
        
        elif list(set(all_env_status_memory_list)) == [-1]:
            ''' red '''
            all_envs_status_gauge_g.labels(server_job=socket.gethostname(), type='cluster').set(3)
            ''' update gloabl variable for alert email'''
            saved_status_dict.update({'server_active' : 'Red'})
            logging.info(f"SERVER ACTIVE : Red")

        else:
            ''' yellow '''
            all_envs_status_gauge_g.labels(server_job=socket.gethostname(), type='cluster').set(2)
            ''' update gloabl variable for alert email'''
            saved_status_dict.update({'server_active' : 'Yellow'})
            logging.info(f"SERVER ACTIVE : Yellow")
            
        ''' all envs update for current data pipeline active --> process in db_jobs_work function'''
        ''' ----------------------------------------------------- '''


        ''' expose failure node with a reason'''
        logging.info(f"[metrtics] saved_failure_dict - {saved_failure_dict}")
        logging.info(f"global_db_configuration [{hostname}] - {json.dumps(global_mail_configuration.get(hostname), indent=2)}")
        logging.info(f"[db] saved_failure_db_dict - {saved_failure_db_dict}")
        
        def remove_special_char(input_str):
            ''' remove special char'''
            special_char = '_'
            if special_char not in input_str:
                return input_str
            
            return str(input_str).split(special_char)[0]

        ''' Warning logs clear'''
        es_service_jobs_failure_gauge_g._metrics.clear()

        """ create alert audit message"""        
        failure_message = []
        
        """ create alert audit message & Update log metrics"""
        ''' merge'''
        saved_failure_dict.update(saved_failure_tasks_dict)
        # saved_failure_dict = {k: v for k, v in sorted(saved_failure_dict.items(), key=lambda item: item[0])}
        for k, v in saved_failure_dict.items():
            es_service_jobs_failure_gauge_g.labels(server_job=socket.gethostname(),  host="{}{}".format(str(global_env_name).lower(), remove_special_char(k)), reason=v).set(0)
            ''' remove waring logs for the alert if our service is online'''
            if not global_service_active:
                failure_message.append(v)
            # failure_message.append(v)
        

        ''' db threads for kafka offset'''
        # for k, v in saved_failure_db_kafka_dict.items():
        #     ''' host_ remove'''
        #     es_service_jobs_failure_gauge_g.labels(server_job=socket.gethostname(), host=remove_special_char(k), reason=v).set(0)
        #     failure_message.append(v)

        
        ''' db threads'''
        for k, v in saved_failure_db_dict.items():
            ''' host_ remove'''
            es_service_jobs_failure_gauge_g.labels(server_job=socket.gethostname(), host=remove_special_char(k), reason=v).set(0)
            failure_message.append(v)

        ''' ------------------------------------------------------'''
        ''' send an email these warning message if the status of env has an yellow or red'''
        # email_list = os.environ["EMAIL_LIST"]
        # logging.info(f"mail_list from shell script: {email_list}")
        
        # ''' if server status is yellow or red'''
        # global saved_thread_alert, saved_thread_alert_message, save_thread_alert_history, saved_thread_green_alert
        
        ''' Checking save_thread_alert_history '''
        if len(save_thread_alert_history) > 1:
            ''' Issue has occured and now the issue was resolved '''
            if save_thread_alert_history == [True, False]:
                saved_thread_green_alert = True
            elif save_thread_alert_history == [False, False]:
                saved_thread_green_alert = False
            
            save_thread_alert_history.pop(0)
        
        ''' one of services is inactive or any issue with data pieplines or any issue with Kakfa offset like out of range from the kafak offset'''
        # if not list(set(all_env_status_memory_list)) == [1] or saved_failure_db_dict or saved_failure_db_kafka_dict:
        if not list(set(all_env_status_memory_list)) == [1] or saved_failure_db_dict:
            ''' if failure mesage has something'''
            if failure_message:
                saved_thread_alert = True
                saved_thread_alert_message = failure_message

                ''' Whenever app does check for the alerts every 10 minutes, sends the first alert, and then resends the alert after 1 hour.'''
                get_alert_resend(False)
    
                ''' add history for alerting '''
                save_thread_alert_history.append(True)
        else:
            saved_thread_alert = False
            ''' add history for alerting '''
            save_thread_alert_history.append(False)

            ''' Update thread_alert_message if save_thread_alert is green'''
            # tracking_failure_dict.update({"alert_sent_time" : "1900-01-01 00:00:00"})

        ''' ------------------------------------------------------'''
      
        # logging.info(f"saved_thread_alert - {saved_thread_alert}, saved_critcal_sms_alert - {saved_critcal_sms_alert}")
        logging.info(f"save_thread_alert_history - {save_thread_alert_history}")
        logging.info(f"saved_status_dict - {json.dumps(saved_status_dict, indent=2)}")
        logging.info(f"service_status_dict - {json.dumps(service_status_dict, indent=2)}")
        logging.info(f"WMx_threads_db_active - {WMx_threads_db_active}, OMx_threads_db_active : {OMx_threads_db_active}")
        logging.info(f"Mail Alert mail Configuration - {global_mail_configuration.get(hostname).get('is_mailing','')}, Mail Alert SMS Configuration : {global_mail_configuration.get(hostname).get('is_sms','')}")
        logging.info(f"global_es_shards_tasks_end_occurs_unassgined - {global_es_shards_tasks_end_occurs_unassgined}")
        logging.info(f"global_OUT_OF_ALERT_TIME : {global_OUT_OF_ALERT_TIME}, global_TIME_STAMP : {global_TIME_STAMP}, global_out_of_alert_time_range - {global_out_of_alert_time_range}")
        logging.info(f"global_es_configuration_host : {global_es_configuration_host}, global_env_name - {global_env_name}")
        logging.info(f"current_alert_message : {saved_thread_alert_message}")
        logging.info(f"alert_job's started time : {ALERT_STARTED_TIME}")
        logging.info(f"tracking_failure_dict : {tracking_failure_dict}, saved_thread_alert : {saved_thread_alert}, alert_duration_time : {ALERT_DURATION}, alert_resent_flag on Main Process : {ALERT_RESENT}")
        logging.info(f"save_thread_alert_history : {save_thread_alert_history}")
        logging.info(f"WMx_backlog : {WMx_backlog}, OMx_backlog : {OMx_backlog}, db_transactin_time_WMx : {db_transactin_time_WMx}, db_transactin_time_OMx : {db_transactin_time_OMx}")
        logging.info(f"recheck_WMx : {recheck_WMx}, WMx_backlog_list : {WMx_backlog_list}")
        
        ''' Service are back online and push them into Grafana-Loki '''
        if saved_thread_green_alert:
            """ # Grafana-Loki Log """
            logger.info("Prometheus-Monitoring-Service - [{}] Services are back online".format(global_env_name),
                                    extra={"tags": {"service": "prometheus-monitoring-service", "message" : "[{}] Services, Alert : {}".format(
                                        global_env_name,
                                        saved_thread_alert
                                        ), 
                                        "env" : "{}".format(global_env_name), 
                                        }},
                    )
           

        ''' ----------------------'''
        ''' SMS alert imediately'''
        ''' Send sms alerts to our team when the usage of CPU/JVM is over 85% for 5 minutes or (ES Service/Data pipeline has at least Yellow)'''
        ''' think how to handle this text alert if autostart script is running eveery 1 minutes'''
        """
        if ES_CLUSTER_RED:
            saved_critcal_sms_alert = True
            saved_thread_alert_message.append("The Status of ES cluster is RED")
            logging.info(f"Sending SMS for ES status")
            alert_to_text(global_mail_configuration, hostname, global_mail_configuration.get(hostname).get("sms_list",""), saved_status_dict, immediately=True)
        else:
            saved_critcal_sms_alert = False
        """
        ''' ----------------------'''
      

    except Exception as e:
        logging.error(f"main get all env : {e}")
        pass
        

''' global mememoy'''
global_es_shards_tasks_end_occurs_unassgined = False
global_out_of_alert_time_range = False
global_TIME_STAMP,  global_OUT_OF_ALERT_TIME = '', ''

''' alert message to mail with interval?'''
saved_thread_alert = False
saved_thread_green_alert = False
save_thread_alert_history = []

saved_thread_alert_message = []
saved_status_dict = {}
service_status_dict = {}

saved_critcal_sms_alert = False


''' dict memory for db failrue'''
saved_failure_db_dict = {}
saved_failure_db_kafka_dict = {}

''' Tracking thread_alert_message '''
tracking_failure_dict = {
    "alert_sent_time" : "1900-01-01 00:00:00"
}


import threading
lock = threading.Lock()

''' DB_DATA_PIPELINE_MULTILE_THREADS'''
WMx_threads_db_active, OMx_threads_db_active = True, True
WMx_threads_db_Kafka_offset_active = True

''' Threshold'''
DATA_PIPELINE_THRESHOLD = 0.505
KAFKA_OFFSET_EDITTS_UPDATED_THRESHOLD = 0.1

''' Backlog '''
WMx_backlog, OMx_backlog = 0, 0


''' Team does not wont to monitor this metrics for DB performace'''
def db_jobs_kafka_offset_tb(interval, database_object, sql, db_http_host, db_url):
    ''' 
    The “spark” user as it processes data for upload into ES, also updates DB table (only in the WMx DB) named “kafka_offsets”. 
    If we notice the “editts” is not current for a given partition, 
    we run the command to obtain the Kafka Offsets from the primary “data transfer node”, 
    We may have an issue with the offsets not being updated correctly which can be causing the issue with some records not being processed correctly. 
    I’m going to reset all Kafka offsets for env.
    '''
    global saved_failure_db_kafka_dict, WMx_threads_db_active, OMx_threads_db_active, WMx_threads_db_Kafka_offset_active

    while True:
        try:
            StartTime = datetime.datetime.now()

            ''' initialize'''
            saved_failure_db_kafka_dict.clear()

            ''' all status are active and clear failure dict for DB'''
            if WMx_threads_db_active and OMx_threads_db_active and WMx_threads_db_Kafka_offset_active:
                saved_status_dict.clear()
            
            if db_http_host:
                '''  retrieve records from DB interface REST API URL using requests library'''
                logging.info("# HTTP Interface")

                ''' call to DB interface RestAPI'''
                request_body = {
                            "db_url" : db_url,
                            "sql" : sql
                }

                logging.info("db_http_host : {}, db_url : {}, sql : {}".format(db_http_host, db_url, sql))
                http_urls = "http://{}/db/get_db_query".format(db_http_host)
                resp = requests.post(url=http_urls, json=request_body, timeout=600)
                    
                if not (resp.status_code == 200):
                    db_jobs_gauge_kafka_offset_wmx_g._metrics.clear()
                    saved_failure_db_kafka_dict.update({'db-jobs-{}_{}'.format("WMx","Kafka_Offset") : "{} db -> ".format(resp.json()['message'])})
                    all_envs_status_gauge_g.labels(server_job=socket.gethostname(), type='data_pipeline').set(2)
                    saved_status_dict.update({'es_pipeline' : 'Red'})
                    logging.info(f"saved_failure_db_kafka_dict in 404 response - {saved_failure_db_kafka_dict}, saved_status_dict - {saved_status_dict}")
                    WMx_threads_db_Kafka_offset_active = False
                    continue

                logging.info(f"db/process_table - {resp}")
                ''' db job performance through db interface restapi'''
                result_json_value = resp.json()["results"]
            
            else:
                ''' This logic perform to connect to DB directly and retrieve records from processd table '''
                logging.info("# DB Interface Directly")
                result_json_value = database_object.excute_oracle_query(sql)

            ''' DB processing time '''
            EndTime = datetime.datetime.now()

            Delay_Time_OMx = str((EndTime - StartTime).seconds) + '.' + str((EndTime - StartTime).microseconds).zfill(6)[:2]
            logging.info("# [db_jobs_kafka_offset_tb] HTTP Rest DB Query Running Time - {}".format(str(Delay_Time_OMx)))

            ''' get EDDITS fiel from Kafak_Offset table in WMx DB'''
            ''' db_jobs_gauge_kafka_offset_wmx_g = Gauge("db_jobs_wmx_kafka_offset_running_metrics", 'Metrics scraped from localhost', ["server_job", "topic",  "partition_num", "offset", "addts", "addwho", "editts", "editwho", "dbid"]) '''
            db_jobs_gauge_kafka_offset_wmx_g._metrics.clear()
            
            is_updated_editts_offset = True
            not_updated_offset_list = []
            if result_json_value:
                 for element_each_json in result_json_value:
                    ''' --------------'''
                    ''' update process name with time difference'''
                    # Calculate the time gap
                    audit_process_name_time = datetime.datetime.strptime(element_each_json.get("EDITTS",""), "%Y-%m-%d %H:%M:%S")
                    # audit_process_name_time = datetime.datetime.strptime("2024-09-04 17:02:00", "%Y-%m-%d %H:%M:%S")
                    time_difference_to_hours = get_time_difference(audit_process_name_time)
                    ''' --------------'''
                    
                    ''' Check the threshold about 5 minutes'''
                    if time_difference_to_hours > KAFKA_OFFSET_EDITTS_UPDATED_THRESHOLD:
                        is_updated_editts_offset = False
                        not_updated_offset_list.append(str(element_each_json.get("PARTITION_NUM")))
                        db_jobs_gauge_kafka_offset_wmx_g.labels(server_job=socket.gethostname(), topic=element_each_json['TOPIC'], partition_num=element_each_json['PARTITION_NUM'], offset=element_each_json["OFFSET"], addts=element_each_json["ADDTS"], addwho=element_each_json['ADDWHO'], editts=element_each_json['EDITTS'], editwho=element_each_json['EDITWHO'], dbid=element_each_json['DBID']).set(0)
                    else:
                        db_jobs_gauge_kafka_offset_wmx_g.labels(server_job=socket.gethostname(), topic=element_each_json['TOPIC'], partition_num=element_each_json['PARTITION_NUM'], offset=element_each_json["OFFSET"], addts=element_each_json["ADDTS"], addwho=element_each_json['ADDWHO'], editts=element_each_json['EDITTS'], editwho=element_each_json['EDITWHO'], dbid=element_each_json['DBID']).set(1)
         
            ''' Not updated'''
            if not is_updated_editts_offset:
                ''' red'''
                logging.info(f"Time Difference with warning from the process - {time_difference_to_hours}")
                all_envs_status_gauge_g.labels(server_job=socket.gethostname(), type='data_pipeline').set(2)
                ''' update gloabl variable for alert email'''
                saved_status_dict.update({'es_pipeline' : 'Red'})
                ''' expose failure node with a reason'''
                saved_failure_db_kafka_dict.update({element_each_json.get('DBID', "db_jobs_{}".format("WMx")) + "_{}".format("KAFKA_OFFSET") : "WMX db -> The Kafka offsets' PARTITION_NUM [{}] not being updated correctly in the last 5 minutes. [{} hours]".format(",".join(not_updated_offset_list), time_difference_to_hours)})
                WMx_threads_db_Kafka_offset_active = False
                
            else:
                ''' all status are active for Data Pipelines and Kafka_Offset'''
                if all([WMx_threads_db_active, OMx_threads_db_active, WMx_threads_db_Kafka_offset_active]):
                    all_envs_status_gauge_g.labels(server_job=socket.gethostname(), type='data_pipeline').set(1)

        
        except Exception as e:
            logging.error(e)
            pass
        
        finally:
            # time.sleep(interval)
            ''' update after five minutes'''
            time.sleep(interval)


''' global func to call for validating'''
def get_time_difference(audit_process_name_time):
        ''' get time difference'''
        # lock.acquire()
        now_time = datetime.datetime.now()
        
        print(f"audit_process_name_time - {audit_process_name_time}, : {type(audit_process_name_time)}, now_time - {now_time} : {type(now_time)}")
        """
        date_diff = now_time-audit_process_name_time
        print(f"Time Difference - {date_diff}")
        time_hours = date_diff.seconds / 3600
        """
        current_time = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        print(f"current_time : {current_time}")
        dt_a = datetime.datetime.strptime(str(current_time), '%Y-%m-%d %H:%M:%S')
        dt_b = audit_process_name_time
        time_hours = float((dt_a-dt_b).total_seconds() / 3600)
        print(f"Time Difference to hours - {time_hours}")
        
        if now_time < audit_process_name_time:
            logging.info(f"now_time < audit_process_name_time - {round(-time_hours, 2)}")
            if time_hours == 0:
                return 0
            return round(-time_hours, 2)
        else:
            logging.info(f"now_time > audit_process_name_time - {round(time_hours, 2)}")
            return round(time_hours, 2)


def db_jobs_work(interval, database_object, sql, db_http_host, db_url, db_info, multipe_db):
# def db_jobs_work(interval, db_http_host):
    ''' We can see the metrics with processname and addts fieds if they are working to process normaly'''
    ''' This thread will run if db_run as argument is true and db is online using DB interface RestAPI'''
    
    def Initialize_active_multiple_db_clear(multipe_db):
        ''' we have to handle the same failure dict if we connect to multiple db'''
        if multipe_db:
            # if WMx_threads_db_active and OMx_threads_db_active and WMx_threads_db_Kafka_offset_active:
            if WMx_threads_db_active and OMx_threads_db_active:
                saved_failure_db_dict.clear()
                saved_status_dict.clear()
        else:
            saved_failure_db_dict.clear()
            saved_status_dict.clear()

    def Initialize_db_status_red(db_info):
        global WMx_threads_db_active, OMx_threads_db_active
        if db_info == "WMx":
            WMx_threads_db_active = False
        elif db_info == "OMx":
            OMx_threads_db_active = False

  
    ''' db main process with sleep five mintues'''
    global saved_status_dict, saved_failure_db_dict, WMx_threads_db_active, OMx_threads_db_active, WMx_threads_db_Kafka_offset_active
    global db_transactin_time_WMx, db_transactin_time_OMx
    global global_env_name
    time_difference_to_hours = 0.0

    while True:
        try:
            # - main sql
            '''
             [
                {'a': 'v', 'b': 'b1}
            ]
            '''

            # lock.acquire()

            StartTime = datetime.datetime.now()
            db_transactin_time_WMx, db_transactin_time_OMx = 0.0, 0.0

            ''' clear saved_failure_db_dict '''
            Initialize_active_multiple_db_clear(multipe_db)

            if db_http_host:
                '''  retrieve records from DB interface REST API URL using requests library'''
                logging.info("# HTTP Interface")

                ''' call to DB interface RestAPI'''
                request_body = {
                        "db_url" : db_url,
                        "sql" : sql
                }

                logging.info("db_http_host : {}, db_info : {}, db_url : {}, sql : {}".format(db_http_host, db_info, db_url, sql))
                http_urls = "http://{}/db/get_db_query".format(db_http_host)
                resp = requests.post(url=http_urls, json=request_body, timeout=600)

                if not (resp.status_code == 200):
                    ''' clear table for db records if host not reachable'''
                    
                    if db_info == "WMx":
                        db_jobs_gauge_wmx_g._metrics.clear()
                        WMx_threads_db_active = False
                    elif db_info == "OMx":
                        db_jobs_gauge_omx_g._metrics.clear()
                        OMx_threads_db_active = False

                    ''' DB error '''
                    logging.info(f"response : {resp.json()['message']}")
                    
                    ''' expose failure node with a reason'''
                    saved_failure_db_dict.update({'db-jobs-{}_{}'.format(db_info,db_info) : "{} db -> ".format(db_info) + resp.json()['message']})
                    all_envs_status_gauge_g.labels(server_job=socket.gethostname(), type='data_pipeline').set(2)
                    saved_status_dict.update({'es_pipeline' : 'Red'})

                    logging.info(f"saved_failure_db_dict in 404 response - {saved_failure_db_dict}, saved_status_dict - {saved_status_dict}")
                    logging.info(f"updated..")
                    # return None
                    continue
                
                logging.info(f"db/process_table - {resp}")
                ''' db job performance through db interface restapi'''
                # db_jobs_performance_gauge_g.labels(server_job=socket.gethostname()).set(int(resp.json["running_time"]))
                result_json_value = resp.json()["results"]

                if db_info == "WMx":
                    db_transactin_time_WMx = resp.json()["running_time"]
                elif db_info == "OMx":
                    db_transactin_time_OMx = resp.json()["running_time"]
         
            else:
                ''' This logic perform to connect to DB directly and retrieve records from processd table '''
                logging.info("# DB Interface Directly")
                result_json_value = database_object.excute_oracle_query(sql)

            ''' DB processing time '''
            EndTime = datetime.datetime.now()

            # logging.info(f"saved_failure_db_dict in 200 response - {saved_failure_db_dict}, saved_status_dict - {saved_status_dict}")
            logging.info(f"WMx_threads_db_active - {WMx_threads_db_active}, OMx_threads_db_active - {OMx_threads_db_active}")

            Delay_Time_WMx, Delay_Time_OMx = 0.0, 0.0
            if db_info == "WMx":
                Delay_Time_WMx = str((EndTime - StartTime).seconds) + '.' + str((EndTime - StartTime).microseconds).zfill(6)[:2]
                logging.info("# [{}] HTTP Rest DB Query Running Time - {}".format(db_info, str(Delay_Time_WMx)))
            elif db_info == "OMx":
                Delay_Time_OMx = str((EndTime - StartTime).seconds) + '.' + str((EndTime - StartTime).microseconds).zfill(6)[:2]
                logging.info("# [{}] HTTP Rest DB Query Running Time - {}".format(db_info, str(Delay_Time_OMx)))

            ''' clear table for db records if host not reachable'''
            # db_jobs_gauge_g._metrics.clear()
            if db_info == "WMx":
                db_jobs_gauge_wmx_g._metrics.clear()
            elif db_info == "OMx":
                db_jobs_gauge_omx_g._metrics.clear()

            ''' calculate delay time for DB'''
            ''' if db_http_post set db_transactin_time from HTTP interface API otherwise set Delay time'''
            # db_transactin_perfomrance = db_transactin_time if db_http_host else Delay_Time
            if db_info == "WMx":
                db_jobs_performance_WMx_gauge_g.labels(server_job=socket.gethostname()).set(float(db_transactin_time_WMx))
                # db_jobs_wmx_sql_data_pipeline_gauge_g.labels(server_job=socket.gethostname()).set(float(db_transactin_time_WMx))
            elif db_info == "OMx":
                db_jobs_performance_OMx_gauge_g.labels(server_job=socket.gethostname()).set(float(db_transactin_time_OMx))
                # db_jobs_omx_sql_data_pipeline_gauge_g.labels(server_job=socket.gethostname()).set(float(db_transactin_time_WMx))

            
            ''' response same format with list included dicts'''   
            logging.info(f"db-job: result_json_value : {result_json_value}")
            # db_jobs_gauge_g._metrics.clear()
            ''' check if process exists in table "es_pipeline_processed" '''
            is_exist_process = False
            
            if result_json_value:
                for each_row, element_each_json in enumerate(result_json_value):
                    
                    ''' updat metrics'''
                    if db_info == "WMx":
                        db_jobs_gauge_wmx_g.labels(server_job=socket.gethostname(), processname=element_each_json['PROCESSNAME'], status=element_each_json['STATUS'], cnt=element_each_json["COUNT(*)"], addts=element_each_json["ADDTS"], dbid=element_each_json['DBID'], db_info="{}{}".format(str(global_env_name).lower(), db_info)).set(1)
                    elif db_info == "OMx":
                        db_jobs_gauge_omx_g.labels(server_job=socket.gethostname(), processname=element_each_json['PROCESSNAME'], status=element_each_json['STATUS'], cnt=element_each_json["COUNT(*)"], addts=element_each_json["ADDTS"], dbid=element_each_json['DBID'], db_info="{}{}".format(str(global_env_name).lower(), db_info)).set(1)

                    if 'PROCESSNAME' in element_each_json:
                        is_exist_process = True
                        ''' all envs update for current data pipeline active --> process in db_jobs_work function'''
                        
                        # if 'ES_PIPELINE_UPLOAD_TEST' in element_each_json.get('PROCESSNAME','') and element_each_json.get('STATUS','') in ['C', 'E']:
                        ''' top record for validating if data pipeline is being processed within 30 minutes'''
                        if each_row == 0:

                            ''' --------------'''
                            ''' update process name with time difference'''
                            # Calculate the time gap
                            audit_process_name_time = datetime.datetime.strptime(element_each_json.get("ADDTS",""), "%Y-%m-%d %H:%M:%S")
                            # audit_process_name_time = datetime.datetime.strptime("2024-09-27 10:35:00", "%Y-%m-%d %H:%M:%S")
                            time_difference_to_hours = get_time_difference(audit_process_name_time)
                            ''' --------------'''

                            ''' Check DATA PIPELINE PROCESS If the processing time is greator than 30 minutes, we believe there may be a problem with the process.'''
                            ''' 1.0 : 1 hour'''
                            if time_difference_to_hours > DATA_PIPELINE_THRESHOLD:
                                ''' red'''
                                logging.info(f"Time Difference with warning from the process - {time_difference_to_hours}")
                                all_envs_status_gauge_g.labels(server_job=socket.gethostname(), type='data_pipeline').set(2)
                                ''' update gloabl variable for alert email'''
                                saved_status_dict.update({'es_pipeline' : 'Red'})
                                ''' expose failure node with a reason'''
                                # saved_failure_db_dict.update({element_each_json.get('DBID', 'db_jobs') : "{} process has not saved test records within the last 30 minutes.".format(element_each_json.get('PROCESSNAME',''))})
                                saved_failure_db_dict.update({element_each_json.get('DBID', "db_jobs_{}".format(db_info)) + "_{}".format(db_info) : "{} db -> Data has not been processed in the last 30 minutes. [{} hours]".format(db_info, time_difference_to_hours)})

                                """
                                if db_info == "WMx":
                                    WMx_threads_db_active = False
                                elif db_info == "OMx":
                                    OMx_threads_db_active = False
                                """
                                ''' Disable to WMx_threads_db_active or OMx_threads_db_active for multiple threads when connecting to DB'''
                                Initialize_db_status_red(db_info)
                            else:
                                ''' we have to check this metric due to connection of two db via multiple threads'''
                                ''' update '''
                                # if 'db-jobs-{}_{}'.format(db_info,db_info) in saved_failure_db_dict.keys():
                                #     del saved_failure_db_dict['db-jobs-{}_{}'.format(db_info,db_info)]

                                if db_info == "WMx":
                                    WMx_threads_db_active = True
                                elif db_info == "OMx":
                                    OMx_threads_db_active = True

                                ''' clear'''
                                Initialize_active_multiple_db_clear(multipe_db)

                                # if all([WMx_threads_db_active, OMx_threads_db_active, WMx_threads_db_Kafka_offset_active]):
                                if len(saved_failure_db_dict) < 1:
                                    all_envs_status_gauge_g.labels(server_job=socket.gethostname(), type='data_pipeline').set(1)

                        ''' else '''
                        ''' update metrics for the number of process on Grafana tool'''
                   
                                
            ''' if DATA PIPELINE process doesn't exist in es_pipeline_processed table'''
            if not is_exist_process:
                ''' red'''
                logging.info(f"No 'Data Pipeline' Process records")
                all_envs_status_gauge_g.labels(server_job=socket.gethostname(), type='data_pipeline').set(2)
                ''' expose failure node with a reason'''
                # es_service_jobs_failure_gauge_g.labels(server_job=socket.gethostname(), reason="No 'ES_PIPELINE_UPLOAD_TEST' Process").set(0)
                # saved_failure_db_dict.update({'db-jobs' : "No 'ES_PIPELINE_UPLOAD_TEST' Process"})
                saved_failure_db_dict.update({'db-jobs-{}_{}'.format(db_info,db_info) : "{} db -> No 'Data Pipeline' Process records".format(db_info)})
                saved_status_dict.update({'es_pipeline' : 'Red'})

                """
                if db_info == "WMx":
                    WMx_threads_db_active = False
                elif db_info == "OMx":
                    OMx_threads_db_active = False
                """
                ''' Disable to WMx_threads_db_active or OMx_threads_db_active for multiple threads when connecting to DB'''
                Initialize_db_status_red(db_info)

                ''' print'''
                logging.info(f"not is_exist_process - {saved_failure_db_dict}, saved_status_dict - {saved_status_dict}")

            logging.info("\n\n")
             # lock.release()
            
        except Exception as e:
            logging.error(e)
            # saved_failure_db_dict.update({"http-db-interface_jobs-{}".format(db_info) : "{} [{} DB]-> {}".format(http_urls, db_info, str(e))})
            # saved_failure_db_dict.update({"http-db-interface_jobs-{}".format(db_info) : "{} DB -> {}".format(db_info, str(e))})
            # all_envs_status_gauge_g.labels(server_job=socket.gethostname(), type='data_pipeline').set(2)
            # saved_status_dict.update({'es_pipeline' : 'Red'})
            ''' Disable to WMx_threads_db_active or OMx_threads_db_active '''
            Initialize_db_status_red(db_info)
            pass
        
        finally:
            # time.sleep(interval)
            ''' update after five minutes'''
            time.sleep(interval)



def db_jobs_backlogs_work(interval, database_object, sql, db_http_host, db_url, db_info):
    ''' Get backlogs for both DB's'''
    global WMx_backlog, OMx_backlog, WMx_backlog_list, recheck_WMx
    
    # Max_History_For_Hour (5 minute * 12)
    WMx_backlog_list = [] 
    recheck_WMx = True

    ''' calculate the lengh of list for the alert can be sent per 1 hour'''
    # Max_History_For_Hour = int(3600/interval)
    Max_History_For_Hour = 12

    # Max_Backlog_CNT = 0
    Max_Backlog_CNT = 10000
    
    while True:
        try:

            StartTime = datetime.datetime.now()
            db_transactin_time_Backlog_WMx, db_transactin_time_Backlog_OMx = 0.0, 0.0

            if db_http_host:
                '''  retrieve records from DB interface REST API URL using requests library'''
                logging.info("# HTTP Interface for db_jobs_backlogs_work")

                ''' call to DB interface RestAPI'''
                request_body = {
                        "db_url" : db_url,
                        "sql" : sql
                }

                logging.info("db_http_host : {}, db_info : {}, db_url : {}, sql : {}".format(db_http_host, db_info, db_url, sql))
                http_urls = "http://{}/db/get_db_query".format(db_http_host)
                resp = requests.post(url=http_urls, json=request_body, timeout=600)

                if not (resp.status_code == 200):
                    ''' clear table for db records if host not reachable'''
                    logging.info(f"db_jobs_backlogs_work in 404 response - {saved_failure_db_dict}, saved_status_dict - {saved_status_dict}")
                    continue
                
                logging.info(f"db/process_table - {resp}")
                ''' db job performance through db interface restapi'''
                # db_jobs_performance_gauge_g.labels(server_job=socket.gethostname()).set(int(resp.json["running_time"]))
                result_json_value = resp.json()["results"]

                if db_info == "WMx":
                    db_transactin_time_Backlog_WMx = resp.json()["running_time"]
                elif db_info == "OMx":
                    db_transactin_time_Backlog_OMx = resp.json()["running_time"]
         
            else:
                ''' This logic perform to connect to DB directly and retrieve records from processd table '''
                logging.info("# DB Interface Directly")
                result_json_value = database_object.excute_oracle_query(sql)

            ''' DB processing time '''
            EndTime = datetime.datetime.now()

            logging.info(f"# db_transactin_time_WMx_backlog : {db_transactin_time_Backlog_WMx}, db_transactin_time_OMx_backlog : {db_transactin_time_Backlog_OMx}")

            Delay_Time_WMx, Delay_Time_OMx = 0.0, 0.0
            if db_info == "WMx":
                Delay_Time_WMx = str((EndTime - StartTime).seconds) + '.' + str((EndTime - StartTime).microseconds).zfill(6)[:2]
                logging.info("# [{}] HTTP db_jobs_backlogs_work DB Query Running Time - {}".format(db_info, str(Delay_Time_WMx)))
            elif db_info == "OMx":
                Delay_Time_OMx = str((EndTime - StartTime).seconds) + '.' + str((EndTime - StartTime).microseconds).zfill(6)[:2]
                logging.info("# [{}] HTTP db_jobs_backlogs_work DB Query Running Time - {}".format(db_info, str(Delay_Time_OMx)))

            ''' response same format with list included dicts'''   
            logging.info(f"db-job: result_json_value : {result_json_value}")

            ''' get db configuration'''
            if not global_mail_configuration:
                get_mail_configuration(db_http_host)
            data = global_mail_configuration

            host_name = socket.gethostname().split(".")[0]
            dev_email_list = data[host_name].get("dev_mail_list", "")
            dev_sms_list = data[host_name].get("dev_sms_list", "")

            if db_info == "WMx":
                WMx_backlog = result_json_value[0].get("TOTAL_UNPROCESSED_RECS")
                db_jobs_backlogs_WMx_gauge_g.labels(server_job=socket.gethostname()).set(float(WMx_backlog))

                WMx_backlog_list.append(WMx_backlog)
                
                ''' check if one of WMx_backlog_list list is bigger than 10000 as Max_Backlog_CNT'''
                is_bigger_than_condition = [k for k in WMx_backlog_list if float(k) > Max_Backlog_CNT]

                ''' send alert for backlog'''
                is_alert_option = data[host_name].get("is_mailing")
                if len(is_bigger_than_condition) > 0 and recheck_WMx and is_alert_option:
                    logging.info(f"db_jobs_backlogs_work alert : {WMx_backlog}, WMx_backlog_list : {WMx_backlog_list}")
                    alert_msg = "Backlog for unprocessed data  in the WMx ES pipeline queue tables: {:,}, db_transactin_time_WMx : {}/sec, db_transactin_time_OMx : {}/sec".format(WMx_backlog, db_transactin_time_WMx, db_transactin_time_OMx)
                    ''' send mail'''
                    send_mail(body=alert_msg, 
                            host= socket.gethostname().split(".")[0], 
                            env=data[host_name].get("env"), 
                            status_dict=saved_status_dict, 
                            to=dev_email_list, cc="", _type='mail')
                    ''' send sms'''
                    # send_mail(body=alert_msg,  host=host_name,  env=data[host_name].get("env"),  status_dict=saved_status_dict,  to=dev_sms_list, cc=None, _type="sms")

                    ''' disbaled this variable for sending every 1 hour'''
                    recheck_WMx = False
                
                ''' alert almost every 1 hour for backlog for unprocessed data '''
                if len(WMx_backlog_list) >= Max_History_For_Hour:
                    recheck_WMx = True
                    WMx_backlog_list.clear()

            elif db_info == "OMx":
                OMx_backlog = result_json_value[0].get("TOTAL_UNPROCESSED_RECS")
                db_jobs_backlogs_OMx_gauge_g.labels(server_job=socket.gethostname()).set(float(OMx_backlog))
       
        except Exception as e:
            logging.error(e)
            pass
        
        finally:
            # time.sleep(interval)
            ''' update after five minutes'''
            time.sleep(interval)



def alert_to_text(data, hostname, sms_list, saved_status_dict, immediately=False):
    ''' Send sms alerts to our team when the usage of CPU/JVM is over 85% for 5 minutes or (ES Service/Data pipeline has at least Yellow)'''
    if saved_thread_alert or saved_critcal_sms_alert or immediately:
        if sms_list:
            ''' check if is_sms is enabled from es_configuration api'''
            if data[hostname].get("is_sms"):
                logging.info("Sending SMS..")
                send_mail(body=", ".join(saved_thread_alert_message), 
                          host=hostname, 
                          env=data[hostname].get("env"), 
                          status_dict=saved_status_dict, 
                          to=sms_list, 
                          cc=None, 
                          _type="sms")
            else:
                logging.info("Sending SMS but no sms_list..")


def inserted_post_log(status, message):
    '''  Insert logs to H2 database through ES Configuration API'''
    logging.info("# HTTP Interface")
    ''' STATUS : ES_RESET_REPLICA, ES_RESTARTED'''

    ''' call to ES Configuration interface RestAPI'''
    """
        curl -X 'POST' \
    'http://localhost:8004/log/create_log' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
    "env": "localhost",
    "host_name": "localhost",
    "status": "ES_RESTARTED",
    "message": "TEST MESSAGE"
    }'
    """
    ''' {"message": "Inserted log successfully."}'''
    request_body = {
                    "env" : global_env_name,
                    "host_name" : socket.gethostname().split(".")[0],
                    "status" : str(status).upper(),
                    "message" : str(message)
    }

    logging.info(f"inserted_post_log - {request_body}")

    http_urls = "http://{}:8004/log/create_log".format(global_es_configuration_host)
    resp = requests.post(url=http_urls, json=request_body, timeout=600)
                
    if not (resp.status_code == 200):
        ''' clear table for db records if host not reachable'''
        ''' API error '''
        logging.info(f"response : {resp.json()['message']}")
                    
    logging.info(f"inserted_post_log - {resp}")
   



gloabl_configuration = {}
def get_global_configuration(es_http_host):
    ''' get global configuration through ES configuration REST API'''

    global gloabl_configuration

    try:
        es_config_host = str(es_http_host).split(":")[0]
        resp = requests.get(url="http://{}:8004/config/get_gloabl_config".format(es_config_host), timeout=5)
                
        if not (resp.status_code == 200):
            ''' save failure node with a reason into saved_failure_dict'''
            logging.error(f"get_global_configuration api do not reachable")
            saved_failure_dict.update({socket.gethostname(): "get_global_configuration api do not reachable"})
                
        # logging.info(f"get_mail_config - {resp}, {json.dumps(resp.json(), indent=2)}")
        logging.info(f"get_global_configuration - {resp}")
        gloabl_configuration = resp.json()
        
    except Exception as e:
        logging.error(e)
        # pass


global_mail_configuration = {}
def get_mail_configuration(db_http_host):
    ''' interface es_config_api http://localhost:8004/config/get_mail_config '''

    global global_mail_configuration, saved_failure_dict
    try:
        # if ':' in str(db_http_host):
        #     es_config_host = str(db_http_host).split(":")[0]
        # else:
        #     es_config_host = str(db_http_host)
        logging.info(f"get_mail_configuration_db_http_host : {db_http_host}")
        es_config_host = os.environ["ES_CONFIGURATION_HOST"]
        logging.info(f"get_mail_configuration_es_config_host : {es_config_host}")
        resp = requests.get(url="http://{}:8004/config/get_mail_config".format(es_config_host), timeout=5)
                
        if not (resp.status_code == 200):
            ''' save failure node with a reason into saved_failure_dict'''
            logging.error(f"es_config_interface api do not reachable")
            saved_failure_dict.update({socket.gethostname(): "es_config_interface_api/get_mail_config do not reachable"})
            return None
                
        # logging.info(f"get_mail_config - {resp}, {json.dumps(resp.json(), indent=2)}")
        # logging.info(f"get_mail_config - {resp}, {resp.json()}")
        global_mail_configuration = resp.json()
        

    except Exception as e:
        logging.error(e)
        pass


def work(es_http_host, db_http_host, port, interval, monitoring_metrics):
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
        logging.info(f"\n\nStandalone Prometheus Exporter Server started..")
        logging.info(f"es_http_host : {es_http_host}")
        logging.info(f"db_http_host : {db_http_host}")

        StartedTime = datetime.datetime.now()
        while True:
            StartTime = datetime.datetime.now()

            ''' get global configuration'''
            get_global_configuration(es_http_host)

            ''' get db configuration'''
            get_mail_configuration(es_http_host)

            ''' Collection metrics from ES/Kafka/Spark/Kibana/Logstash'''
            get_metrics_all_envs(monitoring_metrics)
            
            ''' export application processing time '''
            EndTime = datetime.datetime.now()
            Delay_Time = str((EndTime - StartTime).seconds) + '.' + str((EndTime - StartTime).microseconds).zfill(6)[:2]
            logging.info("# StartedTime Application - {}".format(str(StartedTime)))
            logging.info("# Export Application Running Time - {}\n\n".format(str(Delay_Time)))
            es_service_jobs_performance_gauge_g.labels(server_job=socket.gethostname()).set(float(Delay_Time))
            
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
       

''' Alert'''
ALERT_RESENT_TIME = 1.0
ALERT_DURATION = 0.0
ALERT_RESENT = False
ALERT_STARTED_TIME = "1900-01-01 00:00:00"


def get_alert_resend(updated=True):
    ''' Whenever app does check for the alerts every 10 minutes, sends the first alert, and then resends the alert after 1 hour.'''
    global tracking_failure_dict, ALERT_RESENT, ALERT_DURATION

    get_tracking_alert_time = datetime.datetime.strptime(tracking_failure_dict.get("alert_sent_time"), "%Y-%m-%d %H:%M:%S")
    alert_time_difference = get_time_difference(get_tracking_alert_time)
    
    ''' update current the duration time for the time of alert was sent'''
    ALERT_DURATION = alert_time_difference
    if alert_time_difference >= ALERT_RESENT_TIME:
        ALERT_RESENT = True
        if updated:
            tracking_failure_dict.update({"alert_sent_time" : str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))})
        return True
    else:
        ALERT_RESENT = False
        return False


''' Send text/mail alert depends on es configuration mailing status value'''
def alert_work(db_http_host):
    ''' thread for alert'''
    ''' Whenever app does check for the alerts every 10 minutes, sends the first alert, and then resends the alert after 1 hour. '''
    ''' After retransmitting, the alert will be sent again after 1 hour.'''
    ''' You need to use tracking history to calculate time.'''
    ''' Tracking thread_alert_message '''
    """
        tracking_failure_dict = {
            "alert_sent_time" : "1900-01-01 00:00:00",
            "history_message" : []
        }
    """

    def json_read_config(path):
        ''' read config file with option'''
        with open(path, "r") as read_file:
            data = json.load(read_file)
        return data


    def alert_time_range(alert_exclude_time):
        ''' We don't want to send the alert between these time range'''
        ''' Alert to be sent if True'''
        global global_out_of_alert_time_range, global_TIME_STAMP, global_OUT_OF_ALERT_TIME, ALERT_RESENT
        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M:%S")
        global_TIME_STAMP = current_time
        # start = '00:00:00'
        # end = '00:15:00'

        if not alert_exclude_time:
            global_out_of_alert_time_range = True
            return True

        global_OUT_OF_ALERT_TIME = alert_exclude_time
        start = str(alert_exclude_time).split(",")[0]
        end = str(alert_exclude_time).split(",")[1]
        
        if current_time >= start and current_time <= end:
            logging.info(f"alert_time_range - : 'in', current_time : {current_time}")
            global_out_of_alert_time_range = False
            return False
        else:
            logging.info(f"alert_time_range - : 'out', current_time : {current_time}")
            global_out_of_alert_time_range = True
            return True

    try:
        global saved_failure_dict, tracking_failure_dict, ALERT_STARTED_TIME

        ALERT_STARTED_TIME = datetime.datetime.now()

        while True:
            ''' read config file to enable/disable to send an email'''
            '''
            data = json_read_config("./mail/config.json")
            logging.info(f"config json file : {data}")
            '''

            # logging.info(f"\n\nmail treading working..")

            ''' get db configuration'''
            if not global_mail_configuration:
                get_mail_configuration(db_http_host)
            data = global_mail_configuration

            """
            ''' interface es_config_api http://localhost:8004/config/get_mail_config '''
            es_config_host = str(db_http_host).split(":")[0]
            logging.info(f"es_config_host : {es_config_host}")
            resp = requests.get(url="http://{}:8004/config/get_mail_config".format(es_config_host), timeout=5)
                
            if not (resp.status_code == 200):
                ''' save failure node with a reason into saved_failure_dict'''
                logging.error(f"es_config_interface api do not reachable")
                saved_failure_dict.update({socket.gethostname(): "es_config_interface_api do not reachable"})
                continue
                
            # logging.info(f"get_mail_config - {resp}, {json.dumps(resp.json(), indent=2)}")
            logging.info(f"get_mail_config - {resp}, {resp.json()}")
            data = resp.json()
            """

            get_es_config_interface_api_host_key = socket.gethostname().split(".")[0]

            ''' ------------------------------------------------------'''
            ''' send an email these warning message if the status of env has an yellow or red'''
            # email_list = os.environ["EMAIL_LIST"]
            # email_list = data.get("mail_list")

            # thread_interval = int(data.get("thread_interval"))
            thread_interval = int(data.get(get_es_config_interface_api_host_key).get("thread_interval"))
            logging.info(f"get_mail_config [thread_interval] - {thread_interval}")
            logging.info(f"get_dashbaord_from_shell- {os.environ['GRAFANA_DASHBOARD_URL']}")
            alert_exclude_time = data.get("alert_exclude_time")

            '''
            {
                "dev": {
                    "mail_list": "test",
                    "is_mailing": true
                },
                "localhost": {
                    "mail_list": "test",
                    "is_mailing": true
                }
            }    
            '''
            
            email_list = data[get_es_config_interface_api_host_key].get("mail_list", "")
            cc_list = data[get_es_config_interface_api_host_key].get("cc_list", "") if "cc_list" in data[get_es_config_interface_api_host_key].keys() else ""
            sms_list = data[get_es_config_interface_api_host_key].get("sms_list", "") if "sms_list" in data[get_es_config_interface_api_host_key].keys() else ""

            logging.info(f"mail_list from shell script: {email_list}, cc_list : {cc_list}, sms_list : {sms_list}")
            logging.info(f"is_mailing: {data[get_es_config_interface_api_host_key].get('is_mailing')}, type : {type(data[get_es_config_interface_api_host_key].get('is_mailing'))}")

            logging.info(f"saved_status_dict - {json.dumps(saved_status_dict, indent=2)}")
            logging.info(f"service_status_dict - {json.dumps(service_status_dict, indent=2)}")

            ''' It will send the alert with time range'''
            is_sent_alert = alert_time_range(alert_exclude_time)
            
            ''' Call function to send an email'''
            ''' global mememoy'''
            ''' alert message to mail with interval?'''
            # if saved_thread_alert or saved_thread_green_alert:
            if saved_thread_alert:
                ''' compare the current time with last alert was sent'''
                is_resent_if_alert_need_to = get_alert_resend(True)
                if data[get_es_config_interface_api_host_key].get("is_mailing"):
                    logging.info("Sending email..")
                    
                    ''' It will send the alert with time range'''
                    if is_sent_alert and is_resent_if_alert_need_to:
                        message = "<BR/>".join(saved_thread_alert_message)
                        send_mail(body=message, host=get_es_config_interface_api_host_key, env=data[get_es_config_interface_api_host_key].get("env"), status_dict=saved_status_dict, to=email_list, cc=cc_list, _type='mail')
                    
                ''' ----------------------'''
                ''' sms alert'''
                ''' Send sms alerts to our team when the usage of CPU/JVM is over 85% for 5 minutes or (ES Service/Data pipeline has at least Yellow)'''
                ''' It will send the alert with time range'''
                if data[get_es_config_interface_api_host_key].get("is_sms"):
                    if is_sent_alert and is_resent_if_alert_need_to:
                        alert_to_text(data, get_es_config_interface_api_host_key, sms_list, saved_status_dict)
                ''' ----------------------'''
            
            """ Grafana-Loki Log """
            if saved_thread_alert:
                ''' out of 00:00 time range for some issue from the db and sent alert again after 1 hour'''
                ''' it will be sent alert log regardless of alert option'''
                if is_sent_alert and is_resent_if_alert_need_to:
                    message = ", ".join(saved_thread_alert_message)
                    message_status = "Server Active : {}, ES Data Pipline : {}".format(saved_status_dict.get("server_active","Green"), saved_status_dict.get("es_pipeline","Green"))
                    logger.error("Prometheus-Monitoring-Service - {}".format(message),
                                    extra={"tags": {"service": "prometheus-monitoring-service", "message" : "[{}] Services, Alert : {}, Issues : {}".format(
                                        global_env_name,
                                        saved_thread_alert,
                                        message_status
                                        ),
                                        "env" : "{}".format(global_env_name), 
                                        }},
                    )

            logging.info(f"saved_thread_alert - {saved_thread_alert}")
            # logging.info(f"saved_thread_alert_message - {saved_thread_alert_message}")

            ''' every one day to send an alert email'''
            # time.sleep(60*60*24)
            
            ''' every one hour to send an alert email'''
            if is_dev_mode:
                time.sleep(60)
            else:
                time.sleep(60*thread_interval)

    except (KeyboardInterrupt, SystemExit):
        logging.info("#Interrupted..")
    except Exception as e:
        logging.info(e)
        pass



''' dev mode for alerting'''
#----------------------------
# is_dev_mode = True
is_dev_mode = False
#----------------------------

# Function that send email.
def send_mail(body, host, env, status_dict, to, cc, _type):
    '''' Params for mailling'''

    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    def cleanText(readData):
        text = re.sub('[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\[\]\(\)\<\>`\'…》]', '', readData)
        return text
    
    def mail_attached(grafana_dashboard_url, smtp_host, smtp_port, host, message, to, cc, _type):
        ''' using mailx'''
        # body = body.encode('utf-8')
        # body = "Monitoring [ES Team Dashboard on export application]'\n\t' \
        #         - Grafana 'ES team Dashboard' URL : {}'\n\t' \
        #         - Enviroment: {}, Prometheus Export Application Runnig Host : {}, Export Application URL : http://{}:9115'\n\t' \
        #         - Server Status: {}, ES_PIPELINE Status : {}'\n\t' \
        #         - Alert Message : {} \
        #         ".format(grafana_dashboard_url, env, host, host, status_dict.get("server_active","Green"), status_dict.get("es_pipeline","Green"), body)

        user_list = to.split(",")
        print(f"user_list : {user_list}")
        
        '''
        for user in email_user_list:
            print(user)
            if cc:
                cmd=f"echo {body} | mailx -s 'Prometheus Monitoring Alert' " + f"-c {cc} " + to
            else:
                cmd=f"echo {body} | mailx -s 'Prometheus Monitoring Alert' " + to
            result = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
            output, errors = result.communicate()
            if output:
                print(f"Send mail to user : {user}, output : {output}")
            if errors:
                print(errors)
        '''
        # if cc:
        #     cmd=f"echo {body} | mailx -s '[{env}] Prometheus Monitoring Alert' " + f"-c {cc} " + to
        # else:
        #     cmd=f"echo {body} | mailx -s '[{env}] Prometheus Monitoring Alert' " + to
        # result = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        # output, errors = result.communicate()
        # if output:
        #     print(f"Send mail to user : {to}, output : {output}")
        # if errors:
        #     print(errors)
        
        """
        # cmd=f"echo {body} | mailx -s 'Prometheus Monitoring Alert' " + "-c a@test.mail " + to
        cmd=f"echo {body} | mailx -s 'Prometheus Monitoring Alert [{env}]' " + to
        result = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        output, errors = result.communicate()
        if output:
            print(f"Send mail output : {output}")
        if errors:
            print(errors)
        """

        ''' using smtp'''
        me = os.environ["MAIL_SENDER"]
        you = user_list

        msg = MIMEMultipart('alternative')
        msg['Subject'] = '[{}] Prometheus Monitoring Alert'.format(env)
        msg['From'] = me
        msg['To'] = ','.join(you)
        msg['Cc'] = cc
 
        """
        service_status_dict - {
            "es": "Green",
            "spark": "Green",
            "spark_custom_apps": 1,
            "spark_custom_apps_list": "StreamProcessEXP",
            "es_nodes": 4,
            "kafka": "Green",
            "kafka_nodes": 3,
            "kafka_connect": "Green",
            "kafka_connect_nodes": 3,
            "zookeeper": "Green",
            "zookeeper_nodes": 2,
            "kibana": "Green",
            "logstash": "Green"
        }
        """
        
        alert_date = datetime.datetime.now()

        if _type == "mail":
            body = """
                - Alert Date : %s <BR/> \
                - Grafana Dashboard URL : <a href="%s">%s</a> <BR/> \
                - Monitoring Configuration API : <a href="%s">%s</a>  <BR/> \
                - Enviroment: <b>%s</b>, Prometheus Export Application Runnig Host : %s, Export Application URL : <a href="http://%s:9115">http://%s:9115</a> <BR/> \
                - Service Status: <b>%s</b>, ES_PIPELINE Status : <b>%s</b> <BR/> \
                - Service Health:  <BR/> \
                    Elasticsearch Health : <b>%s</b>, Elasticsearch Nodes : <b>%s</b> <BR/>\
                    Spark Health : <b>%s</b>, Spark Custom Apps : <b>%s</b> <BR/>\
                    - Active Spark Custom Apps : <b>%s</b> <BR/>\
                    Kafka Health : <b>%s</b>, Kafka Nodes : <b>%s</b> <BR/>\
                    Kafka_connect Health : <b>%s</b>, Kafka_connect_primary_node Health : <b>%s</b>, Kafka Connect Nodes : <b>%s</b> <BR/>\
                    Zookeeper Health : <b>%s</b>, Zookeeper Nodes : <b>%s</b> <BR/>\
                    Kibana Health : <b>%s</b> <BR/>\
                    Logstash Health : <b>%s</b> <BR/>\
                - <b>Alert Message : </b><BR/>%s \
                """ % (alert_date, grafana_dashboard_url, grafana_dashboard_url, 
                       os.environ["ES_CONFIGURATION_URL"],os.environ["ES_CONFIGURATION_URL"],
                       env, host, host, host, status_dict.get("server_active","Green"), status_dict.get("es_pipeline","Green"),
                       service_status_dict.get("es",""), service_status_dict.get("es_nodes",""),
                       service_status_dict.get("spark",""), service_status_dict.get("spark_custom_apps",""),
                       str(service_status_dict.get("spark_custom_apps_list","")).replace(" ", ""),
                       service_status_dict.get("kafka",""), service_status_dict.get("kafka_nodes",""),
                       service_status_dict.get("kafka_connect",""), service_status_dict.get("kafka_connect_primary_node",""), service_status_dict.get("kafka_connect_nodes",""),
                       service_status_dict.get("zookeeper",""), service_status_dict.get("zookeeper_nodes",""),
                       service_status_dict.get("kibana",""),
                       service_status_dict.get("logstash",""),
                       message)
        
        elif _type == "sms":
            body = """- Enviroment: %s, Prometheus Export Application Runnig Host : %s - Service Status: <b>%s</b>, ES_PIPELINE Status : <b>%s</b> - <b>Alert Message : </b>%s
                """ % (env, host, status_dict.get("server_active","Green"), status_dict.get("es_pipeline","Green"), message)


        html = """
            <h4>Monitoring [ES Team Dashboard on export application]</h4>
            <HTML><head>
            <body>
            %s
            </body></HTML>
            """ % (body)

        part2 = MIMEText(html, 'html')
        msg.attach(part2)

        # print msg
        s = smtplib.SMTP(smtp_host, smtp_port)

        if not you:
            you = []

        if not cc:
            cc = []
        else:
            cc = [cc]
        
        recipients_list = you + cc
        s.sendmail(me, recipients_list, msg.as_string())
        s.quit()

    try:
        ''' send mail through mailx based on python environment'''
        grafana_dashboard_url = os.environ["GRAFANA_DASHBOARD_URL"]
        smtp_host = os.environ["SMTP_HOST"]
        smtp_port = os.environ["SMTP_PORT"]
        
        ''' remove special characters'''
        '''
        body = body.replace('(', "'('").replace(')', "')'")
        body = body.replace('\n\t', " ").replace('(', "").replace(')', "").replace('\n', " ")
        body = re.sub(r"[^\uAC00-\uD7A30-9a-zA-Z\s]", " ", body)
        body = cleanText(body)
        '''

        ''' remove b first character'''
        logging.info(f"send_mail -> Mail Alert message : {body}, type(body) : {type(body)}")
    
        ''' sending emiall/sms'''
        mail_attached(grafana_dashboard_url, smtp_host, smtp_port, host, body, to, cc, _type)
        
    except Exception as e:
        logging.error(e)
        pass




if __name__ == '__main__':
    '''
    ./standalone-export-run.sh -> ./standalone-es-service-export.sh status/stop/start
    # first node of --kafka_url argument is a master node to get the number of jobs using http://localhost:8080/json
    # -- direct access to db
    python ./standalone-es-service-export.py --interface db --url jdbc:oracle:thin:id/passwd@address:port/test_db --db_run false --kafka_url localhost:9092,localhost:9092,localhost:9092 --kafka_connect_url localhost:8083,localhost:8083,localhost:8083 --zookeeper_url  localhost:2181,localhost:2181,localhost:2181 --es_url localhost:9200,localhost:9201,localhost:9201,localhost:9200 --kibana_url localhost:5601 --sql "SELECT processname from test"
    # -- collect records through DB interface Restapi
    python ./standalone-es-service-export.py --interface http --db_http_host localhost:8002 --url jdbc:oracle:thin:id/passwd@address:port/test_db --db_run false --kafka_url localhost:9092,localhost:9092,localhost:9092 --kafka_connect_url localhost:8083,localhost:8083,localhost:8083 --zookeeper_url  localhost:2181,localhost:2181,localhost:2181 --es_url localhost:9200,localhost:9201,localhost:9201,localhost:9200 --kibana_url localhost:5601 --sql "SELECT processname from test"
    '''
    parser = argparse.ArgumentParser(description="Script that might allow us to use it as an application of custom prometheus exporter")
    parser.add_argument('--env_name', dest='env_name', default="env_name", help='env_name')
    parser.add_argument('--kafka_url', dest='kafka_url', default="localhost:29092,localhost:39092,localhost:49092", help='Kafka hosts')
    parser.add_argument('--kafka_connect_url', dest='kafka_connect_url', default="localhost:8083,localhost:8084,localhost:8085", help='Kafka connect hosts')
    parser.add_argument('--zookeeper_url', dest='zookeeper_url', default="localhost:22181,localhost:21811,localhost:21812", help='zookeeper hosts')
    parser.add_argument('--es_url', dest='es_url', default="localhost:9200,localhost:9501,localhost:9503", help='es hosts')
    parser.add_argument('--kibana_url', dest='kibana_url', default="localhost:5601,localhost:15601", help='kibana hosts')
    parser.add_argument('--redis_url', dest='redis_url', default="", help='redis hosts')
    parser.add_argument('--configuration_job_url', dest='configuration_job_url', default="", help='configuration_job hosts')
    parser.add_argument('--es_configuration_api_url', dest='es_configuration_api_url', default="", help='es_configuration_api_url hosts')
    parser.add_argument('--log_db_url', dest='log_db_url', default="", help='log_db_url')
    parser.add_argument('--alert_monitoring_url', dest='alert_monitoring_url', default="", help='alert_monitoring_ui_url')
    # ''' loki url : http://localhost:3100'''
    # parser.add_argument('--loki_url', dest='loki_url', default="", help='loki_url') 
    # ''' loki REST API url : http://localhost:8010'''
    # parser.add_argument('--loki_api_url', dest='loki_api_url', default="", help='loki_url')
    # parser.add_argument('--loki_custom_promtail_agent_url', dest='loki_custom_promtail_agent_url', default="", help='loki_custom_promtail_agent_url')
    parser.add_argument('--log_aggregation_agent_url', dest='log_aggregation_agent_url', default="", help='log_aggregation_agent_url')
    ''' ----------------------------------------------------------------------------------------------------------------'''
    ''' set DB or http interface api'''
    parser.add_argument('--interface', dest='interface', default="db", help='db or http')
    ''' set DB connection dircectly'''
    parser.add_argument('--url', dest='url', default="postgresql://postgres:1234@localhost:5432/postgres", help='db url')
    parser.add_argument('--db_run', dest="db_run", default="False", help='If true, executable will run after compilation.')
    parser.add_argument('--omx_db_con', dest="omx_db_con", default="True", help='If true, it will connect to db.')
    parser.add_argument('--sql', dest='sql', default="select * from test", help='sql')
    parser.add_argument('--sql_backlog', dest='sql_backlog', default="select * from test", help='sql_backlog')
    parser.add_argument('--backlog', dest="backlog", default="False", help='If true, it will get backlog from DB\'s.')
    # parser.add_argument('--kafka_sql', dest='kafka_sql', default="select * from test", help='kafka_sql')
    ''' request DB interface restpi insteady of connecting db dircectly'''
    parser.add_argument('--db_http_host', dest='db_http_host', default="http://localhost:8002", help='db restapi url')
    ''' ----------------------------------------------------------------------------------------------------------------'''
    parser.add_argument('--port', dest='port', default=9115, help='Expose Port')
    parser.add_argument('--interval', dest='interval', default=30, help='Interval')
    args = parser.parse_args()

    ''' 
    The reason why I created this dashboard was because on security patching day, 
    we had to check the status of ES cluster/kafka/spark job and kibana/logstash manually every time Even if it is automated with Jenkins script.
    
    The service monitoring export we want does not exist in the built-in export application that is already provided. 
    To reduce this struggle, I developed it using the prometheus library to check the status at once on the dashboard.

    Prometheus provides client libraries based on Python, Go, Ruby and others that we can use to generate metrics with the necessary labels.
    When Prometheus scrapes your instance's HTTP endpoint, the client library sends the current state of all tracked metrics to the server. 
    The prometheus_client package supports exposing metrics from software written in Python, so that they can be scraped by a Prometheus service. 
    '''

    global global_env_name, global_es_configuration_host

    if args.env_name:
        env_name = args.env_name

    global_env_name = str(env_name).upper()

    if args.kafka_url:
        kafka_url = args.kafka_url

    if args.kafka_connect_url:
        kafka_connect_url = args.kafka_connect_url

    if args.zookeeper_url:
        zookeeper_url = args.zookeeper_url

    if args.es_url:
        es_url = args.es_url

    if args.kibana_url:
        kibana_url = args.kibana_url

    redis_url, configuration_job_url, es_configuration_api_url, log_db_url, alert_monitoring_url, loki_url, loki_api_url, loki_custom_promtail_agent_url, log_aggregation_agent_url = None, None, None, None, None, None, None, None, None

    ''' Redis port checking'''
    if args.redis_url:
        redis_url = args.redis_url

    ''' es-configuration json file write job checking'''
    if args.configuration_job_url:
        configuration_job_url = args.configuration_job_url

    ''' es-configuration API Service checking'''
    if args.es_configuration_api_url:
        es_configuration_api_url = args.es_configuration_api_url

    ''' log_db_url checking'''
    if args.log_db_url:
        log_db_url = args.log_db_url

    ''' alert_monitoring_url '''
    if args.alert_monitoring_url:
        alert_monitoring_url = args.alert_monitoring_url

    # ''' loki_url for text logs from the agent '''
    # if args.loki_url:
    #     loki_url = args.loki_url

    # ''' loki_api_url as interface api for text logs from the agent '''
    # if args.loki_api_url:
    #     loki_api_url = args.loki_api_url

    # ''' loki_agent for text logs '''
    # if args.loki_custom_promtail_agent_url:
    #     loki_custom_promtail_agent_url = args.loki_custom_promtail_agent_url

    if args.log_aggregation_agent_url:
        log_aggregation_agent_url = args.log_aggregation_agent_url

    ''' ----------------------------------------------------------------------------------------------------------------'''
    ''' set DB or http interface api'''
    if args.interface:
        interface = args.interface

    ''' set DB connection dircectly'''
    if args.url:
        db_url = args.url
    
    if args.db_run:
        db_run = args.db_run

    if args.omx_db_con:
        omx_db_con = args.omx_db_con

    if args.sql:
        sql = args.sql

    if args.sql_backlog:
        sql_backlog = args.sql_backlog

    if args.backlog:
        backlog = args.backlog
        
    # if args.kafka_sql:
    #     kafka_sql = args.kafka_sql

    ''' request DB interface restpi insteady of connecting db dircectly'''
    if args.db_http_host:
        db_http_host = args.db_http_host
    ''' ----------------------------------------------------------------------------------------------------------------'''

    ''' point out to same host'''
    # es_http_host = db_http_host
    es_http_host = os.environ["ES_CONFIGURATION_HOST"]

    ''' update host for ES Configuration API'''
    # global_es_configuration_host = str(es_http_host).split(":")[0]
    global_es_configuration_host = str(es_http_host)

    if args.interval:
        interval = args.interval

    if args.port:
        port = args.port


    monitoring_metrics = {
        "kafka_url" : kafka_url,
        "kafka_connect_url" : kafka_connect_url,
        "zookeeper_url" : zookeeper_url,
        "es_url" : es_url,
        "kibana_url" : kibana_url
    }

    ''' Redis port checking'''
    if redis_url:
        monitoring_metrics.update({"redis_url" : redis_url})

    ''' es-configuration json file write job checking'''
    if configuration_job_url:
        monitoring_metrics.update({"configuration_job_url" : configuration_job_url})

    ''' es-configuration API Service checking'''
    if es_configuration_api_url:
        monitoring_metrics.update({"es_configuration_api_url" : es_configuration_api_url})

    ''' log_db_url checking'''
    if log_db_url:
        monitoring_metrics.update({"log_db_url" : log_db_url})

    ''' alert_monitoring_url checking'''
    if alert_monitoring_url:
        monitoring_metrics.update({"alert_monitoring_url" : alert_monitoring_url})

    ''' loki_url checking '''
    if loki_url:
        monitoring_metrics.update({"loki_url" : loki_url})

    ''' loki_api_url checking '''
    if loki_api_url:
        monitoring_metrics.update({"loki_api_url" : loki_api_url})

    ''' loki_custom_promtail_agent_url checking '''
    # if loki_custom_promtail_agent_url:
    #     monitoring_metrics.update({"loki_custom_promtail_agent_url" : loki_custom_promtail_agent_url})

    ''' log_aggregation_agent_url checking '''
    if log_aggregation_agent_url:
        monitoring_metrics.update({"log_aggregation_agent_url" : log_aggregation_agent_url})
        
    logging.info(json.dumps(monitoring_metrics, indent=2))
    logging.info(interval)

    db_run = True if str(db_run).upper() == "TRUE" else False
    multiple_db = True if str(omx_db_con).upper() == "TRUE" else False
    backlog = True if str(backlog).upper() == "TRUE" else False
    print(interface, db_run, multiple_db, type(db_run), sql, backlog)

    if interface == 'db' and db_run:
        database_object_WMx = oracle_database(db_url)
        # database_object_WMx = oracle_database(str(db_url).split(",")[0])
        # database_object_OMx = oracle_database(str(db_url).split(",")[1])
    else:
        database_object = None
        # database_object_WMx = None
        # database_object_OMx = None
    
    # work(int(port), int(interval), monitoring_metrics)

    ''' log test'''
    # inserted_post_log(status='PROMETHEUS EXPORT APP RESTARTED', message='APP TEST')
    
    try:
        T = []
        '''
        th1 = Thread(target=test)
        th1.daemon = True
        th1.start()
        T.append(th1)
        '''
        
        ''' es/kafka/kibana/logstash prcess check thread'''
        for host in ['localhost']:
            ''' main process to collect metrics'''
            main_th = Thread(target=work, args=(es_http_host, db_http_host, int(port), int(interval), monitoring_metrics))
            main_th.daemon = True
            main_th.start()
            T.append(main_th)

            ''' alert through mailx'''
            mail_th = Thread(target=alert_work, args=(db_http_host,))
            mail_th.daemon = True
            mail_th.start()
            T.append(mail_th)

        
        ''' Set DB connection to validate the status of data pipelines after restart kafka cluster when security patching '''
        ''' We can see the metrics with processname and addts fieds if they are working to process normaly'''
        ''' we create a single test record every five minutes and we upload that test record into a elastic search '''
        ''' and we do that just for auditing purposes to check the overall health of the data pipeline to ensure we're continually processing data '''
        ''' This thread will run every five minutes if db_run as argument is true and db is online'''
        # --
       
        if interface == 'db':
            ''' access to db directly to collect records to check the overall health of the data pipleline'''
            if db_run and database_object.get_db_connection():
            # if db_run and database_object_WMx.get_db_connection() and database_object_OMx.get_db_connection():
                db_thread = Thread(target=db_jobs_work, args=(300, database_object, sql, None, None))
                # db_thread_WMx = Thread(target=db_jobs_work, args=(300, database_object_WMx, sql, None, None, "WMx"))
                db_thread.daemon = True
                db_thread.start()
                T.append(db_thread)

        elif interface == 'http':
            ''' request DB interface restpi insteady of connecting db dircectly '''
            # db_http_thread = Thread(target=db_jobs_work, args=(300, None, sql, db_http_host, db_url, None))
            # db_http_thread.daemon = True
            # db_http_thread.start()
            # T.append(db_http_thread)

            # -- Interval for checking the data pipelines
            if global_env_name == 'DEV':
                # print('\n\n\n\n\n\n')
                # print(global_env_name)
                # print('\n\n\n\n\n\n')
                db_jobs_interval=30
                # db_jobs_interval=300
            else:
                db_jobs_interval=300

            db_wmx_omx_list = str(db_url).split(",")

            ''' last argument is for multiple db connection'''
            db_http_thread_Wmx = Thread(target=db_jobs_work, args=(db_jobs_interval, None, sql, db_http_host, db_wmx_omx_list[0], 'WMx', multiple_db))
            db_http_thread_Wmx.daemon = True
            db_http_thread_Wmx.start()
            T.append(db_http_thread_Wmx)

            ''' Update Kafka Offset '''
            """
            db_http_thread_Wmx_Offset = Thread(target=db_jobs_kafka_offset_tb, args=(300, None, kafka_sql, db_http_host, db_wmx_omx_list[0]))
            db_http_thread_Wmx_Offset.daemon = True
            db_http_thread_Wmx_Offset.start()
            T.append(db_http_thread_Wmx_Offset)
            """

            if multiple_db:
                db_http_thread_Omx = Thread(target=db_jobs_work, args=(db_jobs_interval, None, sql, db_http_host, db_wmx_omx_list[1], 'OMx', multiple_db))
                db_http_thread_Omx.daemon = True
                db_http_thread_Omx.start()
                T.append(db_http_thread_Omx)

            
            ''' Get backlogs.. only for checking WMx backlog'''
            if backlog:
                db_http_thread_Wmx_Backlog = Thread(target=db_jobs_backlogs_work, args=(300, None, sql_backlog, db_http_host, db_wmx_omx_list[0], 'WMx'))
                db_http_thread_Wmx_Backlog.daemon = True
                db_http_thread_Wmx_Backlog.start()
                T.append(db_http_thread_Wmx_Backlog)

                """
                db_http_thread_Omx_Backlog = Thread(target=db_jobs_backlogs_work, args=(300, None, sql_backlog, db_http_host, db_wmx_omx_list[1], 'OMx'))
                db_http_thread_Omx_Backlog.daemon = True
                db_http_thread_Omx_Backlog.start()
                T.append(db_http_thread_Omx_Backlog)
                """

        # wait for all threads to terminate
        for t in T:
            while t.is_alive():
                t.join(0.5)

    except (KeyboardInterrupt, SystemExit):
        logging.info("# Interrupted..")

    finally:
        if interface == 'db' and db_run:
            database_object.set_db_disconnection()
            database_object.set_init_JVM_shutdown()
            # database_object_WMx.set_db_disconnection()
            # database_object_WMx.set_init_JVM_shutdown()
            # database_object_OMx.set_db_disconnection()
            # database_object_OMx.set_init_JVM_shutdown()

        
    logging.info("Standalone Prometheus Exporter Server exited..!")
    
    
     
 