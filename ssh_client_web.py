
import os
import paramiko
from dotenv import load_dotenv
import time
import json
import argparse
import logging
import sys
from flask import Flask, jsonify
# from fastapi import FastAPI
# from starlette.middleware.cors import CORSMiddleware
import datetime, time
import warnings
from ssh_client import utils, work

warnings.filterwarnings("ignore")


''' pip install python-dotenv'''
load_dotenv() # will search for .env file in local folder and load variables 

# Configure basic logging to console with INFO level and a custom format
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    stream=sys.stdout)


app = Flask(__name__)
# app = FastAPI(
#     title="FastAPI Basic Docker with k8s Service",
#     description="FastAPI Basic Docker with k8s Service",
#     version="0.0.1",
#     # terms_of_service="http://example.com/terms/",
# )


# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


@app.route("/ssh/<string:env>/<string:service>/<string:cmd>", methods=["GET"])
def service(env, service, cmd):
    '''
    Sample Request:  http://localhost:8000/ssh/new-qa13/kibana/start
    '''
    try:
        logging.info(f"ENV : {env}, Service : {service}, CMD = {cmd}")
        
        ''' load ssh_config.json'''
        ssh_config = utils.load_json_config("./ssh_config.json", env)
        if ssh_config is None:
            return  {
                "status" : 500,
                "message" : "{}".format("Please ensure the env name")
           }
        
        logging.info(json.dumps(ssh_config, indent=2))

        # ''' call to perform the ssh commands'''
        response = work(ssh_config, service, cmd)
        logging.info(f"response : {json.dumps(response, indent=2)}\n")

        return  jsonify(response), 200, {'Content-Type': 'application/json'}
    
    except Exception as e:
        logging.error(e)
        return  jsonify(response), 500, {'Content-Type': 'application/json'}



@app.route('/')
def service_main():
    # return render_template('./index.html', host_name=socket.gethostname().split(".")[0], linked_port=port, service_host=env_name)
    return {
        "app" : "standalone-ssh-service.py",
        "started_time" : datetime.datetime.now()
    }


if __name__ == '__main__':
    """
    Running this service to check the status of tools and send alerts
    python ./ssh-client-web.py --port 8000 or ./ssh_client_web.sh start
    http://localhost:8000/ssh/test/kibana/start
    """
    parser = argparse.ArgumentParser(description="Running this service to check the status of tools and send alerts using this script")
    parser.add_argument('-port', '--port', dest='port', default=8000, help='port')
    args = parser.parse_args()

    if args.port:
        _port = args.port
    
    try:

        ''' Expose this app to acesss'''
        ''' Flask at first run: Do not use the development server in a production environment '''
        ''' For deploying an application to production, one option is to use Waitress, a production WSGI server. '''
        # app.run(host="0.0.0.0", port=int(port)-4000)
        from waitress import serve
        serve(app, host="0.0.0.0", port=_port)
        logging.info(f"# Flask App's Port : {_port}")

    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        logging.info("** Job is being performed..")