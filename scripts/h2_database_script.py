import os
import requests
from dotenv import load_dotenv
import logging
import argparse
from dotenv import load_dotenv
import os
from datetime import datetime
from threading import Thread
import json
import warnings
from io import BytesIO
import pandas as pd
import datetime
import jaydebeapi, jpype
import logging
import sys

warnings.filterwarnings("ignore")

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


class oracle_database:

    def __init__(self, user, db_url) -> None:
        self.logger = logging
        self.user = user
        self.db_url = db_url
        self.db_conn = None
        # pass

    def set_init_JVM(self):
        '''
        Init JPYPE StartJVM
        '''

        try:
            if jpype.isJVMStarted():
                return
            
            jar = r'./h2-2.3.232.jar'
            args = '-Djava.class.path=%s' % jar

            print('Python Version : ', sys.version)
            # print('JAVA_HOME : ', os.environ["JAVA_HOME"])
            print('Jpype Default JVM Path : ', jpype.getDefaultJVMPath())

            # jpype.startJVM("-Djava.class.path={}".format(JDBC_Driver))
            jpype.startJVM(jpype.getDefaultJVMPath(), args, '-Xrs')
        
        except Exception as e:
            self.logger.error("set_init_JVM :  {}".format(e))


    def set_init_JVM_shutdown(self):
        jpype.shutdownJVM() 
   

    def set_db_connection(self):
        ''' DB Connect '''

        try:
        
            StartTime = datetime.datetime.now()

            # -- Init JVM
            self.set_init_JVM()
            # --

            user_account = str(self.user).split(",")
            
            # - DB Connection
            self.db_conn = jaydebeapi.connect(
                "org.h2.Driver",
                self.db_url,
                user_account,
                # "./h2-2.3.232.jar"
            )
            # --
            EndTime = datetime.datetime.now()
            Delay_Time = str((EndTime - StartTime).seconds) + '.' + str((EndTime - StartTime).microseconds).zfill(6)[:2]
            print("# DB Connection Running Time - {}".format(str(Delay_Time)))
        
        except Exception as e:
            self.logger.error("set_db_connection :  {}".format(e))
        

    
    def set_db_disconnection(self):
        ''' DB Disconnect '''
        if self.db_conn:
            self.db_conn.close()
            # self.set_init_JVM_shutdown()
            self.logger.info("Disconnected to Oracle database successfully!") 

    
    def get_db_connection(self):
        return self.db_conn
    

    ''' export list with dict based on str type'''
    def excute_oracle_query(self, sql):
        '''
        DB Oracle : Excute Query
        '''
        try:
            self.logger.info(f"excute_oracle_query : {sql}")
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
                    json_rows_dict.update({str(cols[i]) : str(row)})
                json_rows_list.append(json_rows_dict)

            cursor.close()

            # self.logger.info(json_rows_list)
            # print(json.dumps(json.loads(json_rows_list), indent=2))
            
            return json_rows_list
        
        except Exception as e:
            self.logger.error(e)
    


def work(db_url, user, sql):
    """
    query = "SELECT * FROM MONITORING"
    connection  = jaydebeapi.connect(
        "org.h2.Driver",
        "jdbc:h2:tcp://localhost/monitoring/h2/data/monitoring",
        ["test", "test"],
        "../h2-1.4.200.jar")
    cursor = connection.cursor()
    cursor.execute(query)
    if returnResult:
        returnResult = _convert_to_schema(cursor)
    cursor.close()
    connection.close()
    """
    try:
        db_obj = oracle_database(user, db_url)
        db_obj.set_db_connection()
        result_dict = db_obj.excute_oracle_query(sql)
        '''  <class 'list'> <- result_dict '''
        logging.info(json.dumps(result_dict, indent=2))

    except Exception as e:
        logging.error(e)

    finally:
        db_obj.set_db_disconnection()
      



if __name__ == '__main__':
    """
    python ./scripts/h2_database_script.py
    """
    parser = argparse.ArgumentParser(description="Logging using this script")
    parser.add_argument('-db_url', '--db_url', dest='db_url', default="jdbc:h2:tcp://localhost/monitoring/h2/data/monitoring", help='db_url')
    parser.add_argument('-user_account', '--user_account', dest='user_account', default="test,test", help='user')
    parser.add_argument('-sql', '--sql', dest='sql', default="SELECT * FROM MONITORING", help='sql')
    args = parser.parse_args()
    
    if args.db_url:
        db_url = args.db_url

    if args.user_account:
        user_account = args.user_account
    
    if args.sql:
        sql = args.sql

    # --
    # Only One process we can use due to 'Global Interpreter Lock'
    # 'Multiprocessing' is that we can use for running with multiple process
    # --
    try:
        work(db_url, user_account, sql)
   
    except Exception as e:
        logging.error(e)
        pass