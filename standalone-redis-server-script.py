
# -*- coding: utf-8 -*-
import sys
import os
import json

import argparse
from dotenv import load_dotenv
import os
from datetime import datetime
from threading import Thread
import requests
import logging
import warnings
import time
import redis
from rediscluster import RedisCluster
from Redis_Service import Redis_Client

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from json import dumps
import logging_loki

warnings.filterwarnings("ignore")

load_dotenv()

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

logging_loki.emitter.LokiEmitter.level_tag = "level"
# assign to a variable named handler 
handler = logging_loki.LokiHandler(
   url="http://{}:3100/loki/api/v1/push".format(os.getenv("LOKI_HOST")),
   version="1",
)
# create a new logger instance, name it whatever you want
logger = logging.getLogger("alert-logger")
logger.addHandler(handler)


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    ''' HTTP Listeners'''

    def _send_cors_headers(self):
        ''' set headers requried for CORS'''
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "x-api-key, Content-Type")


    def send_dict_response(self, d):
        ''' send a dict as Json back to the client '''
        self.wfile.write(bytes(dumps(d), "utf8"))


    def do_GET(self):
        ''' http://localhost:9999/health?kafka_url=localhost:29092,localhost:39092,localhost:49092&es_url=localhost:9200,localhost:9201,localhost:9203'''

        response_dict = {"message" : "Hello World!"}
       
        logging.info(response_dict)
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self._send_cors_headers()
        self.end_headers()

        self.send_dict_response(response_dict)
        


def work():
    ''' get redis all keys from kibana instance'''

    def get_es_configuration_files(path):
        ''' json.loads es-configuration file'''
        with open(path, "r") as read_file:
            data = json.load(read_file)
            return data
        
    def write_es_configuration_files(data):
        try:
            with open(os.getenv("ES_CONFIGURATION_FILE"), 'w') as f:
                # json.dump(data, f)
                f.write(json.dumps(data, indent=2))
        
        except Exception as e:
            logging.error(e)
            '''
            logger.error("Prometheus-Alert-Service",
                extra={"tags": {"service": "prometheus-alert-service", "message" : str(e)}},
            )
            '''
            ''' Push logs to Grafana-Loki'''
            push_log_to_grafana_loki(title_msg=str(e), body_msg=str(e), logger_level="error")



    def get_mapping_host_config():
        ''' get_hostname_from_domain '''
        try:
            ''' get all hots '''
            mapping_hosts = get_es_configuration_files(os.getenv("ES_CONFIGURATION_MAPPING_FILE"))
            # self.logger.info(f"get_mapping_host_config : {hosts}")
            # print(f"get_mapping_host_config : {mapping_hosts}")
                        
            ''' get ./repositoy/mail_config.json '''
            return mapping_hosts
        
        except Exception as e:
           logging.error(e)
           '''
           logger.error("Prometheus-Alert-Service",
                extra={"tags": {"service": "prometheus-alert-service", "message" : str(e)}},
           )
           '''
           ''' Push logs to Grafana-Loki'''
           push_log_to_grafana_loki(title_msg=str(e), body_msg=str(e), logger_level="error")


    def transform_json(mapping_host_dict, configuration_data, key, alert_bool_option):
        ''' load and transform data'''
        try:
            logging.info(f"transform_json")
            key = key.decode('utf-8')
            alert_bool_option = str(alert_bool_option)
            # logging.info(f"key : {key}, value : {str(alert_bool_option).lower()}")
            # logging.info(f"type(alert_bool_option) : {type(alert_bool_option)}")
            
            alert_value = True if str(alert_bool_option).lower() == "true" else False
            logging.info(f"alert_value : {alert_value}, type(alert_value) : {type(alert_value)}")

            ''' get host name matched env name to read their json configuraion'''
            real_host_name = mapping_host_dict.get(key)

            logging.info(f"key : {real_host_name}")
            if real_host_name in configuration_data.keys():
                logging.info(f"OK #1")
                configuration_data[real_host_name]["is_mailing"] = alert_value
                ''' only update sms for Prod env's'''
                if "prod" in key or "dev" in key:
                    logging.info(f"OK #2")
                    configuration_data[real_host_name]["is_sms"] = alert_value

        except Exception as e:
            logging.error(e)
            '''
            logger.error("Prometheus-Alert-Service",
                extra={"tags": {"service": "prometheus-alert-service", "message" : str(e)}},
            )
            '''
            ''' Push logs to Grafana-Loki'''
            push_log_to_grafana_loki(title_msg=str(e), body_msg=str(e), logger_level="error")

    
    def retry_connnection():
        # ... get redis connection here, or pass it in. up to you.
        try:
            redis_client = Redis_Client(os.getenv('REDIS_SERVER_HOST'))
            redis_client.Set_Connect()
            return redis_client
        except (redis.exceptions.ConnectionError, 
                redis.exceptions.BusyLoadingError):
            logging.error(e)
            return None
            

    try:
        ''' Initial Connection'''
        redis_client = retry_connnection()
         
        while True:
            ''' get es configuration file'''
            configuration_data = get_es_configuration_files(os.getenv("ES_CONFIGURATION_FILE"))
            # logging.info(f"configuration_data : {json.dumps(configuration_data, indent=2)}")
            
            """
            # startup_nodes = [
            #     {"host": os.getenv('REDIS_SERVER_HOST'), "port": 6379},
            # ]
            # r = RedisCluster(startup_nodes=startup_nodes, decode_responses=True, skip_full_coverage_check=False)
            r = redis.StrictRedis(host=os.getenv('REDIS_SERVER_HOST'), port=6379, db=0)
            """
            try:
                logging.info("\n\n")
                if redis_client is not None:
                    logging.info(f"Redis is Active")
                else:
                    ''' Retry connection'''
                    redis_client = retry_connnection()

                """
                json_test = {
                    "alert" : "false"
                }
                jsonDataDict = json.dumps(json_test, ensure_ascii=False).encode('utf-8')
                r.set("dev", jsonDataDict)
                """
                logging.info(f"The number of all keys is {len(list(redis_client.Get_keys()))} ..")

                ''' --------------- '''
                ''' get host name matched env name to read their json configuraion'''
                ''' --------------- '''
                mapping_host_dict = get_mapping_host_config()
                
                is_any_updated = False
                if len(list(redis_client.Get_keys())) > 0:
                    is_any_updated = True

                # Get all keys
                for key in redis_client.Get_keys():
                    print(key, redis_client.Get_Memory_dict(key), redis_client.Get_Memory_dict(key)["alert"], json.dumps(redis_client.Get_Memory_dict(key), indent=2))
                    transform_json(mapping_host_dict, configuration_data, key, redis_client.Get_Memory_dict(key)["alert"])

                    key = key.decode('utf-8')
                    message = "[{}] Alert : {}, {}".format(str(key).upper(), redis_client.Get_Memory_dict(key)["alert"], redis_client.Get_Memory_dict(key)["message"]),
                    '''
                    logger.info("Prometheus-Alert-Service - {}".format(message),
                        extra={"tags": {"service": "prometheus-alert-service", "message" : "{} -> {}, notes : {}".format(key, redis_client.Get_Memory_dict(key)["alert"], redis_client.Get_Memory_dict(key)["message"])}},
                    )
                    '''
                    msg = "{} -> {}, notes : {}".format(key, redis_client.Get_Memory_dict(key)["alert"], redis_client.Get_Memory_dict(key)["message"])
                    ''' Push logs to Grafana-Loki'''
                    push_log_to_grafana_loki(title_msg=msg, body_msg=msg, logger_level="info")

                    ''' delete key'''
                    # r.delete(key)
                    redis_client.Set_Delete_Keys(key)
                
                ''' Check all keys'''
                # logging.info(f"Length of all keys from Redis : {len(list(redis_client.Get_keys()))}")

                # logging.info(f"configuration_data - {json.dumps(configuration_data, indent=2)}")
                if is_any_updated:
                    write_es_configuration_files(configuration_data)
                
            except Exception as e:
                logging.info(f"Redis is InActive")
                redis_client = None
                pass
                               
            time.sleep(3)

    # except (KeyboardInterrupt, SystemExit) as e:
    except Exception as e:
        logging.info(e)
        # message = "[{}]".format(str(key).upper()),
        '''
        logger.error("Prometheus-Alert-Service {}".format(message),
                    extra={"tags": {"service": "prometheus-alert-service", "message" : str(e)}},
                )
        '''
        ''' Push logs to Grafana-Loki'''
        push_log_to_grafana_loki(title_msg=str(e), body_msg=str(e), logger_level="error")

    finally:
        redis_client.Set_Close()


