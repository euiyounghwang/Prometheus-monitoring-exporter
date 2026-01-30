import grpc
from concurrent import futures
import time
import service_pb2
import service_pb2_grpc

class DataServiceServicer(service_pb2_grpc.DataServiceServicer):
    def GetStreamData(self, request, context):
        """서버 스트리밍: 데이터 5번 전송"""
        for i in range(5):
            yield service_pb2.Response(result=f"Data {i} for {request.data}")
            time.sleep(1) # 실제 작업 시나리오 (데이터 생산)

def serve():
    port = '50051'
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_DataServiceServicer_to_server(DataServiceServicer(), server)
    server.add_insecure_port('[::]:' + port)
    server.start()
    print("Server started, listening on " + port)
    server.wait_for_termination()

if __name__ == '__main__':
    serve()