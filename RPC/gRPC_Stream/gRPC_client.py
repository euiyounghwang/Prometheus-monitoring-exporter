import grpc
import service_pb2
import service_pb2_grpc

def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = service_pb2_grpc.DataServiceStub(channel)
        
        # 서버 스트리밍 호출
        responses = stub.GetStreamData(service_pb2.Request(data="Hello"))
        for response in responses:
            print(f"Received: {response.result}")

if __name__ == '__main__':
    run()
