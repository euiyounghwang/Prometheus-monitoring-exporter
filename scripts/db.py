import os
import jaydebeapi, jpype
import sys
import logging

logger = logging.getLogger("airflow.task")


current_path = os.path.dirname(os.path.abspath(__file__))


class oracle_database:

    def __init__(self, user, db_url) -> None:
        self.user = user
        self.db_url = db_url
        self.db_conn = None
        logger.info(self.db_url)
        # pass

    def set_init_JVM(self):
        '''
        Init JPYPE StartJVM
        '''

        try:
            if jpype.isJVMStarted():
                return
            
            jar = r'{}/{}'.format(current_path, "h2-2.3.232.jar")
            args = '-Djava.class.path=%s' % jar

            logger.info('Python Version : {}'.format(sys.version))
            # logger.info('JAVA_HOME : ', os.environ["JAVA_HOME"])
            logger.info('Jpype Default JVM Path : {}'.format(jpype.getDefaultJVMPath()))

            # jpype.startJVM("-Djava.class.path={}".format(JDBC_Driver))
            jpype.startJVM(jpype.getDefaultJVMPath(), args, '-Xrs')
        
        except Exception as e:
            logger.info("set_init_JVM :  {}".format(e))


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
            self.db_conn = jaydebeapi.connect(
                "org.h2.Driver",
                self.db_url,
                user_account,
                # "./h2-2.3.232.jar"
            )
            # --
            
        except Exception as e:
            logger.info("set_db_connection :  {}".format(e))
        

    
    def set_db_disconnection(self):
        ''' DB Disconnect '''
        if self.db_conn:
            self.db_conn.close()
            # self.set_init_JVM_shutdown()
            logger.info("Disconnected to Oracle database successfully!") 

    
    def get_db_connection(self):
        return self.db_conn
    

    ''' export list with dict based on str type'''
    def select_oracle_query(self, sql):
        '''
        DB Oracle : Excute Query
        '''
        try:
            logger.info(f"excute_oracle_query : {sql}")
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
            # logger.info(json.dumps(json.loads(json_rows_list), indent=2))
            
            return json_rows_list
        
        except Exception as e:
            logger.info(e)


    ''' not select'''
    def excute_oracle_query(self, sql):
        '''
        DB Oracle : Excute Query
        '''
        logger.info(f"excute_oracle_query : {sql}")
        # Creating a cursor object
        cursor = self.get_db_connection().cursor()

        # Executing a query
        cursor.execute(sql)