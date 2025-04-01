import logging
import json
import datetime
import redis
import os

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

class Redis_Client:

    def __init__(self, startup_nodes):
        """
        https://soyoung-new-challenge.tistory.com/117
        $ redis-cli
        127.0.0.1:6379> set [key] [value]
        127.0.0.1:6379> mset [key] [value] [key2] [value2] [key3] [value3] ...
        127.0.0.1:6379> get [key]
        127.0.0.1:6379> mget [key] [value] [key2] [value2] [key3] [value3] ...

        127.0.0.1:6379> keys *

        # incre Key Count
        127.0.0.1:6379> INCR [key]
        127.0.0.1:6379> del [key]
        :param server_ip:
        :param port:
        """
        # self.SERVER_IP = server_ip
        # self.PORT = port
        self.startup_nodes = startup_nodes
        self.rd_client = None
        # Cache is None
        self.Max_Minutes = 100000000


    def Set_Connect(self):
        """

        :return:
        """
        from rediscluster import RedisCluster
        """
        startup_nodes = [
                            {"host": localhost", "port": "6379"},
                            {"host": "localhost", "port": "6479"},
                            {"host": "localhost", "port": "6579"}
                        ]
        """
        # self.rd_client = RedisCluster(startup_nodes=self.startup_nodes, decode_responses=True)
        self.rd_client = redis.StrictRedis(host=self.startup_nodes, port=6379, db=0)
        print('\n')
        logging.info('Redis Set_Connect..')
        

    def Set_Close(self):
        """

        :return:
        """
        self.rd_client.close()
        logging.info('Redis Client Closed..')
        

    def Set_Memory_dict(self, key, values):
        """

        :param key:
        :param values:
        :return:
        """
        # json dumps
        jsonDataDict = json.dumps(values, ensure_ascii=False).encode('utf-8')
        # jsonDataDict = json.dumps(values, ensure_ascii=False)

        # Redis Set
        self.rd_client.delete(key)
        self.rd_client.set(key, jsonDataDict)
        # self.rd_client.set(key, values)


    def Get_keys(self):
        """

        :param key:
        :return:
        """
        return self.rd_client.keys()


    def Set_Delete_Keys(self, key):
        """

        :param key:
        :return:
        """
        self.rd_client.delete(key)


    def Get_Memory_dict(self, key):
        """

        :param key:
        :return:
        """
        # Redis get
        resultData = self.rd_client.get(key)
        # resultData = resultData.decode('utf-8')

        # json loads
        # print('\n')
        if resultData:
            result = dict(json.loads(resultData))
        else:
            result= {}

        return result

    def Get_Memory_Time_Diff(self, key):
        """

        :param key:
        :return:
        """
        # Redis get
        resultData = self.rd_client.get(key)

        if resultData is None:
            return int(self.Max_Minutes)
        else:
            # print('resultData ', resultData)
            result = dict(json.loads(resultData))
            # print('self.rd_client.get(key) ', result)
            delta = datetime.datetime.now() - datetime.datetime.strptime(result['INPUTDATE'], "%Y-%m-%d %H:%M:%S")
            # print(delta, delta.seconds/60)
            return float(delta.seconds/60)
            # return 11


    def Set_Clear_Memory(self):
        """

        :return:
        """
        print('\n')
        ''' Redis all keys was deleted at once '''
        self.rd_client.flushdb()
        logging.info('Set_Clear_Memory..')
