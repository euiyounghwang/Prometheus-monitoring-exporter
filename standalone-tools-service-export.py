
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
import socket
import pytz
import datetime, time
from flask import Flask, render_template


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
tracking_xMatters_alert_dict = {
    "alert_sent_time" : "1900-01-01 00:00:00"
}

def get_alert_resend_func(alert_duration_time, tracking_alert_dict) -> bool:
    """
    Request to api 'get_alert_resend_func'

    Args:
        alert_duration_time (str) : time
        tracking_alert_dict (Json) : Manage the alert event using timestamp to send an email alert at a set time inverval
    Returns:
        Json
    """
       
    ''' global func to call for validating'''
    def get_time_difference(audit_process_name_time):
            ''' get time difference'''
            # lock.acquire()
            # now_time = datetime.datetime.now()
            # now_time = datetime.datetime.now(tz=gloabal_default_timezone).strftime('%Y-%m-%d %H:%M:%S')
                    
            # print(f"audit_process_name_time - {audit_process_name_time}, : {type(audit_process_name_time)}, now_time - {now_time} : {type(now_time)}")
            """
            date_diff = now_time-audit_process_name_time
            print(f"Time Difference - {date_diff}")
            time_hours = date_diff.seconds / 3600
            """
            # current_time = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
            current_time = datetime.datetime.now(tz=gloabal_default_timezone).strftime('%Y-%m-%d %H:%M:%S')
            # print(f"current_time : {current_time}")
            dt_a = datetime.datetime.strptime(str(current_time), '%Y-%m-%d %H:%M:%S')
            dt_b = audit_process_name_time
            time_hours = float((dt_a-dt_b).total_seconds() / 3600)
            print(f"\nCurrent_time : {current_time}, Time Difference to hours - {time_hours}\n")

            return round(time_hours,3)
        
    
    get_tracking_alert_time = datetime.datetime.strptime(tracking_alert_dict.get("alert_sent_time"), "%Y-%m-%d %H:%M:%S")
    alert_time_difference = get_time_difference(get_tracking_alert_time)
    
    ''' update current the duration time for the time of alert was sent'''
    if alert_time_difference >= alert_duration_time:
    #    tracking_alert_dict.update({"alert_sent_time" : str(datetime.datetime.now(tz=gloabal_default_timezone).strftime("%Y-%m-%d %H:%M:%S"))})
       return True
    else:
        return False
    

def post_request_mail_alert(url, service) -> json:
    """
    Request to api endpoint

    Args:
        None
    Returns:
        Json
    """
    try:
        
        headers = {
            'Content-type': 'application/json',
            'Connection': 'close'
        }
         
        payload = {
            "env": "Tools",
            # "to_user": os.getenv("MAIL_TO"),
            # "cc_user": os.getenv("MAIL_CC"),
            # "to_user": global_mail_configuration.get("tools").get("dev_mail_list"),
            # "cc_user": global_mail_configuration.get("tools").get("dev_mail_list"),
            "to_user": global_mail_configuration.get("tools").get("mail_list"),
            "cc_user": global_mail_configuration.get("tools").get("cc_list"),
            "subject": "Prometheus Monitoring Alert for the Service",
            "message": "The <b>{}</b> service (<a href=\"{}\">{}</a>) was offline. <BR/>Please check the service now.".format(
                service, 
                gloabl_configuration.get("config").get("xmatters_webhook_url"),
                gloabl_configuration.get("config").get("xmatters_webhook_url")
            )
        }
        
        # payload = json.dumps(payload)
        resp = requests.post(url, json=payload, headers=headers, verify=False)
                        
        if not (resp.status_code == 200):
            return None
        
        logger.info(f"post_request_mail_alert - {resp}, {resp.status_code}")

        return resp.json()

    except Exception as e:
        logger.error(e)



def post_request_to_prometheus() -> json:
    """
    Request to proemtheus for the metrics

    Args:
        None
    Returns:
        Json
    """
    try:
        resp = requests.get(
                url="http://{}:9090/api/v1/query?query=xMatters_service_health_metric{{}}".format(os.getenv("PROMETHEUS_APPS_HOST"), os.getenv("PROMETHEUS_LOOKUP_HOST")), 
                auth=(os.getenv("PROMETHEUS_USERNAME"), os.getenv("PROMETHEUS_PASSWORD")), 
                timeout=5, 
                verify=False
            )
                        
        logger.info(f"post_request_to_prometheus")

        if not (resp.status_code == 200):
            return None
        
        logger.info(f"post_request_to_prometheus - {resp}, {resp.status_code}")

        return resp.json()

    except Exception as e:
        logger.error(e)



