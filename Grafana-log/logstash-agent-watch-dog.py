# -*- coding: utf-8 -*-
import socket
import json
import subprocess
import logging
import argparse


logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

SERVICE_NAME='python-logging-to-logstash-sparklogs'


''' get ProcessID'''
def get_command_output(cmd):
    ''' Get PID with process name'''
    try:
        call = subprocess.check_output("{}".format(cmd), shell=True)
        response = call.decode("utf-8")
        # logging.info(response)
        return response
    except subprocess.CalledProcessError:
        pass


def work(cmd):
    
    hostname = socket.gethostname()
    try:
        pid = get_command_output("ps ax | grep -i '/push_to_logstash_script.py' | grep -v grep | awk '{print $1}'")
        if pid:
            logging.info("[{}] {} is Running as PID: {}".format(hostname, SERVICE_NAME, str(pid).replace('\n','')))
        else:
            logging.error("[{}] {} was not Running".format(hostname, SERVICE_NAME, pid))
            get_command_output(cmd)

    except Exception as e:
            logging.info("# Interrupted..")
        

if __name__ == "__main__":
    '''
    python ./logstash-agent-watch-dog.py --cmd /home/devuser/monitoring/log_to_logstash/logstash-agent-restart.sh
    #--
    #** Script for Log Agent Restart **
    */5 * * * * python /home/devuser/monitoring/log_to_logstash/logstash-agent-watch-dog.py --cmd /home/devuser/monitoring/log_to_logstash/logstash-agent-restart.sh
    #** ---------------------- **

    '''
    parser = argparse.ArgumentParser(description="Checking this script if it's running")
    parser.add_argument('-c', '--cmd', dest='cmd', default="/home/devuser/monitoring/log_to_logstash/logstash-agent-restart.sh", help='logs script')
    args = parser.parse_args()
    
    if args.cmd:
        cmd = args.cmd

    try:
        work(cmd)
    except Exception as e:
        logging.error(e)
