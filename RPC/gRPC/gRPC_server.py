from concurrent import futures
import logging
import grpc

import service_pb2
import service_pb2_grpc

from google.protobuf.struct_pb2 import Struct
from service_pb2 import MetricsStatusResponse
import sys
from concurrent import futures
import time
from flask import Flask


# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)


class Greeter(service_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):
        return service_pb2.HelloReply(message=f'Hello, {request.name}!')
    
    # 함수 2 구현
    def GetServerStatus(self, request, context):
        return service_pb2.StatusResponse(active=True)
    
    def GetMetricsStatus(self, request, context):
        logging.info(f"request : {request.env}")
        
        metadata_dict = {"token": "my-auth-token", "trace_id": "12345"}
        
        # metadata_struct = Struct()
        # metadata_struct.update(metadata_dict) # Update the Struct from a Python dict

        # request = MetricsStatusResponse(
        #     metrics=metadata_struct
        # )

        # return request

        return service_pb2.MetricsStatusResponse(metrics=metadata_dict)


def run_grpc_server():
    port = '50052'
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    server.add_insecure_port('[::]:' + port)
    server.start()
    try:
        while True:
            logging.info("Server started, listening on " + port)
            time.sleep(60) # One day in seconds
    except KeyboardInterrupt:
        server.stop(0)


def serve():
    port = '50052'
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    server.add_insecure_port('[::]:' + port)
    # server.add_insecure_port('[::]:50051')
    server.start()
    print("Server started, listening on " + port)
    server.wait_for_termination()


if __name__ == '__main__':
    # serve()
    
    # Start gRPC server in a separate thread/process for local testing
    # Note: For production, manage concurrency carefully
    import threading
    grpc_thread = threading.Thread(target=run_grpc_server)
    grpc_thread.daemon = True # Allows the main program to exit
    grpc_thread.start()

    # Run Flask app (this will block the main thread)
    app = Flask(__name__)
    @app.route('/')
    def index():
        return "Flask app is running alongside gRPC server!"
    app.run(host="0.0.0.0", port=8000)