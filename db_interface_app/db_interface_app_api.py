# pip install psycopg2-binary

import psycopg2
import jaydebeapi
import jpype
import os, sys
from urllib.parse import urlparse
import argparse
import json
import datetime, time
import logging
import threading
from threading import Thread
import pytz
from flask import Flask, render_template, jsonify, request

import grpc
import service_pb2
import service_pb2_grpc
from google.protobuf.json_format import MessageToJson
from concurrent import futures

import socket
from _thread import *

import dotenv
import warnings
warnings.filterwarnings("ignore")
from pathlib import Path

"""
JayDeBeApi      1.2.3
JPype1          1.5.0
packaging       24.0
pip             20.2.3
psycopg2-binary 2.9.9
setuptools      49.2.1
"""

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    # format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    format='[%(asctime)s] [%(levelname)s] [%(module)s] [%(funcName)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)


''' pip install python-dotenv'''
# load_dotenv() # will search for .env file in local folder and load variables 
# Reload the variables from your .env file, overriding existing ones
dotenv.load_dotenv(dotenv_path=f"{os.path.abspath(os.getcwd())}/.env", override=True)


class Util:

    def __init__(self):
        pass
                
    @staticmethod
    def get_json_load(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data
    
    @staticmethod
    def get_datetime():
        return datetime.datetime.now(tz=pytz.timezone('US/Eastern'))
    

# (.venv) [devuser@localhost db_test]$ pwd
# /home/devuser/Git_Repo/db_test
# (.venv) [devuser@localhost db_test]$ python ./test_db_connection.py
# ('euiyoung', 'ehwang', 11, None)
# (.venv) [devuser@localhost db_test]$

def postgres(connection_str, sql):
    '''
    import psycopg2-binary
    '''
    try:
        p = urlparse(connection_str)
        # print(p.hostname)

        pg_connection_dict = {
            'dbname': p.path[1:],
            'user': p.username,
            'password': p.password,
            'port': p.port,
            'host': p.hostname
        }

        print('pg_connection_dict - ', pg_connection_dict)
        conn = psycopg2.connect(**pg_connection_dict)

        # conn = psycopg2.connect(dbname="postgres",
        #                         user="postgres",
        #                         host="172.25.224.1",
        #                         password="1234",
        #                         port="5432")

        if conn:
            print("Connected to Oracle database successfully!")
        else:
            print("Failed to connect to Oracle database.")

        cursor = conn.cursor()
        cursor.execute(sql)
        results = cursor.fetchall()
        for row in results:
            print('record - ', row)
            break

    except Exception as e:
        print(e)
        pass

    conn.close()
    print("Disconnected to Oracle database successfully!")



class oracle_database:

    def __init__(self, db_url) -> None:
        self.db_url = db_url
        self.set_db_connection()
        

    def set_init_JVM(self):
        '''
        Init JPYPE StartJVM
        '''
        try:
            if jpype.isJVMStarted():
                return
        
            jar = r'./ojdbc8.jar'
            args = '-Djava.class.path=%s' % jar

            # print('Python Version : ', sys.version)
            # print('JAVA_HOME : ', os.environ["JAVA_HOME"])
            # print('JDBC_Driver Path : ', JDBC_Driver)
            # print('Jpype Default JVM Path : ', jpype.getDefaultJVMPath())

            # jpype.startJVM("-Djava.class.path={}".format(JDBC_Driver))
            jpype.startJVM(jpype.getDefaultJVMPath(), args, '-Xrs')

        finally:
            jpype.java.lang.Thread.detach()
            jpype.java.lang.Thread.attachAsDaemon()
 

    def set_init_JVM_shutdown(self):
        # jpype.shutdownJVM() 
        if jpype.isJVMStarted():
            jpype.shutdownJVM() 
   

    def set_db_connection(self):
        ''' DB Connect '''
        print('connect-str : ', self.db_url)
        
        StartTime = datetime.datetime.now()

        # -- Init JVM
        self.set_init_JVM()
        # --
        
        # - DB Connection
        self.db_conn = jaydebeapi.connect("oracle.jdbc.driver.OracleDriver", self.db_url)
        # --
        EndTime = datetime.datetime.now()
        Delay_Time = str((EndTime - StartTime).seconds) + '.' + str((EndTime - StartTime).microseconds).zfill(6)[:2]
        print("# DB Connection Running Time - {}".format(str(Delay_Time)))

    
    def set_db_disconnection(self):
        ''' DB Disconnect '''
        self.db_conn.close()
        logging.info("Disconnected to Oracle database successfully!") 
        print("\n\n")

    
    def get_db_connection(self):
        return self.db_conn
    

    def excute_oracle_query(self, sql):
        '''
        DB Oracle : Excute Query
        '''
        print('excute_oracle_query -> ', sql)
        # Creating a cursor object
        cursor = self.get_db_connection().cursor()

        # Executing a query
        cursor.execute(sql)
        
        # Fetching the results
        results = cursor.fetchall()
        cols = list(zip(*cursor.description))[0]
        # print(type(results), cols)

        json_rows_list = []
        for row in results:
            # print(type(row), row)
            json_rows_dict = {}
            for i, row in enumerate(list(row)):
                json_rows_dict.update({cols[i] : row})
            json_rows_list.append(json_rows_dict)

        cursor.close()

        # logging.info(json_rows_list)
        
        return json_rows_list
        


def oracle(db_url, sql):
    
    database_object = oracle_database(db_url)

    try:
        StartTime = datetime.datetime.now()
    
        # - main sql
        result_json_value = database_object.excute_oracle_query(sql)
        db_rows_list = json.loads(str(result_json_value).replace("'",'"'))

        EndTime = datetime.datetime.now()
        Delay_Time = str((EndTime - StartTime).seconds) + '.' + str((EndTime - StartTime).microseconds).zfill(6)[:2]
        print("# DB Query Running Time - {}".format(str(Delay_Time)))

        # df = pd.DataFrame(results, columns=tuple(zip(*cursor.description))[0])
        # print(df.head())

        response = {
            "running_time" : float(Delay_Time),
            "request_dbid" : str(db_url.rsplit('/', 1)[-1]).upper(),
            "results" : db_rows_list
        }

        print(f"# DB Results : {json.dumps(response, indent=2)}")

        return response

    except Exception as e:
        print(e)
        # pass
    except (KeyboardInterrupt, SystemExit):
        logging.info("# Interrupted..")

    finally:
        if database_object:
            database_object.set_db_disconnection()
            # database_object.set_init_JVM_shutdown()


app = Flask(__name__)

@app.route('/')
def desc():
    # return render_template('./index.html', host_name=socket.gethostname().split(".")[0], linked_port=port, service_host=env_name)
    return {
        "app" : "db_interface_app_api.py",
        "started_time" : datetime.datetime.now()
    }


@app.route('/db_interface', methods=['GET'])
def db_interface_get():
    try:
        logging.info(f"GET Methods...")
        # return render_template('./index.html', host_name=socket.gethostname().split(".")[0], linked_port=port, service_host=env_name)
        return oracle(os.getenv("db_url"), os.getenv("sql")), 200
    except Exception as e:
        logging.error(e)
        # return jsonify(error=404, message=str(e)), 404
        return {"error" : str(e)}, 404


@app.route('/db/get_db_query', methods=['POST'])
def db_interface():
    try:
        logging.info(f"POST Methods...")
        # Access JSON data using request.get_json()
        data = request.get_json(force=True)
        # if request.method == 'POST':
        # return render_template('./index.html', host_name=socket.gethostname().split(".")[0], linked_port=port, service_host=env_name)
        return oracle(data.get('db_url'), data.get('sql')), 200
    
    except Exception as e:
        # return jsonify(error=404, message=str(e)), 404
        logging.error(e)
        return {"error" : str(e)}, 404




''' socket server logic'''
lock = threading.Lock()

class SocketManager(object):
    def __init__(self):
        self.is_client = True
        self.socket_client_list = []
        self.socket_emulator_list = []
        
    def add(self, client, is_client):
        lock.acquire()
        self.socket_client_list.append(client)
        logging.info('Add.. socket client size : {}'.format(len(self.socket_client_list)))
        lock.release()
        
    def remove(self, client, is_client):
        lock.acquire()
        self.socket_client_list.remove(client)
        logging.info('Remove.. socket client size : {}'.format(len(self.socket_client_list)))
        lock.release()


class SocketServer(object):
    
    def __init__(self):
        pass

    def receive_buffer(self, chunks):
        try:
            # Attempt to load the string as a JSON object
            data = json.loads(''.join(chunks))
            # print("## ", data, type(data))
        except (json.JSONDecodeError, TypeError) as e:
            # Catch the specific error raised for invalid JSON or incorrect input types (like None)
            # return False
            data = ''.join(chunks)

        if isinstance(data, (dict, list)):
            print("Json received.. ", json.dumps(data, indent=2), type(data))
        else:
            print("String received.. ", data)
            ''' check disk space and transform into Json'''
            # make_dict_disk_space(received.decode('utf-8'))

        return data

    def threaded_client(self, connection, my_socket, is_client_type):
        try:
            # connection.sendall(str.encode('Welcome to the Servern'))
            
            chunks = []
            while True:
                data = connection.recv(1024)
        
                if not data or data == 'q':
                    break
                    
                chunks.append(data.decode('utf-8'))

            # data = ''.join(chunks)
            # logging.info('Server received ... {}'.format(data))
            # logging.info('response ... {}'.format(get_command_output(data)))

            data_buffer = self.receive_buffer(chunks)

            ''' socket.send is a low-level method It can send less bytes than you requested, but returns the number of bytes sent'''
            ''' socket.sendall is a high-level Python-only method that sends the entire buffer you pass or throws an exception '''
            # connection.sendall(str.encode(reply))
            # connection.sendall(get_command_output(data).encode('utf-8'))

            ''' Json reply'''
            # data = {'msg' : 'Json'}
            ''' Call Orale class to receive the records for the pipeline'''
            # data = oracle(os.getenv("DB_URL"), os.getenv("SQL"))

            print(data_buffer.get("DB_URL"))
            data = oracle(data_buffer.get("DB_URL"), data_buffer.get("SQL"))

            connection.sendall(str.encode(json.dumps(data)))
            # print(f"Send : {json.dumps(data, indent=2)}")

            # common socket client send..
            # if len(my_socket.socket_client_list) > 0:
            #     for _client in my_socket.socket_client_list:
            #         _client.sendall(str.encode(reply))
            
            
        finally:
            # with clients_lock:
            my_socket.remove(connection, is_client_type)
            connection.close()
            # pass


    def server_socket_start(self, my_socket, _port, service_client):
        ''' service_client : client or emulator '''
        
        ServerSocket = socket.socket()
        ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
        ServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1);
        # ServerSocket.settimeout(10000000)
        
        
        # host = '0.0.0.0'  (Docker Container: 0.0.0.0, local test : 127.0.0.1)
        host = os.getenv("HOST", "0.0.0.0")
        port = _port
        ThreadCount = 0
        # clients_lock = threading.Lock()

        try:
            ServerSocket.bind((host, port))
        except socket.error as e:
            print(str(e))

        logging.info('[{}] Waitiing for a Connection..'.format(_port))
        ServerSocket.listen(-1)
        
        try:
            while True:
                client, address = ServerSocket.accept()
                logging.info('New connection from: {} : {}'.format(address[0], str(address[1])))
                start_new_thread(self.threaded_client, (client, my_socket, service_client))
                
                # with clients_lock:
                my_socket.add(client, service_client)
                socket_list_cnt = str(len(my_socket.socket_client_list)) if service_client else str(len(my_socket.socket_emulator_list))
                logging.info('Current socket client size: {}'.format(socket_list_cnt))
                    
        except KeyboardInterrupt as e:
            logging.error(e)
            # sys.exit()
        finally:
            ServerSocket.close()


