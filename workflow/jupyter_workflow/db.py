import os
import jaydebeapi, jpype
import sys
import logging
import json
import pandas as pd
from datetime import datetime

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

class oracle_database:

    def __init__(self, user, db_url, db_type) -> None:
        self.user = user
        self.db_url = db_url
        self.db_conn = None
        self.db_type = db_type
        logging.info(self.db_url)
        # pass

    def set_init_JVM(self):
        '''
        Init JPYPE StartJVM
        '''

        logging.info(f"set_init_JVM")

        try:
            if jpype.isJVMStarted():
                return

            if self.db_type == 'h2':
                jar = r'{}'.format("./h2-2.3.232.jar")
            elif self.db_type == 'oracle':
                jar = r'{}'.format("./ojdbc11.jar")
                
            args = '-Djava.class.path=%s' % jar

            logging.info(f"args : {args}")

            logging.info('Python Version : {}'.format(sys.version))
            # logger.info('JAVA_HOME : ', os.environ["JAVA_HOME"])
            logging.info('Jpype Default JVM Path : {}'.format(jpype.getDefaultJVMPath()))

            # jpype.startJVM("-Djava.class.path={}".format(JDBC_Driver))
            jpype.startJVM(jpype.getDefaultJVMPath(), args, '-Xrs')
        
        except Exception as e:
            logging.info("set_init_JVM :  {}".format(e))


    def set_init_JVM_shutdown(self):
        jpype.shutdownJVM() 
   

    def set_db_connection(self):
        ''' DB Connect '''

        try:
        
            # -- Init JVM
            self.set_init_JVM()
            # --

            user_account = str(self.user).split(",")
            
            # - DB Connection
            if self.db_type == 'h2':
                self.db_conn = jaydebeapi.connect(
                    "org.h2.Driver",
                    self.db_url,
                    user_account,
                    # "./h2-2.3.232.jar"
                )
            elif self.db_type == 'oracle':
                ''' db_rul example : jdbc:oracle:thin:test/test@localhost:1234/DEV'''
                self.db_conn = jaydebeapi.connect("oracle.jdbc.driver.OracleDriver", self.db_url)

            if self.db_conn:
                if self.db_type == 'h2':
                    logging.info("Connected to h2 database successfully!") 
                elif self.db_type == 'oracle':
                    logging.info("Connected to Oracle database successfully!") 
            # --
            
        except Exception as e:
            logging.info("set_db_connection :  {}".format(e))
        

    
    def set_db_disconnection(self):
        ''' DB Disconnect '''
        if self.db_conn:
            self.db_conn.close()
            # self.set_init_JVM_shutdown()
            if self.db_type == 'oracle':
                logging.info("Disconnected to Oracle database successfully!") 
            elif self.db_type == 'h2':
                logging.info("Disconnected to h2 database successfully!") 
                

    
    def get_db_connection(self):
        return self.db_conn
    

    ''' export list with dict based on str type'''
    def select_oracle_query(self, sql):
        '''
        DB Oracle : Excute Query
        '''
        try:
            logging.info(f"excute_oracle_query : {sql}")
            # Creating a cursor object
            cursor = self.get_db_connection().cursor()

            # Executing a query
            cursor.execute(sql)
            
            # Fetching the results
            results = cursor.fetchall()
            cols = list(zip(*cursor.description))[0]
            # logger.info(type(results), cols)

            json_rows_list = []
            for row in results:
                # logger.info(type(row), row)
                json_rows_dict = {}
                for i, row in enumerate(list(row)):
                    json_rows_dict.update({str(cols[i]) : str(row)})
                json_rows_list.append(json_rows_dict)

            cursor.close()

            # self.logger.info(json_rows_list)
            # logging.info(json.dumps(json_rows_list, indent=2))
            
            return json_rows_list
        
        except Exception as e:
            logging.info(e)


    ''' not select'''
    def excute_oracle_query(self, sql):
        '''
        DB Oracle : Excute Query
        '''
        logging.info(f"excute_oracle_query : {sql}")
        # Creating a cursor object
        cursor = self.get_db_connection().cursor()

        # Executing a query
        cursor.execute(sql)
