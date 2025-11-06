
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
import socket
from flask import Flask, render_template


warnings.filterwarnings("ignore")

load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)


def post_request_to_prometheus():
    ''' request to proemtheus for the metrics'''
    try:
        resp = requests.get(
                url="http://{}:9090/api/v1/query?query=xMatters_service_health_metric{{}}".format(os.getenv("PROMETHEUS_APPS_HOST"), os.getenv("PROMETHEUS_LOOKUP_HOST")), 
                auth=(os.getenv("PROMETHEUS_USERNAME"), os.getenv("PROMETHEUS_PASSWORD")), 
                timeout=5, 
                verify=False
            )
                        
        logging.info(f"post_request_to_prometheus")

        if not (resp.status_code == 200):
            return None
        
        logging.info(f"post_request_to_prometheus - {resp}, {resp.status_code}")

        return resp.json()

    except Exception as e:
        logging.info(e)


def work():
    ''' main process '''
    try:
         
        while True:
            try:
                logging.info("\n\n")
                logging.info("** work func")

                ''' request to proemtheus for the metrics'''
                resp = post_request_to_prometheus()
                if resp:
                    logging.info(f"resp - {json.dumps(resp, indent=2)}")
                    data = resp.get('data').get('result')[0]
                    xMatters_value = int(data.get('value')[1])
                    ''' Active if xMatters_value is 1, InActive if xMatters_value is 2'''
                    if xMatters_value == 1:
                        logging.info(f"xMatters Status - Active..")
                    else:
                        logging.info(f"xMatters Status - InActive..")
                        ''' Sending alerts to the Team'''
               
            except Exception as e:
                logging.info(f"work func : {e}")
                pass
                               
            time.sleep(30)

    # except (KeyboardInterrupt, SystemExit) as e:
    except Exception as e:
        logging.info(e)
   

app = Flask(__name__)


@app.route('/')
def hello():
    # return render_template('./index.html', host_name=socket.gethostname().split(".")[0], linked_port=port, service_host=env_name)
    return {"app" : "standalone-tools-service-export.py"}



if __name__ == '__main__':
    """
    Running this service to check the status of tools and send alerts
    python ./standalone-tools-service-export.py
    """
    parser = argparse.ArgumentParser(description="Running this service to check the status of tools and send alerts using this script")
    parser.add_argument('-t', '--ts', dest='ts', default="https://localhost:9201", help='host target')
    args = parser.parse_args()
    
        
    # if args.ts:
    #     target_server = args.ts
        
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
        port = 9999
        serve(app, host="0.0.0.0", port=9999)
        logging.info(f"# Flask App's Port : {port}")

        for t in T:
            while t.is_alive():
                t.join(0.5)
        # work(target_server)
   
    except Exception as e:
        logging.error(e)
        pass