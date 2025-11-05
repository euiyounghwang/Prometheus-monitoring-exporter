
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


def work():
    ''' main process '''
    try:
         
        while True:
            try:
                logging.info("\n\n")
                logging.info("** work func")
               
            except Exception as e:
                logging.info(f"work func : {e}")

                pass
                               
            time.sleep(10)

    # except (KeyboardInterrupt, SystemExit) as e:
    except Exception as e:
        logging.info(e)
   


if __name__ == '__main__':
    """
    Running this service to check the status of tools and send alerts
    python ./standalone-tools-service-export.py
    """
    parser = argparse.ArgumentParser(description="Running this service to check the status of tools and send alerts using this script")
    # parser.add_argument('-t', '--ts', dest='ts', default="https://localhost:9201", help='host target')
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

        for t in T:
            while t.is_alive():
                t.join(0.5)
        # work(target_server)
   
    except Exception as e:
        logging.error(e)
        pass