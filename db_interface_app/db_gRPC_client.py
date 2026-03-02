import grpc
import service_pb2
import service_pb2_grpc
from google.protobuf.json_format import MessageToJson, Parse
import os
import dotenv

''' pip install python-dotenv'''
# load_dotenv() # will search for .env file in local folder and load variables 
# Reload the variables from your .env file, overriding existing ones
dotenv.load_dotenv(dotenv_path=f"{os.path.abspath(os.getcwd())}/.env", override=True)

def run():
    with grpc.insecure_channel(f"{os.getenv('HOST')}:8002") as channel:
        stub = service_pb2_grpc.DBInterfacerStub(channel)
        
        print(os.getenv("DB_URL"))
        print(os.getenv("SQL"))

        # 서버 스트리밍 호출
        responses = stub.GetMetricsStatus(service_pb2.DBSQLRequest(db_url=os.getenv("DB_URL"),sql=os.getenv("SQL")))
        Jsons = MessageToJson(responses)
        print(Jsons)
        # for response in responses:
        #     print(f"Received: {response}")

if __name__ == '__main__':
    ''' export PYTHONDONTWRITEBYTECODE=1 '''
    ''' gRPC client to recevie the recores from DB'''
    run()
