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
import warnings
warnings.filterwarnings("ignore")


"""
JayDeBeApi      1.2.3
JPype1          1.5.0
kafka-python    2.0.2
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


    def set_init_JVM_shutdown(self):
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
        print("Disconnected to Oracle database successfully!") 

    
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

    except Exception as e:
        print(e)
        pass

    finally:
        database_object.set_db_disconnection()
        # database_object.set_init_JVM_shutdown()


if __name__ == "__main__":
    ''' 
    python ./test_db_connection.py --db postgres --url postgresql://postgres:1234@localhost:5432/postgres --sql "SELECT * FROM postgres.user"
    python ./test_db_connection.py --db oracle --url jdbc:oracle:thin:test/test@localhost:12343/test --sql "SELECT * FROM SELECT DBMS_LOB.SUBSTR(JSON_OBJECT, DBMS_LOB.GETLENGTH(JSON_OBJECT)) * FROM test"
    '''
    parser = argparse.ArgumentParser(description="Running db test script")
    parser.add_argument('-d', '--db', dest='db', default="postgres", help='choose one of db')
    # parser.add_argument('-u', '--url', dest='url', default="postgresql://postgres:1234@localhost:5432/postgres", help='db url')
    parser.add_argument('-u', '--url', dest='url', default="jdbc:oracle:thin:test/test@localhost:12343/test", help='db url')
    parser.add_argument('-s', '--sql', dest='sql', default="select * from test", help='sql')
    args = parser.parse_args()
    
    if args.db:
        db_type = args.db

    if args.url:
        db_url = args.url
    
    if args.sql:
        sql = args.sql

    # if db_type == 'postgres':
    #     postgres(db_url, sql)

    # elif db_type == 'oracle':
    #     # -- db_url, sql, processname, key-pairs for WHERE Clause
    #     oracle(db_url, sql)

    logging.info("Standalone Promotheus API Exporter Server Started..! [{}]".format(Util.get_datetime()))

    try:
        T = []

        oracle(db_url, sql)
        
        # main_th = Thread(target=work, args=(db_type, db_url, sql, 60))
        # main_th.daemon = True
        # main_th.start()
        # T.append(main_th)

                
        ''' Expose this app to acesss index.html (./templates/index.html)'''
        ''' Flask at first run: Do not use the development server in a production environment '''
        ''' For deploying an application to production, one option is to use Waitress, a production WSGI server. '''
        # app.run(host="0.0.0.0", port=int(port)-4000)
        # from waitress import serve
        # _flask_port = port+1
        # serve(app, host="0.0.0.0", port=_flask_port)
        # logging.info(f"# Flask App's Port : {_flask_port}")

        # wait for all threads to terminate
        for t in T:
            while t.is_alive():
                t.join(0.5)

    except (KeyboardInterrupt, SystemExit):
        logging.info("# Interrupted..")

    finally:
        logging.info("Standalone Prometheus Exporter Server exited..!")
    
