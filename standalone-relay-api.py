import time
import datetime
import threading
import pytz
from threading import Thread
from dotenv import load_dotenv
from flask import Flask, render_template, jsonify
import argparse
import logging
import requests
import os
import json
import sys
import warnings

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

logger = logging.getLogger("ES-API-Relay-Service-Script")

''' Tracking thread_alert_message '''
tracking_dict = {
    
}


app = Flask(__name__)

@app.route('/')
def hello():
    # return render_template('./index.html', host_name=socket.gethostname().split(".")[0], linked_port=port, service_host=env_name)
    return {
        "app" : "standalone-es-api-relay-service",
        "started_time" : datetime.datetime.now(),
        "tools": [
            {
               "message" : "standalone-relay-api.py",
               "tracking" : tracking_dict
            }
        ]
    }


@app.route('/relay_service/api/<path:sub_url>')
def relay_service(sub_url):
    ''' Using <path:sub_url> captures the entire sub-path, including any forward slashes (/) '''
    ''' Sample URL : http://localhost:9981/relay_service/api/https://spark_master_url:4441/api/v1/applications/app-20261016134903-0000/streaming/statistics'''
    '''
    [2026-10-30 15:35:00,204] [ES-API-Relay-Service-Script] [INFO] json - {
        "startTime": "2026-10-16T17:49:06.995GMT",
        "batchDuration": 10000,
        "numReceivers": 0,
        "numActiveReceivers": 0,
        "numInactiveReceivers": 0,
        "numTotalCompletedBatches": 121955,
        "numRetainedCompletedBatches": 2000,
        "numActiveBatches": 1,
        "numProcessedRecords": 248585,
        "numReceivedRecords": 248587,
        "avgInputRate": 0.20169915042478223,
        "avgSchedulingDelay": 0,
        "avgProcessingTime": 1276,
        "avgTotalDelay": 1276
    }

    {"code":404,"error":"no such app: app-20261029203909-0007"}
    
    '''
    logger.info(f"api_url = {sub_url}")
    try:
        # query_params = {
        #     "page": 2,
        #     "search": "flask"
        # }

        response = requests.get(sub_url, params=None, verify=False)
        logger.info(f"response - {response.status_code}")

        if response.status_code != 200:
            return jsonify({"error": "External API Error", "error": response.text, "code" : response.status_code}), response.status_code
        
        logger.info(f"json - {json.dumps(response.json(), indent=2)}")

        return response.json()
    except Exception as e:
        logger.error(f"work func : {e}")
        

def work():
    ''' Main'''
    while True:
        try:
            print("\n")
            logger.info("** work func ** ")

       
        # except (KeyboardInterrupt, SystemExit) as e:           
        except Exception as e:
            logger.error(f"work func : {e}")
            pass
    
        time.sleep(60)
       


if __name__ == "__main__":
    ''' This script will run and sending the alert value via CRONJOB'''
    # schedule_thread = threading.Thread(target = job)
    # schedule_thread.start()

    parser = argparse.ArgumentParser(description="Running this service allows us to request the api service using this script")
    parser.add_argument('-port', '--port', dest='port', default=9981, help='port')
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
            
    #   T = []
    #   th1 = Thread(target=work, args=())
    #   th1.daemon = True
    #   th1.start()
    #   T.append(th1)

      ''' Expose this app to acesss'''
      ''' Flask at first run: Do not use the development server in a production environment '''
      ''' For deploying an application to production, one option is to use Waitress, a production WSGI server. '''
      # app.run(host="0.0.0.0", port=int(port)-4000)
      from waitress import serve
      serve(app, host="0.0.0.0", port=_port)
      logger.info(f"# Flask App's Port : {_port}")
      
    #   for t in T:
    #     while t.is_alive():
    #         t.join(0.5)

    except Exception as e:
      logger.error(e)