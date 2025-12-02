
import logging
import os
import sys
import time
import datetime
import argparse
import threading
import http.server, socketserver
import socket
import sys

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


def purge_old_logs(folder_path, interval, delete_interval):
    ''' Delete old logs'''
    
    def delete_old_files(folder_path, days_old):
        now = time.time()
        
        for filename in os.listdir(folder_path):
            # print(filename)
            if "log" in filename:
                file_path = os.path.join(folder_path, filename)
                
                file_mtime = os.path.getmtime(file_path) 
                
                file_age_seconds = now - file_mtime
                
                file_age_days = file_age_seconds / (60 * 60 * 24)
                
                if file_age_days > days_old:
                    logging.info("Will be deleted this file {}".format(file_path))
                    os.remove(file_path)
                
    
    while True:
        logging.info('purge_old_logs.. ({}), delete_interval : {}'.format(folder_path, delete_interval))

        delete_old_files(folder_path, delete_interval) 

        time.sleep(interval)


def Http_Listen(http_port):
    ''' python3 HTTP server '''
    PORT = http_port

    Handler = http.server.SimpleHTTPRequestHandler

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Serving at port {PORT}")
        # Start the server and keep it running until you stop the script
        httpd.serve_forever()


def Socket_Listen(socket_port):
    ''' A server has a bind() method which binds it to a specific IP and port so that it can listen to incoming requests on that IP and port. '''
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # With the help of bind() function 
        # binding host and port
        soc.bind(("0.0.0.0", socket_port))
        
    except socket.error as message:
        
        # if any error occurs then with the 
        # help of sys.exit() exit from the program
        logging.error('Bind failed. Error Code : ' + str(message[0]) + ' Message ' + message[1])
        sys.exit()
        
    # print if Socket binding operation completed    
    print('Socket binding operation completed')
    
    # With the help of listening () function
    # starts listening
    soc.listen(9)
    
    conn, address = soc.accept()
    # print the address of connection
    logging.info('Connected with ' + address[0] + ':' + str(address[1]))


if __name__ == "__main__":

    ''' sudo find /apps/var/spark/logs/*log* -mtime +0 -exec rm {} \; '''
    ''' sudo find /apps/kafka_2.11-0.11.0.0/logs -name '*log*' -type f -mtime +0 -exec rm -f {} \; '''
    ''' adm account: cd /apps/kafka/latest/ -> sudo chmod 777 ./logs/'''
    ''' python ./purge_script.py --server_port 8001 --spark_log /apps/var/spark/logs --kafka_log /apps/kafka/latest/logs --interval 60 --delete_interval 2'''
    parser = argparse.ArgumentParser(description="Script that might allow us to use it as an application of purge scheduler")
    parser.add_argument('--server_port', dest='server_port', default="8001", help='server_port')
    parser.add_argument('--spark_log', dest='spark_log', default="/apps/var/spark/logs", help='spark_log')
    parser.add_argument('--kafka_log', dest='kafka_log', default="/apps/kafka/latest/logs", help='kafka_log')
    parser.add_argument('--interval', dest='interval', default=10, help='interval')
    parser.add_argument('--delete_interval', dest='delete_interval', default=7, help='delete-interval')
    args = parser.parse_args()

    if args.server_port:
        server_port = int(args.server_port)

    if args.spark_log:
        spark_log = args.spark_log

    if args.kafka_log:
        kafka_log = args.kafka_log

    if args.interval:
        interval = int(args.interval)

    if args.delete_interval:
        delete_interval = int(args.delete_interval)
     
    logging.info("spark_log : {}, kafka_log : {}".format(spark_log, kafka_log))
    
    ''' Thread list'''
    T = []
    
    try:
        ''' In Python 2.7, the threading module is used to work with threads, which allow for concurrent execution of multiple parts of a program within a single process. '''
        # Create two threads
        thread1 = threading.Thread(target=purge_old_logs, args=(spark_log, interval, delete_interval))
        thread2 = threading.Thread(target=purge_old_logs, args=(kafka_log, interval, delete_interval))

        # http_th = threading.Thread(target=Http_Listen, args=(server_port,))
        http_th = threading.Thread(target=Socket_Listen, args=(server_port,))
     
        ''' a daemon thread is a thread that runs in the background and is terminated automatically when the main program exits.'''
        thread1.daemon = True
        thread1.start()

        thread2.daemon = True
        thread2.start()

        http_th.daemon = True
        http_th.start()

        T.append(thread1)
        T.append(thread2)

        T.append(http_th)

        """
        # Start the threads
        thread1.start()
        thread2.start()

        # Wait for both threads to complete
        thread1.join()
        thread2.join()
        """

         # wait for all threads to terminate
        for t in T:
            while t.is_alive():
                t.join(0.5)
        
    except Exception as e:
        logging.error(e)
        logging.info("# Interrupted..")