
import logging
import os
import sys
import time
import datetime
import argparse
import threading

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


if __name__ == "__main__":

    ''' sudo find /apps/var/spark/logs/*log* -mtime +0 -exec rm {} \; '''
    ''' sudo find /apps/kafka_2.11-0.11.0.0/logs -name '*log*' -type f -mtime +0 -exec rm -f {} \; '''
    ''' adm account: cd /apps/kafka/latest/ -> sudo chmod 775 -R ./logs/'''
    ''' python ./purge_script.py --interval 60 --delete_interval 2'''
    parser = argparse.ArgumentParser(description="Script that might allow us to use it as an application of purge scheduler")
    parser.add_argument('--interval', dest='interval', default=10, help='interval')
    parser.add_argument('--delete_interval', dest='delete_interval', default=7, help='delete-interval')
    args = parser.parse_args()

    if args.interval:
        interval = int(args.interval)

    if args.delete_interval:
        delete_interval = int(args.delete_interval)
     

    ''' Thread list'''
    T = []
    
    try:
        ''' In Python 2.7, the threading module is used to work with threads, which allow for concurrent execution of multiple parts of a program within a single process. '''
        # Create two threads
        thread1 = threading.Thread(target=purge_old_logs, args=("/apps/var/spark/logs", interval, delete_interval))
        thread2 = threading.Thread(target=purge_old_logs, args=("/apps/kafka/latest/logs", interval, delete_interval))

        ''' a daemon thread is a thread that runs in the background and is terminated automatically when the main program exits.'''
        thread1.daemon = True
        thread1.start()

        thread2.daemon = True
        thread2.start()

        T.append(thread1)
        T.append(thread2)

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