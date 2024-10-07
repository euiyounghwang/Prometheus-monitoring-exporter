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
import xlsxwriter
warnings.filterwarnings("ignore")


''' pip install python-dotenv'''
load_dotenv() # will search for .env file in local folder and load variables 

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

current_path = os.path.dirname(os.path.abspath(__file__))
path = os.path.dirname(os.path.abspath(__file__)) + '/output'
file_output = path + "/disk-usage-prod-{}.xlsx".format(datetime.datetime.today().strftime('%Y-%m-%d'))


def generate_excel(global_host_dict, data):

    def output_clear():
        if not os.path.exists(path):
             os.makedirs(path)

        if os.path.exists(file_output):
            os.remove(file_output)
        

    ''' generate excel'''
    try:
        logging.info("generate_excel")

        output_clear()

        results = []
        for index, each_json in enumerate(data):
            for row in each_json.values():
                for v in row:
                    results.append([v.get("category"), v.get("host"), v.get("disktotal"),v.get("diskavail"),v.get("diskused"),v.get("diskusedpercent"),v.get("env_name"),v.get("ip"),v.get("name")])
                    # if v.get("env_name") in global_host_dict.keys():
                        # results.append([v.get("category"), global_host_dict.get(v.get("env_name"),"").get(v.get("name"), ""), v.get("disktotal"),v.get("diskavail"),v.get("diskused"),v.get("diskusedpercent"),v.get("env_name"),v.get("ip"),v.get("name")])

        ''' response df with sparkjob position that's status is N'''
        df = pd.DataFrame(
                # [['Dev#1', "Dev spark job Dev spark job Dev spark job", "localhost", "localhost", "test_job", "Y"], ["Dev#2", "Dev spark job", "localhost", "localhost", "test_job", "N"]], 
                results,
                columns=["Category", "Server Name", "Disk_Total", "Disk_Avaiable", "Disk_Used", "Disk_Used_Percentage", "ENV_NAME", "IP Address", "Description"]
            )
        
        '''
        return df from service layer 
        df = pd.DataFrame(
                [["Canada", 10], ["USA", 20]], 
                columns=["team", "points"]
        )
        '''

        '''
        # -- csv
        https://xlsxwriter.readthedocs.io/working_with_pandas.html
        return StreamingResponse(
                iter([df.to_csv(index=False)]),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename=ES_SPARK_JOBS_{datetime.datetime.now().strftime('%Y%m%d')}.csv"}
                # headers={"Content-Disposition": f"attachment; filename=data.csv"}
        )
        '''
        # - getnerate excel file
        workbook = xlsxwriter.Workbook(file_output)
        worksheet = workbook.add_worksheet(str(datetime.datetime.today().strftime('%Y-%m-%d')))

        (max_row, max_col) = df.shape
        header_format = workbook.add_format( # !!! here workable, no error
                {
                    'bold': True,
                    'text_wrap': True,
                    'valign': 'top',
                    'valign': 'center',
                    # 'fg_color': '#D7E4BC',
                    # 'bg_color': '#edbd93',
                    'bg_color': 'yellow',
                    'border': 1
                }
            )

        for col_num, value in enumerate(df.columns.values):
            # print(col_num, value)
            worksheet.write(0, col_num, value, header_format)
            worksheet.set_column(0, col_num, 15)
            worksheet.autofilter(0, 0, max_row, max_col - 1)
            worksheet.autofit()
            col_num += 1

        ''' response df with sparkjob position that's status is N'''
        # frm2 = workbook.add_format({'bold': True,'bg_color': 'white',})
        for idx, rows in enumerate(results):
            for idx1, row in enumerate(rows) :
                worksheet.write(idx+1, idx1, rows[idx1])
                worksheet.autofit()

        workbook.close()

    except Exception as e:
        logging.error(e)
    

