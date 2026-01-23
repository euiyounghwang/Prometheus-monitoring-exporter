from concurrent import futures
import logging
import grpc

import service_pb2
import service_pb2_grpc

from google.protobuf.json_format import MessageToJson, Parse
import json
import sys

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

def run():
    print("Will try to greet world ...")
    
    with grpc.insecure_channel('localhost:50052') as channel:
        stub = service_pb2_grpc.GreeterStub(channel)

        response = stub.SayHello(service_pb2.HelloRequest(name='azamman'))
        print("Greeter client received: " + response.message)

        # 함수 2 호출
        response2 = stub.GetServerStatus(service_pb2.StatusRequest(id='123'))
        print("서버 상태:", "활성" if response2.active else "비활성")

        '''
        # 1. Convert a Python dictionary (JSON) to a Protobuf message before sending
        json_input = {"name": "Test User", "id": 123}
        request_message = Parse(json.dumps(json_input), pb2.YourRequestMessage())
        response = stub.YourMethod(request_message)
        '''
        
        response_dict = stub.GetMetricsStatus(service_pb2.MetricsStatusRequest(env='Dev'))
        # print(f"response_dict : {response_dict}, type {type(response_dict)}")

        ''' MessageToJson(message): Serializes a Protobuf message object to a JSON formatted string.'''
        Jsons = MessageToJson(response_dict)
        Jsons_dict = json.loads(Jsons).get('metrics')
        # print(f"MessageToJson : {Jsons}, type : {type(Jsons_dict)}, key : {Jsons_dict.get('token')}")
        logging.info(json.dumps(Jsons_dict, indent=2))


if __name__ == '__main__':
    run()