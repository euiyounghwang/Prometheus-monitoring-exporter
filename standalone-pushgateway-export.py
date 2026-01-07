from prometheus_client import CollectorRegistry, Gauge, push_to_gateway, delete_from_gateway
import random
import time
import datetime, time
import argparse
from threading import Thread
import logging
import json
from dotenv import load_dotenv
import logging
import warnings
import sys
import threading
warnings.filterwarnings("ignore")

# Create a global lock object
lock = threading.Lock()


''' pip install python-dotenv'''
load_dotenv() # will search for .env file in local folder and load variables 


# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    # format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    format='[%(asctime)s] [%(levelname)s] [%(module)s] [%(funcName)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)


# A registry is needed to manage the metrics for this specific push operation
registry = CollectorRegistry()

# Define a Gauge metric, associating it with the registry
# The metric name is 'my_batch_job_duration_seconds'
# The description explains what it measures
g = Gauge(
    'my_batch_job_duration_seconds',
    'Duration of the batch job in seconds',
    registry=registry
)

def work(pushgateway_url):
    ''' 
    main logic (Check : http://localhost:9091/metrics)
    # TYPE my_batch_job_duration_seconds gauge
    my_batch_job_duration_seconds{instance="",job="test_job"} 2.009629249572754
    
    params: pushgateway_url
    '''

    # while True:
    #     try:
            
    #     except (KeyboardInterrupt, SystemExit):
    #         logging.info("#Interrupted..")
    #     except Exception as e:
    #         logging.error(e)
        
    #     time.sleep(interval)

    # Simulate a batch job process
    try:
        print("Simulating a batch job...")
        job_start_time = time.time()
        # Your batch job logic goes here
        time.sleep(random.randint(1, 5)) 
        job_end_time = time.time()
        duration = job_end_time - job_start_time

        # Example 1: Delete all metrics for a specific job and instance
        # This matches metrics pushed with the exact grouping key: {job="my_batch_job", instance="instance_1"}
        # delete_from_gateway('http://localhost:9091', job='test_job', grouping_key={'instance': 'instance_1'})

        # Example 2: Delete all metrics associated only with a specific job name, regardless of instance
        # This matches metrics pushed with the grouping key: {job="my_other_job"}
        # delete_from_gateway(pushgateway_url, job='test_job')

        # Set the gauge value
        g.set(duration)
        print(f"Job finished in {duration:.2f} seconds.")

        # Push the metrics to the Pushgateway
        # Replace 'localhost:9091' with your Pushgateway address
        # The 'job' label is essential for grouping metrics in the Pushgateway
        push_to_gateway(
            pushgateway_url,
            job='test_job',
            registry=registry
        )
        print("Metrics pushed to Pushgateway.")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == '__main__':
    '''
    pip install prometheus-client
    python standalone-pushgateway-export.py
    '''
    parser = argparse.ArgumentParser(description="Script that might allow us to push metrics into pushgateway tool")
    parser.add_argument('--pushgateway_url', dest='pushgateway_url', default="localhost:9091", help='pushgateway_url')
    args = parser.parse_args()
    
    if args.pushgateway_url:
        pushgateway_url = args.pushgateway_url

    logging.info("Standalone Pushgateway Started..!")
    
    try:
        T = []
        ''' *** '''

        main_th = Thread(target=work, args=(pushgateway_url, ))
        main_th.daemon = True
        main_th.start()
        T.append(main_th)
            
        # wait for all threads to terminate
        for t in T:
            while t.is_alive():
                t.join(0.5)

    except (KeyboardInterrupt, SystemExit):
        logging.info("# Interrupted..")

    finally:
        logging.info("Standalone Prometheus Exporter Server exited..!")
    
    