gloabl_configuration = {}
def get_global_configuration() -> None:
    """
    get global configuration through ES configuration REST API

    Args:
        None
    Returns:
        None
    """
   
    global gloabl_configuration

    try:
        es_config_host = os.getenv("PROMETHEUS_APPS_HOST")
        resp = requests.get(url="http://{}:8004/config/get_gloabl_config".format(es_config_host), timeout=5)
                
        if not (resp.status_code == 200):
            ''' save failure node with a reason into saved_failure_dict'''
            logger.error(f"get_global_configuration api do not reachable")
            return {}
                
        # logging.info(f"get_mail_config - {resp}, {json.dumps(resp.json(), indent=2)}")
        logger.info(f"get_global_configuration - {resp}")
        gloabl_configuration = resp.json()
        
    except Exception as e:
        logger.error(e)


global_mail_configuration = {}
def get_mail_configuration() -> None:
    """
    interface es_config_api http://localhost:8004/config/get_mail_config

    Args:
        None
    Returns:
        None
    """

    global global_mail_configuration
    try:
        es_config_host = os.getenv("PROMETHEUS_APPS_HOST")
        logger.info(f"get_mail_configuration_es_config_host : {es_config_host}")
        resp = requests.get(url="http://{}:8004/config/get_mail_config".format(es_config_host), timeout=5)
                
        if not (resp.status_code == 200):
            ''' save failure node with a reason into saved_failure_dict'''
            logger.error(f"es_config_interface api do not reachable")
            return None
                
        global_mail_configuration = resp.json()
        

    except Exception as e:
        logger.error(e)
        pass


def get_xMatters_status(resp, service) -> None:
    """
    get_xMatters_status

    Args:
        resp (Json) : Json result from the Prometheus
        service (str) : The name of service
    Returns:
        None
    """
    try:
        if resp:
            logger.info(f"resp - {json.dumps(resp, indent=2)}")
            data = resp.get('data').get('result')[0]
            xMatters_value = int(data.get('value')[1])

            ''' Printout '''
            # logging.info(f"global_mail_configuration : {json.dumps(global_mail_configuration.get('tools'), indent=2)}")
            # logging.info(f"global_mail_configuration : {json.dumps(global_mail_configuration.get('tools').get('is_mailing'), indent=2)}")
            if global_mail_configuration.get('tools').get('is_mailing'):
                logger.info(f"Alert is True")
            else:
                logger.info(f"Alert is False")

            ''' Active if xMatters_value is 1, InActive if xMatters_value is 2'''
            if xMatters_value == 1:
            # if xMatters_value == 2:
                logger.info(f"{service} Status - Active..")
            else:  
                logger.info(f"{service} Status - InActive..")
                logger.info(f"tracking_xMatters_alert_dict - {tracking_xMatters_alert_dict}")
                ''' *** '''
                ''' Will be sent an alert if the value of is_mailing in global configuration file is True '''
                ''' Sending alerts to the Team'''
                ''' Send alerts every 24 hours '''
                ''' *** '''
                if global_mail_configuration.get('tools').get('is_mailing'):
                    ''' ** Checking the time interval '''
                    if get_alert_resend_func(24, tracking_xMatters_alert_dict):
                        logger.warning(f"** Sending an alert **")
                        
                        ''' Send an email alert'''
                        post_request_mail_alert("http://{}:8004/service/push_alert_mail".format(os.getenv("PROMETHEUS_APPS_HOST")), service)

                        ''' Update timestamp for the alerts'''
                        tracking_xMatters_alert_dict.update({"alert_sent_time" : str(datetime.datetime.now(tz=gloabal_default_timezone).strftime("%Y-%m-%d %H:%M:%S"))})
                    else:
                        logger.info(f"** Will be sent an alert every 24 hrs **")
                else:
                    logger.warning(f"** Alert value was False for the endpoint **")

    except Exception as e:
        logger.error(e)
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

            ''' Call get_global_configuration func'''
            get_global_configuration()

            ''' Call get_mail_configuration func'''
            get_mail_configuration()

            ''' Call to the Proemtheus for the status of xMatters'''
            get_xMatters_status(post_request_to_prometheus(), "xMatters")

        # except (KeyboardInterrupt, SystemExit) as e:           
        except Exception as e:
            logger.error(f"work func : {e}")
            pass

        time.sleep(60)
   

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
        logger.info(f"# Flask App's Port : {_port}")

        for t in T:
            while t.is_alive():
                t.join(0.5)
        # work(target_server)
   
    except Exception as e:
        logger.error(e)