from concurrent import futures
import logging
import grpc

import service_pb2
import service_pb2_grpc

from google.protobuf.json_format import MessageToJson, Parse
import json
import os, sys
import argparse
import dotenv

''' pip install python-dotenv'''
# load_dotenv() # will search for .env file in local folder and load variables 
# Reload the variables from your .env file, overriding existing ones
dotenv.load_dotenv(".env", override=True)

''' export PYTHONDONTWRITEBYTECODE=1 '''
sys.dont_write_bytecode = True


# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

def run(gRPC_server_host, param_env):
    print("Will try to greet world ...")
    
    ''' Local Test'''
    # with grpc.insecure_channel("{}:50052".format(gRPC_server_host)) as channel:
    ''' ES Monitoring Test '''
    with grpc.insecure_channel("{}:50001".format(gRPC_server_host)) as channel:
        stub = service_pb2_grpc.GreeterStub(channel)

        '''
        response = stub.SayHello(service_pb2.HelloRequest(name='azamman'))
        print("Greeter client received: " + response.message)

        # 함수 2 호출
        response2 = stub.GetServerStatus(service_pb2.StatusRequest(id='123'))
        print("서버 상태:", "활성" if response2.active else "비활성")
        '''

        '''
        # 1. Convert a Python dictionary (JSON) to a Protobuf message before sending
        json_input = {"name": "Test User", "id": 123}
        request_message = Parse(json.dumps(json_input), pb2.YourRequestMessage())
        response = stub.YourMethod(request_message)
        '''
        
        response_dict = stub.GetMetricsStatus(service_pb2.MetricsStatusRequest(env=param_env))
        # print(f"response_dict : {response_dict}, type {type(response_dict)}")

        ''' MessageToJson(message): Serializes a Protobuf message object to a JSON formatted string.'''
        Jsons = MessageToJson(response_dict)
        Jsons_dict = json.loads(Jsons).get('metrics')
        # print(f"MessageToJson : {Jsons}, type : {type(Jsons_dict)}, key : {Jsons_dict.get('token')}")
        logging.info(json.dumps(Jsons_dict, indent=2))


if __name__ == '__main__':
    '''
    gRPC Client
    python ./RPC/gRPC/gRPC_client.py --gRPC_server_host localhost
    ./gRPC_client.sh start
    '''
    parser = argparse.ArgumentParser(description="Script that might allow us to get the response fromm the gRPC server")
    parser.add_argument('--gRPC_server_host', dest='gRPC_server_host', default="localhost", help='gRPC_server_host')
    parser.add_argument('--env', dest='env', default="Dev", help='env')
    args = parser.parse_args()

    if args.gRPC_server_host:
        gRPC_server_host = args.gRPC_server_host
        
    if args.env:
        env = args.env

    try:
        run(gRPC_server_host, env)

    except Exception as e:
        logging.error(e)