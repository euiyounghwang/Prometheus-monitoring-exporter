

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter

import time
import argparse
import logging
import sys
import random
import json

# 로깅 설정
# logging.basicConfig(
#     level=logging.INFO,
#     format='[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s',
#     handlers=[
#         logging.StreamHandler(sys.stdout)
#     ]
# )

# logging.basicConfig(
#     format='%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
#     datefmt='%Y-%m-%dT%H:%M:%S',
#     level=logging.INFO
# )

# ''' including path and funtions of code for logging'''
# logging.basicConfig(
#     # format='%(asctime)s,%(msecs)d %(levelname)-8s [%(pathname)s:%(lineno)d in ' \
#     #        'function %(funcName)s] %(message)s',
#     format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s]' \
#            ' [%(funcName)s] %(message)s',
#     datefmt='%Y-%m-%d:%H:%M:%S',
#     level=logging.INFO
# )


class opentelemetry_client:
    
    def __init__(self, otel_host):

        logging.basicConfig(
            # format='%(asctime)s,%(msecs)d %(levelname)-8s [%(pathname)s:%(lineno)d in ' \
            #        'function %(funcName)s] %(message)s',
            format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s]' \
                ' [%(funcName)s] %(message)s',
            datefmt='%Y-%m-%d:%H:%M:%S',
            level=logging.INFO
        )

        self.otel_host = otel_host

        self.resource = Resource.create(
            attributes={
                "service.name": "my-python-app",
                "service.namespace": "production",
            }
        )

    
    def push_trace_metric_via_grpc(self):
        ''' Here is an example of how to configure the OTLP gRPC exporter for traces in Python '''
        logging.info(f"otel_host : {self.otel_host}")
        
        # Set up the tracer provider
        provider = TracerProvider(resource=self.resource)
        trace.set_tracer_provider(provider)

        # Configure the OTLP gRPC exporter
        # By default, it sends to localhost:4317, the standard OTLP gRPC port
        # otlp_exporter = OTLPSpanExporter()
        otlp_exporter = OTLPSpanExporter(endpoint="{}:4317".format(self.otel_host), insecure=True)

        # Register the exporter with the tracer provider
        provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

        # Get a tracer and create a span
        tracer = trace.get_tracer(__name__)

        with tracer.start_as_current_span("my_span"):
            logging.info("Doing some work in the span...")
            time.sleep(1)


    def push_prometheus_via_grpc(self):
        ''' Push a metric to the otel server via gRPC'''
        logging.info(f"otel_host : {self.otel_host}")

        try:
            # 1. OTLP 엑스포터 설정

            # Prometheus 직접 전송 시 엔드포인트: http://<prometheus-host>:9090/api/v1/otlp/v1/metrics

            '''
            # Configure the OTLP exporter
            # By default, OTLP uses gRPC on port 4317 or HTTP on port 4318
            # The endpoint parameter specifies the collector URL
            '''
            exporter = OTLPMetricExporter(endpoint="http://{}:4318/v1/metrics".format(self.otel_host))
            
            # 2. MetricReader 및 MeterProvider 설정
            # Configure the Metric Reader
            # This reader will collect and export metrics every 60 seconds (default interval)
            reader = PeriodicExportingMetricReader(exporter, export_interval_millis=5000)
            provider = MeterProvider(metric_readers=[reader])
            metrics.set_meter_provider(provider)

            # 3. 메트릭 생성 및 기록
            meter = metrics.get_meter("example.meter")
            # counter = meter.create_counter(
            #     name="python_request_total",
            #     description="Total number of requests",
            #     unit="1"
            # )

            # Create a synchronous gauge
            '''
            # HELP background_noise_level_dB The background noise level
            # TYPE background_noise_level_dB gauge
            background_noise_level_dB{environment="staging",from="python",job="unknown_service",method="gRPC",otel_scope_name="example.meter",otel_scope_schema_url="",otel_scope_version="",room="server_room"} 697
            '''
            background_noise_gauge = meter.create_gauge(
                name="background_noise_level",
                unit="dB",
                description="The background noise level",
            )

            # 메트릭 값 증가시키기
            # logging.info("Sending metrics to OTLP endpoint...")

            # Set the value directly
            # counter.add(1, {"environment": "staging", "from" : "python", "method": "GET"})
            # background_noise_gauge.set(75, attributes={"room": "server_room"})
            
            # while True:
            #     rand_num = random.randint(1, 1000)
            #     # counter.add(rand_num, {"environment": "staging", "method": "GET"})
            #     background_noise_gauge.set(rand_num, attributes={"room": "server_room", "environment": "staging", "from" : "python", "method": "gRPC"})
            #     logging.info("Sending metrics [{}] to OTLP endpoint.. ".format(rand_num))
            #     time.sleep(30)

            rand_num = random.randint(1, 1000)
            background_noise_gauge.set(rand_num, attributes={"room": "server_room", "environment": "staging", "from" : "python", "method": "gRPC"})

            return {
                    "func" : sys._getframe().f_code.co_name,
                    "status" : "Success"
                }
        
        except Exception as e:
            logging.error(e)
            return {
                    "func" : sys._getframe().f_code.co_name,
                    "status" : "Failed"
                }



if __name__ == '__main__':
    ''' docker run -p 4317:4317 -p 4318:4318 -v /path/to/your/config.yaml:/etc/otelcol/config.yaml otel/opentelemetry-collector:latest '''
    ''' 
    # HTTP 사용 시
    pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp-proto-http

    # gRPC 사용 시
    pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp-proto-grpc
    '''
    ''' pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp-proto-grpc opentelemetry-exporter-otlp-proto-http --trusted-host pypi.org --trusted-host files.pythonhosted.org'''
    '''  pip install "urllib3<2" when occuring the issue for OpenSSL'''
    
    # Ensure your OpenTelemetry Collector is running and configured to receive OTLP gRPC metrics. The default endpoint for gRPC reception is 0.0.0.0:4317.

    parser = argparse.ArgumentParser(description="Running this service allows us to send and expose the metrics using this script with otel gRPC")
    parser.add_argument('-otel_host', '--otel_host', dest='otel_host', default="localhost", help='otel_host')
    args = parser.parse_args()
    
        
    if args.otel_host:
        otel_host = args.otel_host

    ''' trace'''
    opentelemetry_client(otel_host).push_trace_metric_via_grpc()

    ''' metrics '''
    ack = opentelemetry_client(otel_host).push_prometheus_via_grpc()
    logging.info(json.dumps(ack, indent=2))