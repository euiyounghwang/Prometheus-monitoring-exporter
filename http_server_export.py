
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import os
from socketserver import BaseServer
import requests
import json
import logging
from json import dumps
import socket
from subprocess import check_output
import psutil
import subprocess
import re


logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


class ProcessHandler():

    def __init__(self) -> None:
        pass

    def isProcessRunning(self, name):
        ''' Get PID with process name'''
        try:
            call = subprocess.check_output("pgrep -f '{}'".format(name), shell=True)
            logging.info("Process IDs - {}".format(call.decode("utf-8")))
            return True
        except subprocess.CalledProcessError:
            return False


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    ''' HTTP Listeners'''

    def _send_cors_headers(self):
        ''' set headers requried for CORS'''
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "x-api-key, Content-Type")


    def send_dict_response(self, d):
        ''' send a dict as Json back to the client '''
        self.wfile.write(bytes(dumps(d), "utf8"))


    def get_Process_Id(self):
        process_name = "/logstash-"
        process_handler = ProcessHandler()
        logging.info("Prcess - {}".format(process_handler.isProcessRunning(process_name)))
        if process_handler.isProcessRunning(process_name):
            return 1
        return 0


    def do_GET(self):
        ''' http://localhost:9999/health?kafka_url=localhost:29092,localhost:39092,localhost:49092&es_url=localhost:9200,localhost:9201,localhost:9203'''

        response_dict = {}
        logging.info(self.path)
        
        pathList = self.path.split("/")[1].split("?")
        if str(pathList[0]).startswith('health'):
            logging.info("pathList : {}".format(pathList))

            #-- split each metrics
            urls_metrics = str(pathList[1]).split('&')
            logging.info("urls_metrics : {}".format(urls_metrics))

            for urls_metric in urls_metrics:
                urls = str(urls_metric).split('=')

                logging.info("url key: {}".format(urls[0]))
                logging.info("url value: {}".format(urls[1]))

                url_key = urls[0]
                url_value = urls[1] 

                response_dict.update({url_key : ""})
                response_sub_dict = {}

                totalcount = 0
                # logging.info("url_key ", url_key)
                # if urls[1]:
                if url_key == "logstash_url":
                    response_dict.update({url_key : self.get_Process_Id()})
                else:
                    url_lists = urls[1].split(",")
                    logging.info("url_lists : {}".format(url_lists))
                    for each_url in url_lists:
                        each_urls = each_url.split(":")
                        logging.info("each_brokers : {}".format(each_urls))
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        result = sock.connect_ex((each_urls[0],int(each_urls[1])))
                        if result == 0:
                            # print("Port is open")
                            totalcount +=1
                            response_sub_dict.update({each_urls[0] + ":" + each_urls[1] : "OK"})
                            response_sub_dict.update({"GREEN_CNT" : totalcount})
                        else:
                            # print("Port is not open")
                            response_sub_dict.update({each_urls[0] + ":" + each_urls[1] : "FAIL"})
                            response_sub_dict.update({"GREEN_CNT" : totalcount})
                        sock.close()

                    response_dict.update({url_key : response_sub_dict})

        logging.info(response_dict)
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self._send_cors_headers()
        self.end_headers()

        # self.wfile.write('<h1>hello</h1>'.encode('utf-8'))
        # self.send_dict_response({"status" : "OK"})
        self.send_dict_response(response_dict)
        

if __name__ == '__main__':
    ''' ./es-service-all-server-export-run.sh status/start/stop '''
    try:
        port = 9999
        # httpd = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
        # logging.info(f'Http Server running on port:{port}')
        # httpd.serve_forever()
        server = ThreadingHTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
        logging.info('Http Server running on port:{}'.format(port))
        server.serve_forever()
    except KeyboardInterrupt:
        logging.info("#Interrupted..")
        # httpd.shutdown()    
        