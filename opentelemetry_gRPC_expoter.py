

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

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Resource configuration (optional but recommended)
resource = Resource.create(
    attributes={
        "service.name": "my-python-app",
        "service.namespace": "production",
    }
)

def tracer_gRPC(otel_host):
    ''' Here is an example of how to configure the OTLP gRPC exporter for traces in Python '''
    logging.info(f"otel_host : {otel_host}")
    
    # Set up the tracer provider
    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)

    # Configure the OTLP gRPC exporter
    # By default, it sends to localhost:4317, the standard OTLP gRPC port
    # otlp_exporter = OTLPSpanExporter()
    otlp_exporter = OTLPSpanExporter(endpoint="{}:4317".format(otel_host), insecure=True)

    # Register the exporter with the tracer provider
    provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

    # Get a tracer and create a span
    tracer = trace.get_tracer(__name__)

    with tracer.start_as_current_span("my_span"):
        print("Doing some work in the span...")
        time.sleep(1)


def metrics_gRPC(otel_host):
    logging.info(f"otel_host : {otel_host}")
    # 1. OTLP 엑스포터 설정
    # Prometheus 직접 전송 시 엔드포인트: http://<prometheus-host>:9090/api/v1/otlp/v1/metrics
    exporter = OTLPMetricExporter(endpoint="http://{}:4318/v1/metrics".format(otel_host))

    # 2. MetricReader 및 MeterProvider 설정
    reader = PeriodicExportingMetricReader(exporter, export_interval_millis=5000)
    provider = MeterProvider(metric_readers=[reader])
    metrics.set_meter_provider(provider)

    # 3. 메트릭 생성 및 기록
    meter = metrics.get_meter("example.meter")
    counter = meter.create_counter(
        name="python_request_total",
        description="Total number of requests",
        unit="1"
    )

    # 메트릭 값 증가시키기
    print("Sending metrics to OTLP endpoint...")
    counter.add(1, {"environment": "staging", "from" : "python", "method": "GET"})
    
    """
    while True:
        counter.add(1, {"environment": "staging", "method": "GET"})
        time.sleep(1)
    """


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
    
    parser = argparse.ArgumentParser(description="Running this service allows us to check and delete old ES indices using this script")
    parser.add_argument('-otel_host', '--otel_host', dest='otel_host', default="localhost", help='otel_host')
    args = parser.parse_args()
    
        
    if args.otel_host:
        otel_host = args.otel_host

    ''' trace'''
    tracer_gRPC(otel_host)

    ''' metrics '''
    metrics_gRPC(otel_host)