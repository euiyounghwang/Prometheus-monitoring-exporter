
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
import pytz
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


''' Tracking thread_alert_message '''
tracking_alert_dict = {
    "alert_sent_time" : "1900-01-01 00:00:00"
}

def get_alert_resend_func(alert_duration_time):
       
    ''' global func to call for validating'''
    def get_time_difference(audit_process_name_time):
            ''' get time difference'''
            # lock.acquire()
            # now_time = datetime.datetime.now()
            now_time = datetime.datetime.now(tz=gloabal_default_timezone).strftime('%Y-%m-%d %H:%M:%S')
                    
            print(f"audit_process_name_time - {audit_process_name_time}, : {type(audit_process_name_time)}, now_time - {now_time} : {type(now_time)}")
            """
            date_diff = now_time-audit_process_name_time
            print(f"Time Difference - {date_diff}")
            time_hours = date_diff.seconds / 3600
            """
            # current_time = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
            current_time = datetime.datetime.now(tz=gloabal_default_timezone).strftime('%Y-%m-%d %H:%M:%S')
            print(f"current_time : {current_time}")
            dt_a = datetime.datetime.strptime(str(current_time), '%Y-%m-%d %H:%M:%S')
            dt_b = audit_process_name_time
            time_hours = float((dt_a-dt_b).total_seconds() / 3600)
            print(f"Time Difference to hours - {time_hours}")

            return round(time_hours,3)
        
    
    get_tracking_alert_time = datetime.datetime.strptime(tracking_alert_dict.get("alert_sent_time"), "%Y-%m-%d %H:%M:%S")
    alert_time_difference = get_time_difference(get_tracking_alert_time)
    
    ''' update current the duration time for the time of alert was sent'''
    if alert_time_difference >= alert_duration_time:
    #    tracking_alert_dict.update({"alert_sent_time" : str(datetime.datetime.now(tz=gloabal_default_timezone).strftime("%Y-%m-%d %H:%M:%S"))})
       return True
    else:
        return False
    

def post_request_mail_alert(url):
    ''' request to api endpoint'''
    try:
        
        headers = {
            'Content-type': 'application/json',
            'Connection': 'close'
        }
         
        payload = {
            "env": "dev",
            "to_user": "localhost@testcom",
            "cc_user": "localhost@testcom",
            "subject": "Prometheus Monitoring Alert",
            "message": "Push Alert"
        }
        
        # payload = json.dumps(payload)
        ''' There should be an option to disable certificate verification during SSL connection. It will simplify developing and debugging process. '''
        resp = requests.post(url, json=payload, headers=headers, verify=False)
                        
        logging.info(f"post_request")

        if not (resp.status_code == 200):
            return None
        
        logging.info(f"post_request_mail_alert - {resp}, {resp.status_code}")

        return resp.json()

    except Exception as e:
        logging.info(e)



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
                        ''' *** '''
                        ''' Send alerts every 24 hours '''
                        ''' *** '''
                        # post_request_mail_alert("http://{}:8004/service/push_alert_mail".format(os.getenv("PROMETHEUS_APPS_HOST")))
                        ''' Update timestamp for the alerts'''
                        # tracking_alert_dict.update({"alert_sent_time" : str(datetime.datetime.now(tz=gloabal_default_timezone).strftime("%Y-%m-%d %H:%M:%S"))})

               
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
    parser.add_argument('-port', '--port', dest='port', default=9999, help='port')
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
        logging.info(f"# Flask App's Port : {_port}")

        for t in T:
            while t.is_alive():
                t.join(0.5)
        # work(target_server)
   
    except Exception as e:
        logging.error(e)
        pass