def get_metrics_from_expoter_app():
    ''' get metrics from prometheus app''' 

    def get_global_host_configuration(es_http_host):
        ''' get global configuration through ES configuration REST API'''

        
        def json_read_config(path):
            ''' read config file with option'''
            with open(path, "r") as read_file:
                data = json.load(read_file)
            return data

        try:
            """
            Call API to get host information with key like 'dev'
            es_config_host = str(es_http_host)
            resp = requests.get(url="http://{}:8004/config/get_host_info".format(es_config_host), timeout=5)
                    
            if not (resp.status_code == 200):
                ''' save failure node with a reason into saved_failure_dict'''
                logging.error(f"es_config_interface api do not reachable")
                    
            # logging.info(f"get_mail_config - {resp}, {json.dumps(resp.json(), indent=2)}")
            logging.info(f"get_global_configuration - {resp}")
            return resp.json()
            """
            return json_read_config(current_path + "/env_hosts.json")
            
        except Exception as e:
            logging.error(e)
            # pass


    def transform_prometheus_txt_to_Json(host, env_name, response):
        ''' transform_prometheus_txt_to_Json '''
        body_list = [body for body in response.text.split("\n") if not "#" in body and len(body)>0]
        
        prometheus_json = {}
        prometheus_json_list = []
        loop = 0
        for x in body_list:
            json_key_pairs = x.split("} ")
            key = json_key_pairs[0]
            if 'node_disk_space_metric' in key:
                json_key_pairs[0] = json_key_pairs[0].replace('node_disk_space_metric','')
                # print("json_key_pairs[0]", json_key_pairs[0])
                extract_keys = json_key_pairs[0].replace("{","").replace("}","").replace("\"","").split(",")
                # print("extract_keys", extract_keys)
                json_keys_list = {each_key.split("=")[0] : each_key.split("=")[1] for each_key in extract_keys}
                # print("json_keys_list", json_keys_list)

                prometheus_json_list.append({
                        'category' : json_keys_list.get('category'),
                        # 'host' : host,
                        'host' : json_keys_list.get('host'),
                        'disktotal' : json_keys_list.get('disktotal'),
                        'diskavail' : json_keys_list.get('diskavail'),
                        'diskused' : json_keys_list.get('diskused'),
                        'diskusedpercent' : json_keys_list.get('diskusedpercent'),
                        'ip' : json_keys_list.get('ip'),
                        'name' : json_keys_list.get('name'),
                        'env_name' : env_name
                    }
                )
                loop += 1
                
        # print(json.dumps(prometheus_json, indent=2))
        """
         {
            "0-node_disk_space_metric{category=\"Elastic": "Node\",diskavail=\"1.7gb\",disktotal=\"1.8gb\",diskused=\"1.1gb\",diskusedpercent=\"1.08%\",ip=\"0.0.0.0\",name=\"test-node-1\",server_job=\"localhost\"}",
        }
        """
        prometheus_json_list = sorted(prometheus_json_list, key=lambda k: k['name'], reverse=False)
        prometheus_json.update({host : prometheus_json_list})

        return prometheus_json
    
    try:
        disk_usage_host_list = []
        host_list = str(os.getenv('PROMETHEUS_HOST')).split(",")
        for each_host in host_list:
            host = each_host.split(":")[1]
            env_name = each_host.split(":")[0]
            resp = requests.get(url="http://{}:9115/metrics".format(host), timeout=5)
                        
            if not (resp.status_code == 200):
                ''' save failure node with a reason into saved_failure_dict'''
                logging.error(f"get_metrics_from_expoter_app port do not reachable")
                
            logging.info(f"resp : {resp}")

            ''' extract content'''
            prometheus_json = transform_prometheus_txt_to_Json(host, env_name, resp)
            disk_usage_host_list.append(prometheus_json)

        # logging.info(f"disk_usage_host_list : {json.dumps(disk_usage_host_list, indent=2)}")  

        ''' get hostname from prometheus export directly after deployed Prometheus Export that has additional request(get_host_info) for this'''
        generate_excel(get_global_host_configuration(None), disk_usage_host_list)  
        
    except Exception as e:
        logging.error(e)


def work():
    try:
        ''' call Prometheus API'''
        get_metrics_from_expoter_app()

    except Exception as e:
        logging.error(e)    



if __name__ == '__main__':
    """
    python ./scripts/extract_disk_usage_export.py
    """
    parser = argparse.ArgumentParser(description="Extract Prometheus Disk Usage of ES/Kafka all nodes using this script")
    # parser.add_argument('-t', '--ts', dest='ts', default="https://localhost:9201", help='host target')
    args = parser.parse_args()
    
        
    # --
    # Only One process we can use due to 'Global Interpreter Lock'
    # 'Multiprocessing' is that we can use for running with multiple process
    # --
    try:
        ''' Add HTTP Server for checking this process'''
        # HTTP_Server()
    
        T = []
        th1 = Thread(target=work, args=())
        th1.daemon = True
        th1.start()
        T.append(th1)
        
        for t in T:
            while t.is_alive():
                t.join(0.5)
        # work(target_server)
   
    except Exception as e:
        logging.error(e)
        pass