def push_log_to_grafana_loki(title_msg, body_msg, logger_level):
    ''' push msg log into grafana-loki '''

    def loki_timestamp():
      return f"{(int(time.time() * 1_000_000_000))}"

    try:
        url = 'https://{}:3100/loki/api/v1/push'.format(os.getenv('LOKI_HOST'))
        headers = {
            'Content-type': 'application/json'
        }
        ''' 'service': 'prometheus-monitoring-service','message': '[DEV] Services, Alert : True, Issues : Server Active : Green, ES Data Pipline : Red','env': 'PROD' '''
        payload = {
            'streams': [
                {
                    'stream' : {
                        'service': 'prometheus-alert-service',
                        "message": body_msg,
                        "logger" : "prometheus-logger",
                        "level" : logger_level
                    },
                    'values': [
                        [
                            loki_timestamp(),
                            title_msg
                        ]
                    ]
                }
            ]
        }
        # payload = json.dumps(payload)
        response = requests.post(url, json=payload, headers=headers, verify=False)
        print(response.status_code)

    except Exception as e:
        logging.error(e)


def HTTP_Server():
    ''' Add HTTP Server for checking this process'''
    try:
        port = 9116
        server = ThreadingHTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
        logging.info('Http Server running on port:{}'.format(port))
        server.serve_forever()
    except KeyboardInterrupt:
        logging.info("#Interrupted..")
        

if __name__ == '__main__':
    """
    https://hyewon-s-dev.tistory.com/5
    dis default port: 6379
    ./scr/redis-server --daemonize yes --protected-mode no

    ./redis-cli ping
    ./redis-cli shutdown
    ./redis-cli
    """
    parser = argparse.ArgumentParser(description="Index into Elasticsearch using this script")
    # parser.add_argument('-t', '--ts', dest='ts', default="https://localhost:9201", help='host target')
    args = parser.parse_args()
    
        
    # if args.ts:
    #     target_server = args.ts
        
    # --
    # Only One process we can use due to 'Global Interpreter Lock'
    # 'Multiprocessing' is that we can use for running with multiple process
    # --
    try:
        ''' Add HTTP Server for checking this process'''
        # HTTP_Server()
    
        T = []
        th1 = Thread(target=work, args=())
        th1.daemon = True
        th1.start()
        T.append(th1)

        ''' http://localhost:9116/ -> Add HTTP Server for checking this process'''
        th2 = Thread(target=HTTP_Server, args=())
        th2.daemon = True
        th2.start()
        T.append(th2)
        
        for t in T:
            while t.is_alive():
                t.join(0.5)
        # work(target_server)
   
    except Exception as e:
        logging.error(e)
        pass