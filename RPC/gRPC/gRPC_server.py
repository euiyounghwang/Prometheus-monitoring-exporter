from concurrent import futures
import logging
import grpc

import service_pb2
import service_pb2_grpc

from google.protobuf.struct_pb2 import Struct
from service_pb2 import MetricsStatusResponse
import sys


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
    serve()