# -*- coding: utf-8 -*-
import time
import os
from datetime import datetime
from threading import Thread
import requests
import logging
import socket
import sys
import subprocess
import warnings
warnings.filterwarnings("ignore")

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)



''' get ProcessID'''
def get_command_output(cmd):
    ''' Get PID with process name'''
    try:
        call = subprocess.check_output("{}".format(cmd.decode()), shell=True)
        # call = subprocess.check_output("{}".format("ps ax | grep -i '/filebeat.yml' | grep -v grep | awk '{print $1}'"), shell=True)
        response = call.decode("utf-8")
        logging.info(response)
        return response
    except subprocess.CalledProcessError:
        pass


def server_listen():
    ''' Return Pid whether filebeat is running via socket library to ES Monitoring Application (Used filebeat for error log, not this script)'''
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

                if not data:
                    break

                """ reqeust this cmd (ps ax | grep -i '/filebeat.yml' | grep -v grep | awk '{print $1}') from ES Monitoring Application using socket library """
                ''' send output'''
                pid = get_command_output(data)
                if pid:
                    connection.send(pid.encode())
                

        except Exception as e:
            logging.error("# Interrupted..{}".format(e))

        finally:
            connection.close()


if __name__ == '__main__':
    '''
    [install pip for python2.7] python ./get-pip.py ➜ [install the library] pip install python-logstash
    (.venv) ➜  python ./Grafana-log/push_to_logstash_script.py --path ./Grafana-log --filename test.log --hostname Data_Transfer_Node_#1
    '''
    
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
    