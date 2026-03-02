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
from concurrent import futures

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
        
        print(f"# DB Results : {json.dumps(db_rows_list, indent=2)}")

        EndTime = datetime.datetime.now()
        Delay_Time = str((EndTime - StartTime).seconds) + '.' + str((EndTime - StartTime).microseconds).zfill(6)[:2]
        print("# DB Query Running Time - {}".format(str(Delay_Time)))

        # df = pd.DataFrame(results, columns=tuple(zip(*cursor.description))[0])
        # print(df.head())

        return db_rows_list

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
        return oracle(os.getenv("DB_URL"), os.getenv("SQL")), 200
    except Exception as e:
        logging.error(e)
        # return jsonify(error=404, message=str(e)), 404
        return {"error" : str(e)}, 404


@app.route('/db_interface', methods=['POST'])
def db_interface():
    try:
        logging.info(f"POST Methods...")
        # Access JSON data using request.get_json()
        data = request.get_json(force=True)
        # if request.method == 'POST':
        # return render_template('./index.html', host_name=socket.gethostname().split(".")[0], linked_port=port, service_host=env_name)
        return oracle(data.get('DB_URL'), data.get('SQL')), 200
    
    except Exception as e:
        # return jsonify(error=404, message=str(e)), 404
        logging.error(e)
        return {"error" : str(e)}, 404



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
        
        return response
            
        

def run_grpc_server(port):
    # port = '50052'
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_DBInterfacerServicer_to_server(DBInterfacer(), server)
    server.add_insecure_port('[::]:' + port)
    server.start()
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
    parser.add_argument('-s', '--server_mode', dest='server_mode', default='http', help='server_mode')
    args = parser.parse_args()
    
    if args.port:
        port = args.port

    if args.server_mode:
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
    
