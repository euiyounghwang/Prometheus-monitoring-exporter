
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

        # except (KeyboardInterrupt, SystemExit) as e:           
        except Exception as e:
            logger.error(f"work func : {e}")
            pass

        time.sleep(60)
   

app = Flask(__name__)

@app.route('/')
def hello():
    # return render_template('./index.html', host_name=socket.gethostname().split(".")[0], linked_port=port, service_host=env_name)
    return {
        "app" : "standalone-es-curator.py",
        "started_time" : datetime.datetime.now(),
        "tools": [
            {
               "message" : "standalone-es-curator.py"
            }
        ]
    }


if __name__ == '__main__':
    """
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