''' gPRC server logic'''
class DBInterfacer(service_pb2_grpc.DBInterfacerServicer):
    def SayHello(self, request, context):
        return service_pb2.HelloReply(message=f'Hello, {request.name}!')
    
    def GetMetricsStatus(self, request, context):
        logging.info(f"request : {request.db_url}, {request.sql}")

        db_records = oracle(request.db_url, request.sql)
        
        # return service_pb2.DBSQLResponse(records=db_records)
       
        ''' In gRPC, the standard way to return a list of items is to define a message in your .proto file that contains a repeated field of the desired message type. '''
        ''' In your Python gRPC server implementation, you populate the repeated field with the data you want to return. '''
        # Create the response object
        response = service_pb2.DBSQLResponse()

        # Add Element messages to the repeated field
        for each_record in db_records:
            record = response.records.add()
            record.PROCESSNAME = each_record['PROCESSNAME']
            record.STATUS = each_record['STATUS']
            record.ADDTS = each_record['ADDTS']
            record.COUNT = each_record['COUNT']
            record.DBID = each_record['DBID']

        # For debugging or logging, convert the full protobuf message to JSON
        # logging.info(f"Response data in JSON: {MessageToJson(response)}")
        
        return response
            

def run_grpc_server(port):
    # port = '50052'
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_DBInterfacerServicer_to_server(DBInterfacer(), server)
    server.add_insecure_port('[::]:' + port)
    server.start()
    # server.wait_for_termination()
    try:
        while True:
            # logging.info("Server started, listening on " + port)
            time.sleep(60) # One day in seconds
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == "__main__":
    ''' 
    export PYTHONDONTWRITEBYTECODE=1
    pip install grpcio grpcio-tools
    python ./test_db_connection.py --db postgres --url postgresql://postgres:1234@localhost:5432/postgres --sql "SELECT * FROM postgres.user"
    python ./test_db_connection.py --db oracle --url jdbc:oracle:thin:test/test@localhost:12343/test --sql "SELECT * FROM SELECT DBMS_LOB.SUBSTR(JSON_OBJECT, DBMS_LOB.GETLENGTH(JSON_OBJECT)) * FROM test"
    '''
    parser = argparse.ArgumentParser(description="Running db test script")
    parser.add_argument('-p', '--port', dest='port', default=8002, help='port')
    ''' server mode has http, gRPC to support the client'''
    parser.add_argument('-s', '--server_mode', dest='server_mode', default='http', help='server_mode (http, gRPC, socket)')
    args = parser.parse_args()
    
    if args.port:
        port = args.port

    if args.server_mode:
        logging.info(f"gRPC Mode [port:{port}]")
        server_mode = args.server_mode

    # if db_type == 'postgres':
    #     postgres(db_url, sql)

    # elif db_type == 'oracle':
    #     # -- db_url, sql, processname, key-pairs for WHERE Clause
    #     oracle(db_url, sql)

    logging.info("Standalone Promotheus API Exporter Server Started..! [{}]".format(Util.get_datetime()))

    try:
        T = []

        if server_mode == 'http':
            ''' Expose this app to acesss index.html (./templates/index.html)'''
            ''' Flask at first run: Do not use the development server in a production environment '''
            ''' For deploying an application to production, one option is to use Waitress, a production WSGI server. '''
            # app.run(host="0.0.0.0", port=int(port))
            from waitress import serve
            serve(app, host="0.0.0.0", port=port)
            logging.info(f"# Flask App's Port : {port}")
        
        elif server_mode == 'grpc':
            ''' gRPC (Google Remote Procedure Call) is is a remote procedure call (RPC) framework from Google that can run in any environment. It uses Protocol Buffers as a serialization format and uses HTTP2 as the transport medium '''
            ''' 
            # Use the grpcio-tools package to compile the .proto file and generate necessary Python classes for the client and server stubs. The command looks something like this
            python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. service.proto
            '''
            grpc_thread = threading.Thread(target=run_grpc_server, args=(str(port),))
            grpc_thread.daemon = True # Allows the main program to exit
            grpc_thread.start()
            T.append(grpc_thread)

        elif server_mode == 'socket':
            ''' socket mode '''
            my_socket = SocketManager()
            socket_thread = threading.Thread(target=SocketServer().server_socket_start, args=(my_socket, 5044, True))
            socket_thread.daemon = True # Allows the main program to exit
            socket_thread.start()
            T.append(socket_thread)
            pass

        else:
            logging.error(f"Please check server_mode when running..")
    
        # wait for all threads to terminate
        for t in T:
            while t.is_alive():
                t.join(0.5)

    except (KeyboardInterrupt, SystemExit):
        logging.info("# Interrupted..")

    finally:
        # jpype.attachAsDaemon()
        logging.info("Standalone Prometheus Exporter Server exited..!")
        # sys.exit()
    
