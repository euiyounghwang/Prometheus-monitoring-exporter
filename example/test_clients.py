from prometheus_client import start_http_server, Summary
from prometheus_client import Counter
import random
import time
 
 
# Create a metric to track time spent and requests made.
REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')
 
# Decorate function with metric.
@REQUEST_TIME.time()
def process_request(t):
    """A dummy function that takes some time."""
    time.sleep(t)
 
 
if __name__ == '__main__':
    # Start up the server to expose the metrics.
    start_http_server(8000)
 
    c = Counter('sejong_packet_bytes', 'http request failure', ['src_ip', 'dst_ip', 'src_port', 'dst_port'])
    # Generate some requests.
    print("Server started..")
    while True:
        process_request(random.random()/10)
        c.labels(src_ip='10.1.4.11', dst_ip='192.168.5.22', src_port='11111', dst_port='').inc(1322)
        c.labels(src_ip='10.1.8.33', dst_ip='192.168.9.66', src_port='12345', dst_port='23456').inc(1500)
        c.labels(src_ip='172.16.8.33', dst_ip='192.168.9.66', src_port='12345', dst_port='23456').inc(1500)
        c.labels(src_ip='172.17.7.33', dst_ip='192.168.33.66', src_port='80808', dst_port='90909').inc(1500)
