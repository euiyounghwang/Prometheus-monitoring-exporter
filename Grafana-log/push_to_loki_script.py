# -*- coding: utf-8 -*-
import time
import argparse
import os
from datetime import datetime
from threading import Thread
import requests
import logging
import socket
import warnings
warnings.filterwarnings("ignore")



def get_info_error(line, buffer):
    ''' return all wrap log'''
    if 'INFO' in line or 'ERROR' in line:
        if len(buffer) > 0:
            yield ",".join(buffer)
            buffer = []
        buffer.append(line)
    else:
        buffer.append(line)
        

def get_error(line, buffer):
    ''' return only ERROR wrap log'''
    print(line)
    if 'ERROR' in line:
        if len(buffer) > 0:
            yield ",".join(buffer)
            buffer = []
        buffer.append(line)
    else:
        if 'INFO' not in line:
            buffer.append(line)
    print(buffer)
    

def follow(thefile, logs):
    '''generator function that yields new lines in a file
    '''
    # seek the end of the file
    thefile.seek(0, os.SEEK_END)
    
    buffer = []
    # start infinite loop
    while True:
        # read last line of file
        line = thefile.readline()
        # print(line)
        # sleep if file hasn't been updated
        if not line:
            ''' add new logic'''
            ''' ------------'''
            if len(buffer) > 0:
                yield "".join(buffer)
                buffer = []
            ''' ------------'''
            time.sleep(0.1)
            continue

        # print(line)
        # get_error(line, buffer)
        ''' return only ERROR wrap log'''
        ''' get_error(line, buffer) '''
        if logs == 'ERROR':
            if 'ERROR' in line:
                if len(buffer) > 0:
                    yield ",".join(buffer)
                    buffer = []
                buffer.append(line)
            else:
                if 'INFO' not in line or 'WARN' not in line:
                    buffer.append(line)
        else:
            ''' return all wrap log'''
            ''' get_info_error'''
            if 'INFO' in line or 'ERROR' in line:
                if len(buffer) > 0:
                    yield "".join(buffer)
                    buffer = []
                buffer.append(line)
            else:
                buffer.append(line)
            yield line


def push_to_log_via_api(log_status, hostname, filename, message):
    ''' send logs to api '''
    ''' call to interface RestAPI'''
    try:
        request_body = {
            "log_status": log_status,
            "env": os.environ["ENV"],
            "host": socket.gethostname().split(".")[0],
            "host_name": hostname,
            "log_filename": filename,
            "message": message
        }
        
        logging.info("push_to_log_via_api")
        http_urls = "http://{}:8010/log/push_to_loki".format(os.environ["LOKI_RESTAPI_HOST"])
        resp = requests.post(url=http_urls, json=request_body, timeout=600)
                        
        if not (resp.status_code == 200):
            logging.info("push_to_log_via_api in 404 response")

        logging.info("push_to_log_via_api - {}".format(resp.json()))
        ''' send logs through interface restapi'''
        

    except Exception as e:
        logging.error(e)

    
def work(path, log_filename, hostname, logs):
    ''' main job'''

    ''' Readline with INFO/ERROR with Seek Offset'''
    try:
        logfile = open("{}/{}".format(path, log_filename),"r")
        loglines = follow(logfile, logs)
        # iterate over the generator
        for line in loglines:
            print(line)
            ''' send logs to inteface api for saving them in Grafana-loki'''
            log_status = "INFO"
            if 'ERROR' in line:
                log_status = "ERROR"
            push_to_log_via_api(log_status, hostname, log_filename, line)
    
    except Exception as e:
        # logging.error(e)
        pass



if __name__ == '__main__':
    '''
    (.venv) ➜  python ./push_to_loki_script.py --path /home/devuser --filename test1.log --hostname Data_Transfer_Node_#1
    '''
    parser = argparse.ArgumentParser(description="Index into Elasticsearch using this script")
    parser.add_argument('-p', '--path', dest='path', default="/home/devuser", help='path for log')
    parser.add_argument('-f', '--filename', dest='filename', default="test1.log,test2.log", help='filename for log')
    parser.add_argument('-t', '--hostname', dest='hostname', default="hostname", help='hostname')
    parser.add_argument('-l', '--logs', dest='logs', default="all", help='logs')
    args = parser.parse_args()
    
    if args.path:
        path = args.path

    if args.filename:
        log_filename = args.filename

    if args.hostname:
        hostname = args.hostname

    if args.logs:
        logs = args.logs

    # print(socket.gethostname())

    T = []
        
    # --
    # Only One process we can use due to 'Global Interpreter Lock'
    # 'Multiprocessing' is that we can use for running with multiple process
    # --
    try:
        for collect_log in log_filename.split(","):
            th1 = Thread(target=work, args=(path, collect_log, hostname, logs, ))
            th1.daemon = True
            th1.start()
            T.append(th1)

        # wait for all threads to terminate
        for t in T:
            while t.is_alive():
                t.join(0.5)

    except (KeyboardInterrupt, SystemExit):
        logging.info("# Interrupted..")
        
    except Exception as e:
        logging.error(e)
    