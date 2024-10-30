# -*- coding: utf-8 -*-
import time
import argparse
import os
from datetime import datetime
from threading import Thread
import requests
import logging
import socket
from json import dumps
import sys
import logstash
import warnings
warnings.filterwarnings("ignore")

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)



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
    

def follow(thefile, logs, is_end_seek=True):
    '''generator function that yields new lines in a file
    '''
    if is_end_seek:
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
                # if 'ERROR' in line:
                if 'INFO' not in line and 'WARN' not in line:
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
            # yield line


def push_to_logstash(log_status, hostname, filename, message):
    ''' push logs to logstash'''
    host = os.environ["LOGSTASH_HOST"]
    SOCEKT_PORT = 5950

    # Monitoring
    ''' "message" => "{'message': '[test.log] [Dev] 24/10/29 00:00:01 INFO myLogger: 2024-10-29 00:00:01.803 Elastic INSERT START for queueid: 123456\\n'}", '''
    extra = {
        # "log_status": log_status,
        # # "env": os.environ["ENV"],
        # "host": socket.gethostname().split(".")[0],
        # "host_name": hostname,
        # "log_filename": filename,
        "message": "[{}] [{}] {}".format(filename, os.environ["ENV"], message)
    }
    
    """:
    try:
        # SOC = UDP_SOCKET(SOCKET_SERVER_IP, 5959)
        SOC = TCP_SOCKET(SOCKET_SERVER_IP, 5950)
        for _ in range(4):
            SOC.socket_logstash_handler(log_sample_data)
    except Exception as e:
        print(e)
    """

    ''' python ./get-pip.py -> pip install python-logstash '''
    ''' https://github.com/vklochan/python-logstash/tree/master '''

    test_logger = logging.getLogger('python-logstash-logger')
    test_logger.setLevel(logging.INFO)
    '''test_logger.addHandler(logstash.LogstashHandler(host, SOCEKT_PORT, version=1))'''
    test_logger.addHandler(logstash.TCPLogstashHandler(host, SOCEKT_PORT, version=1))
    # test_logger.addHandler(logstash.UDPLogstashHandler(host, SOCEKT_PORT, version=1))

    # test_logger.error('python-logstash: test logstash error message.')
    # test_logger.info('python-logstash: test logstash info message.')
    # test_logger.warning('python-logstash: test logstash warning message.')

    # test_logger.info('python-logstash: test extra fields', extra=extra)
    test_logger.info(extra)

    
def work(path, log_filename, hostname, logs):
    ''' main job'''
    '''
    To save spark text log, we need to pass it to filebeat-logstash-es cluster.
    However, if we pass all lines in the spark log or archive log files to logstash using filebeat, a lot of traffic will be generated.
    So, instead of filebeat, I implemented a python script as agent to read only error logs and pass them to logstash.
    -- ./push_to_logstash.sh start (This script will be run as agent to send text logs to logstash using TCP socket)
    Then, The Grafana dashboard will read the ES log index in ES cluster and show ERROR logs in near real time.
    '''
    ''' Readline with INFO/ERROR with Seek Offset'''
    try:
        logfile = open("{}/{}".format(path, log_filename),"r")
        loglines = follow(logfile, logs)
        # loglines = follow(logfile, logs, is_end_seek=False)
        # iterate over the generator
        for line in loglines:
            # line = str(line).replace("\n", "")
            print(line)
            ''' send logs to inteface api for saving them in Grafana-loki'''
            log_status = "INFO"
            if 'ERROR' in line:
                log_status = "ERROR"
            push_to_logstash(log_status, hostname, log_filename, line)
    
    except Exception as e:
        logging.error(e)
        pass



def server_listen():
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = 2000
    serversocket.bind(("0.0.0.0", 2000))
    serversocket.listen(5) # become a server socket, maximum 5 connections

    logging.info("Wating a session..via PORT {}".format(str(port)))


    while True:
        # print("Waiting for connection")
        connection, client = serversocket.accept()
        
        try:
            # print("Connected to client IP: {}".format(client))
                
            # Receive and print data 1024 bytes at a time, as long as the client is sending something
            while True:
                data = connection.recv(1024)
                # print("Received data: {}".format(data))

                ''' get df -h /apps/ '''
            
                if not data:
                    break

        except Exception as e:
            logging.error("# Interrupted..{}".format(e))

        finally:
            connection.close()


if __name__ == '__main__':
    '''
    [install pip for python2.7] python ./get-pip.py ➜ [install the library] pip install python-logstash
    (.venv) ➜  python ./Grafana-log/push_to_logstash_script.py --path ./Grafana-log --filename test.log --hostname Data_Transfer_Node_#1
    '''
    parser = argparse.ArgumentParser(description="Sending error logs through this script")
    parser.add_argument('-p', '--path', dest='path', default="/home/devuser", help='path for log')
    parser.add_argument('-f', '--filename', dest='filename', default="test1.log,test2.log", help='filename for log')
    parser.add_argument('-t', '--hostname', dest='hostname', default="hostname", help='hostname')
    # parser.add_argument('-l', '--logs', dest='logs', default="all", help='logs')
    parser.add_argument('-l', '--logs', dest='logs', default="ERROR", help='logs')
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
        ''' socket server for checking the status'''
        socket_th = Thread(target=server_listen)
        socket_th.daemon = True
        socket_th.start()
        T.append(socket_th)

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
        logging.error("# Interrupted..")
    
    except Exception as e:
        logging.error(e)
        
    except Exception as e:
        logging.error(e)
    