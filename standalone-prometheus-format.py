#!/usr/bin/env python
"""Basic authentication example

This example demonstrates how to protect Flask endpoints with basic
authentication, using secure hashed passwords.

After running this example, visit http://localhost:5000 in your browser. To
gain access, you can use (username=john, password=hello) or
(username=susan, password=bye).
"""
from flask import Flask
from flask_httpauth import HTTPBasicAuth, MultiAuth
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import sys, os
import base64
import datetime, time
from prometheus_client import start_http_server, Enum, Histogram, Counter, Summary, Gauge, CollectorRegistry
from threading import Thread
import json, pytz
import socket
import pyfiglet
import warnings, logging
warnings.filterwarnings("ignore")

load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)


app = Flask(__name__)
app.config['SECRET_KEY'] = 'top secret!'


auth = HTTPBasicAuth()

# users = {
#     "john": generate_password_hash("hello"),
#     "susan": generate_password_hash("bye")
# }

prometheus_user_credential_gauge_g = Gauge("prometheususer_credential_metrics", 'User Credential Usage', ["server_job", "env", "userid", "userpw"])

@auth.verify_password
def verify_password(username, password):
    # if username in users and check_password_hash(users.get(username),
    #                                              password):
    #     return username
    
    if username == os.getenv("AUTH_USER_ID") and base64.b64encode(password.encode('utf-8')).decode() == os.getenv("AUTH_USER_PW"):
        return True


@app.route('/')
@auth.login_required
def index():
    return "Hello, %s!" % auth.current_user()


@app.route('/metrics/users')
@auth.login_required
def metrics():
    return {
        "test" : "test"
    }


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
    

def work(interval):
    ''' main logic'''

    # generated_exporter = Prometheus_Service_Export(config_each_json)

    while True:
        try:
            ''' Performing'''
            # logging.info("#Performing..")
            ''' initialize '''
            prometheus_user_credential_gauge_g.clear()

            ''' Load config Json file for the user info'''
            config = Util.get_json_load("./standalone-prometheus-format.json")
            for env_name in config.keys():
                for k, v in config.get(env_name).items():
                    prometheus_user_credential_gauge_g.labels(
                        server_job=socket.gethostname(), 
                        env=env_name, 
                        userid=k,
                        userpw=v
                        )\
                    .set(1)
    
            # generated_exporter.service_uptime()

        except (KeyboardInterrupt, SystemExit):
            logging.info("#Interrupted..")
        except Exception as e:
            logging.error(e)
            pass
        
        time.sleep(interval)


if __name__ == '__main__':
    ''' pip install Flask-HTTPAuth --trusted-host pypi.org --trusted-host files.pythonhosted.org --trusted-host pypi.org --trusted-host files.pythonhosted.org '''
    ''' FastAPI HTTP-Basic Implementation - http://pykestrel.medium.com/implementing-basic-authentication-with-python-fastapi-12f9718ff0ad'''
    '''
    scrape_configs:
  - job_name: 'example-app'
    metrics_path: /metrics
    scheme: https
    static_configs:
      - targets: ['localhost:8080']
    basic_auth:
      username: prometheus
      password: <secret> # Can be a secret or a plaintext value, though plaintext is not recommended

    '''

    print(pyfiglet.figlet_format('ES Monitoring!',font= 'doom'))

    logging.info("Standalone Prometheus Exporter Server Started..! [{}]".format(Util.get_datetime()))
    
    try:
        T = []
        
        port=5005

        ''' Prometehus start server '''
        ''' *** '''
        start_http_server(int(port))
        ''' *** '''

        main_th = Thread(target=work, args=(60,))
        main_th.daemon = True
        main_th.start()
        T.append(main_th)
           
                
        ''' Expose this app to acesss index.html (./templates/index.html)'''
        ''' Flask at first run: Do not use the development server in a production environment '''
        ''' For deploying an application to production, one option is to use Waitress, a production WSGI server. '''
        # app.run(host="0.0.0.0", port=int(port)-4000)
        from waitress import serve
        _flask_port = port+1
        serve(app, host="0.0.0.0", port=_flask_port)
        logging.info(f"# Flask App's Port : {_flask_port}")

        # wait for all threads to terminate
        for t in T:
            while t.is_alive():
                t.join(0.5)

    except (KeyboardInterrupt, SystemExit):
        logging.info("# Interrupted..")

    finally:
        logging.info("Standalone Prometheus Exporter Server exited..!")
