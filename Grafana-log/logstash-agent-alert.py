# -*- coding: utf-8 -*-
import argparse
import os
from datetime import datetime, timedelta
from threading import Thread
import logging
import json
from elasticsearch import Elasticsearch, exceptions
import warnings
warnings.filterwarnings("ignore")

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)



def get_search(source_host):
    ''' get search results from ES v.5'''   
    def get_headers():
        ''' Elasticsearch Header '''
        return {
            'Content-type': 'application/json', 
            'Connection': 'close'
        }
    
    try:
        """
        obj = datetime(2015, 4, 21, 20, 0, 0)
        logging.info(obj.isoformat())
        """
        # logging.info(datetime.now().isoformat())
        ''' "@timestamp": "2024-11-13T17:46:17.368Z" --> "timestamp": "2024-11-13 12:46:16" '''
        timestamp_now = datetime.now() + timedelta(hours=2)
        logging.info(datetime.now())
        logging.info(timestamp_now.isoformat())
        es_client = Elasticsearch(hosts=source_host, headers=get_headers(), verify_certs=False, max_retries=0, timeout=5)
        
        es_query = {
            "size": 0, 
            "query": {
                "bool": {
                    "must": [
                        {
                            "range": {
                                "@timestamp": {
                                    "gte": timestamp_now.isoformat()
                                }
                            }
                        }
                    ]
                }
            },
            "sort": [
                {
                "@timestamp": {
                    "order": "desc"
                }
                }
            ],
            "aggs": {
                "spark_log": {
                "terms": {
                    "field": "fields.env.keyword",
                    "size": 100
                }
                }
            }
        }

        logging.info(json.dumps(es_query, indent=2))      
        return es_client.search(index= "logstash-logger-*", body=es_query,)
    
    except Exception as e:
        logging.error(e)
        return {}
        
    

def alert(env):
    '''' send alert '''
    logging.info(f"alert started : {env}")

    
def work(es_host):
    ''' Alert job for error logs'''
    ''' This script will be running with while clause'''
    try:
        logging.info(f"es_host : {es_host}")
        ''' get resutls with aggs'''
        results = get_search(es_host)
        # logging.info(json.dumps(results, indent=2))
        # aggs_buckets = results["aggregations"]["spark_log"]["buckets"]
        aggs_buckets = [ {"key" : "Dev", "doc_count": 10}]
        ''' if buckets are in the aggs result'''
        if aggs_buckets:
            logging.info(f"aggs_buckets : {json.dumps(aggs_buckets, indent=2)}")
            ''' send an alert'''
            for env in aggs_buckets:
                alert(env.get("key"))
        else:
            logging.info(f"aggs_buckets : {json.dumps([], indent=2)}")
    except Exception as e:
        logging.error(e)
        pass

    

if __name__ == '__main__':
    '''
    Sending alert whenever we got the error logs from the spark job via ES cluster with logstash-logger-* indexes
    (.venv) ➜  python ./Grafana-log/logstash-agent-alert.py --ts http://localhost:9200
    '''
    parser = argparse.ArgumentParser(description="Sending alert for error logs from spark jobs using this script")
    parser.add_argument('-t', '--ts', dest='ts', default="http://localhost:9200", help='host target')
    args = parser.parse_args()
    
    if args.ts:
        es_host = args.ts

    T = []
        
    # --
    # Only One process we can use due to 'Global Interpreter Lock'
    # 'Multiprocessing' is that we can use for running with multiple process
    # --
    try:
        ''' socket server for checking the status'''
        socket_th = Thread(target=work, args=(es_host, ))
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
    