
# -*- coding: utf-8 -*-
import sys
import os
import json

import argparse
from dotenv import load_dotenv
import os
from datetime import datetime
from threading import Thread
import requests
import pytz

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
# from opentelemetry.sdk.trace.export import BatchExportSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor

import logging
import warnings
import datetime, time
warnings.filterwarnings("ignore")

load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# 1. Tracer Provider 및 Exporter 설정
provider = TracerProvider()
# Jaeger Exporter 설정 (Jaeger 서버 주소: http://localhost:14250 또는 UDP 포트)
exporter = JaegerExporter(
    agent_host_name='localhost', # Jaeger Agent 주소 (docker-compose 시 변경 가능)
    agent_port=6831, # UDP 포트
    # agent_port=4317, # UDP 포트
    # 또는 OTLP로 보내려면 (collector 사용 시):
    # collector_endpoint='http://localhost:4318/v1/traces'
)
# Configure the OTLP Exporter
# By default, OTLPSpanExporter sends via gRPC to localhost:4317
otlp_exporter = OTLPSpanExporter(endpoint="localhost:4317", insecure=True) #
# provider.add_span_processor(BatchSpanProcessor(exporter))
provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
trace.set_tracer_provider(provider)

# 2. Tracer 가져오기
tracer = trace.get_tracer("my-python-app")

# 3. Span 생성 및 추적
def say_hello(name):
    # 'say-hello' 이름의 span 시작
    with tracer.start_as_current_span("say-hello") as span:
        print(f"Hello, {name}!")
        # Span에 속성(Attributes) 추가
        span.set_attribute("name", name)
        # 다른 작업...
        time.sleep(0.1) # 작업 시뮬레이션


def work() -> None:
    """
    Docstring for work
    """
    while True:
        try:
            logging.info("** Jeager Tracing..**")

        # except (KeyboardInterrupt, SystemExit) as e:           
        except Exception as e:
            logging.error(f"work func : {e}")
            pass

        time.sleep(60)
   


if __name__ == '__main__':
    """
    
    - Running this service to track the log on interconnected software components called microservices. 
        - docker run -d --name jaeger -p 16686:16686 -p 14268:14268 jaegertracing/all-in-one:latest
    - Reference : ./docker-compose.yaml or ./jaeger-msa-docker-compose.yaml
    - pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-jaeger opentelemetry-exporter-otlp
    python ./jaeger-trace-script.py
    
    """
    parser = argparse.ArgumentParser(description="Running this service to check the status of tools and send alerts using this script")
    # parser.add_argument('-port', '--port', dest='port', default=9999, help='port')
    args = parser.parse_args()
    
    global gloabal_default_timezone

        
    # if args.port:
    #     _port = args.port

    gloabal_default_timezone = pytz.timezone('US/Eastern')

    # --
    # Only One process we can use due to 'Global Interpreter Lock'
    # 'Multiprocessing' is that we can use for running with multiple process
    # --
    try:
        """
        T = []
        th1 = Thread(target=work, args=())
        th1.daemon = True
        th1.start()
        T.append(th1)

        for t in T:
            while t.is_alive():
                t.join(0.5)
        """
        say_hello("Jaeger")
        say_hello("OpenTelemetry")
   
    except Exception as e:
        logging.error(e)