
import sys
import socket
import json
import argparse
import logging
import logstash
from datetime import datetime


logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)



class SOCKET_JSON:
    """
    UDP SOCKET with Logstsh
    """

    socket_logstash_dict = {}

    def socket_json_push(self, key, value):
         if key not in self.socket_logstash_dict.keys():
            self.socket_logstash_dict[key] = value
            # self.socket_logstash_dict[key].append(value)
            # del (self.socket_logstash_dict[key][0])


    def get_socket_json_pop(self):
        return self.socket_logstash_dict


class TCP_SOCKET:
    """
    TCP SOCKET with Logstsh
    """
    def __init__(self, ip, port):
        self.target_server_ip = ip
        self.socket_port = port


    def socket_logstash_handler(self, message):
        try:
            soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            soc.connect((self.target_server_ip, int(self.socket_port)))
            msg = {'@message': 'python test message', '@tags': ['python', 'test']}
            soc.sendall(json.dumps(msg))
            soc.send("\n")
            soc.close()
            logging.info('Socket Closed')
        except Exception as e:
            logging.error(e)



class UDP_SOCKET:
    """
    UDP SOCKET with Logstsh
    """

    def __init__(self, ip, port):
        self.target_server_ip = ip
        self.socket_port = port

    def socket_logstash_handler(self, message):
        try:
            soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            soc.connect((self.target_server_ip, self.socket_port))
            soc.send(json.dumps(message, ensure_ascii=False).encode("utf8")) # we must encode the string to bytes\
            soc.close()
            logging.info('Socket Closed')
        except Exception as e:
            logging.error(e)


if __name__ == '__main__':

    '''
    python ./ELK-config/logstash/logstash-socket.py --host localhost
    '''
    parser = argparse.ArgumentParser(description="Send message to logstash server based on socket using this script")
    parser.add_argument('--host', dest='host', default="localhost", help='logstash host')
    args = parser.parse_args()
    
    if args.host:
        host = args.host

    SOCKET_SERVER_IP = host
    # SOCEKT_PORT = 5959
    SOCEKT_PORT = 5950

    log_level = "ERROR"
    
    # Monitoring
    extra = {
        'log_status': log_level, 
        'log_filename': 'test.log', 
        'host': 'localhost', 
        'host_name': 'Data_Transfer_Node_#1', 
        'env': 'Dev', 
        'message' : '224/10/16 15:33:30 INFO myLogger: 2024-10-16 15:33:30.907 Elastic UPDATE END ',
        # 'event':{'original': '2018-02-01 09:14:11,550 WARN  - [[ACTIVE] ExecuteThread: {}'.format(log_level)}
    }
    ''' {'env': 'Dev', 'log_level': 'ERROR', 'message': 'Script to Logstash - 2024-10-16 11:58:46'} -> 
        \{\'env\'\: \'%{GREEDYDATA:ENV}\', 'log_level'\: \'%{GREEDYDATA:LOG_LEVEl}\', 'message'\: \'%{GREEDYDATA:MESSAGE}\'
    
        24/10/16 15:33:30 INFO myLogger: 2024-10-16 15:33:30.907 Elastic UPDATE END for queueid: 1065
        %{WORD:RM}\/%{WORD:RM}\/%{WORD:RM} %{WORD:RM}\:%{WORD:RM}:%{WORD:RM} %{WORD:LOG_LEVEL} %{WORD:LOG_NAME}\: %{TIMESTAMP_ISO8601:LOGGER_DATE} %{GREEDYDATA:MESSAGE}

        {'log_status': 'INFO', 'log_filename': 'test.log', 'host': 'localhost', 'host_name': 'Data_Transfer_Node_#1', 'env': 'Dev', 'message': '24/10/16 15:53:30 INFO TaskSetManager: Starting task 2.0 in stage)\\n'}
        \{\'log_status\'\: \'%{GREEDYDATA:LOG_LEVEL}\', 'log_filename'\: \'%{GREEDYDATA:LOG_FILENAME}\', 'host'\: \'%{GREEDYDATA:SHORT_HOST}\', 'host_name'\: \'%{GREEDYDATA:NODE_NAME}\', 'env'\: \'%{GREEDYDATA:ENV}\', 'message'\: \'%{GREEDYDATA:MESSAGE}\'
    
    '''

    try:
        SOC = UDP_SOCKET(SOCKET_SERVER_IP, 5959)
        # SOC = TCP_SOCKET(SOCKET_SERVER_IP, 5950)
        for _ in range(4):
            SOC.socket_logstash_handler(extra)
    except Exception as e:
        print(e)
    
    ''' python ./get-pip.py -> pip install python-logstash '''
    ''' https://github.com/vklochan/python-logstash/tree/master '''

    """
    test_logger = logging.getLogger('python-logstash-logger')
    test_logger.setLevel(logging.INFO)
    test_logger.addHandler(logstash.LogstashHandler(host, SOCEKT_PORT, version=1))
    test_logger.addHandler(logstash.TCPLogstashHandler(host, SOCEKT_PORT, version=1))
    # test_logger.addHandler(logstash.UDPLogstashHandler(host, SOCEKT_PORT, version=1))

    # test_logger.error('python-logstash: test logstash error message.')
    # test_logger.info('python-logstash: test logstash info message.')
    # test_logger.warning('python-logstash: test logstash warning message.')

    # test_logger.info('python-logstash: test extra fields', extra=extra)
    test_logger.info(extra)
    """