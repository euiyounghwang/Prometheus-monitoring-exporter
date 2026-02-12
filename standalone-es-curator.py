
# -*- coding: utf-8 -*-
import sys
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
import time
from flask import Flask, render_template
from datetime import datetime, timedelta

warnings.filterwarnings("ignore")

load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("Tools-Alert-Script")

''' Tracking thread_alert_message '''
tracking_dict = {
    
}


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
    

def get_es_instance(es_config_json):
    """
    Docstring for get_es_instance
    
    :param es_config_json: Description
    """
    def get_headers(es_config_json):
        ''' Elasticsearch Header '''
        ''' 
        Basic Authentication is a method for an HTTP user agent (e.g., a web browser) 
        to provide a username and password when making a request. 
        You can send the authorization header 
        when making requests and accessing to ES Cluster based on Search-Guard as X-pack. 
        
        Basic Auth : 
        {
            'Content-type': 'application/json', 
            'Authorization' : 'Basic base64.encode(id:password), 
            'Connection': 'close'
        }
        '''
        headers = {
                'Content-type': 'application/json', 
                'Authorization' : 'Basic {}'.format(es_config_json),
                'Connection': 'close'
        }
        # print(f"headers : {json.dumps(headers, indent=2)}")
        return headers
    
    logging.info(f"Trying access {es_config_json.get('env')}")
    es_client = Elasticsearch(hosts=list(es_config_json.get("service").strip().split(",")), headers=get_headers(es_config_json.get("basic_auth")), timeout=5, verify_certs=False)
    print(f"An instance of the ES client : {es_client}")

    if not es_client.ping():
        logging.error(f"Trying access {es_config_json.get('env')} - Error Occured")
        return None

    return es_client


def perform_delete_old_indices(es_client, es_indices_list, date_format, deleted_commands, _threshold_days):
    """
    Docstring for perform_delete_old_indices
    
    :param es_client: Description
    :param es_indices_list: Description
    :param date_format: Description
    :param deleted_commands: Description
    :param _threshold_days: Description
    """
    def try_exists_index(es_client, _index, deleted_commands):
        try:
            if es_client.indices.exists(_index):
                if not deleted_commands:
                    print(f"Please check the option to delete in config file..")    
                    return
                response = es_client.indices.delete(index=_index, ignore=[400, 404])
                print(response)
                print(f"{_index} was removed..")
        except Exception as e:
            # logging.error(e)
            print(e)
            pass

    threshold_days = _threshold_days
    two_days_ago = datetime.now().date() - timedelta(days=threshold_days)
    print(f"** es_indices_list : {es_indices_list}, Threshold_days of date value: {two_days_ago}")

    try:
        will_be_removed = 0
        if es_indices_list:
            for logstash_es_indic in es_indices_list:
                file_date_str = logstash_es_indic.rsplit('-', 1)[1]
                # file_date = datetime.strptime(file_date_str, "%Y.%m.%d").date()
                file_date = datetime.strptime(file_date_str, date_format).date()
                # print(file_date)

                # 3. 날짜 비교
                if file_date <= two_days_ago:
                    # print(f"{logstash_es_indic}: 이틀 이상 지난 파일입니다.")
                    try_exists_index(es_client, logstash_es_indic, deleted_commands)
                    will_be_removed += 1
                else:
                    print(f"{logstash_es_indic} is a recent file")
            return will_be_removed
        else:
            print("No ES Indices with your pattern")
            return will_be_removed
    except Exception as e:
        pass


def work() -> None:
    """
    work main function

    Args:
        None
    Returns:
        None
    """
    while True:
        try:
            logger.info("\n\n")
            logger.info("** work func")

            ''' Get ES Instance'''
            for each_es_env in Util.get_json_load("./standalone-es-curator.json"):
                es_client = get_es_instance(each_es_env)
                if es_client:
                    logging.info(f"{es_client}")

                    will_be_removed = perform_delete_old_indices(es_client, 
                                                                 list(es_client.indices.get(each_es_env.get("delete_indices_pattern")).keys()), 
                                                                 each_es_env.get("date_pattern"),
                                                                 each_es_env.get("deleted_commands"),
                                                                 each_es_env.get("threshold_days")
                                                                 )
                    tracking_dict.update({
                            each_es_env.get("env") : {
                                "checked_time" : datetime.now(),
                                "service" : each_es_env.get("service"),
                                "es_indices_pattern" : each_es_env.get("delete_indices_pattern"),
                                "old_es_indices_total_count" : will_be_removed,
                                "service_completed" : "Green"
                            }
                        })
            
            logger.info("\n\n")
            logger.info("** Time sleep..")

        # except (KeyboardInterrupt, SystemExit) as e:           
        except Exception as e:
            # logger.error(f"work func : {e}")
            pass

        time.sleep(60*60*24)
   

app = Flask(__name__)

@app.route('/')
def hello():
    # return render_template('./index.html', host_name=socket.gethostname().split(".")[0], linked_port=port, service_host=env_name)
    return {
        "app" : "standalone-es-curator.py",
        "started_time" : datetime.now(),
        "tools": [
            {
               "message" : "standalone-es-curator.py",
                "tracking" : tracking_dict
            }
        ]
    }


if __name__ == '__main__':
    """
    Ingnore ssl pip - pip install numpy==1.26.4 --trusted-host pypi.org --trusted-host files.pythonhosted.org
    Running this service allows us to check and delete old ES indices
    python ./standalone-es-curator.py
    """
    parser = argparse.ArgumentParser(description="Running this service allows us to check and delete old ES indices using this script")
    parser.add_argument('-port', '--port', dest='port', default=9998, help='port')
    args = parser.parse_args()
    
    global gloabal_default_timezone

        
    if args.port:
        _port = args.port

    gloabal_default_timezone = pytz.timezone('US/Eastern')

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

        ''' Expose this app to acesss'''
        ''' Flask at first run: Do not use the development server in a production environment '''
        ''' For deploying an application to production, one option is to use Waitress, a production WSGI server. '''
        # app.run(host="0.0.0.0", port=int(port)-4000)
        from waitress import serve
        serve(app, host="0.0.0.0", port=_port)
        logger.info(f"# Flask App's Port : {_port}")

        for t in T:
            while t.is_alive():
                t.join(0.5)
        # work(target_server)
   
    except Exception as e:
        logger.error(e)