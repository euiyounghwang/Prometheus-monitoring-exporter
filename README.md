# prometheus-export
<i>python-prometheus-export

Prometheus provides client libraries based on Python, Go, Ruby and others that we can use to generate metrics with the necessary labels. 
- Such an exporter can be included directly in the code of your application
- it can be run as a separate service that will poll one of your services and receive data from it, which will then be converted into the Prometheus format and sent to the Prometheus server. 

When Prometheus scrapes your instance's HTTP endpoint, the client library sends the current state of all tracked metrics to the server.

The prometheus_client package supports exposing metrics from software written in Python, so that they can be scraped by a Prometheus service.
Metrics can be exposed through a standalone web server, or through Twisted, WSGI and the node exporter textfile collector.
- Prometheus SSL: (Reference: https://velog.io/@zihs0822/Prometheus-Security)
  - openssl req -x509 -newkey rsa:4096 -nodes -keyout private.key -out certificate.crt 
  - openssl x509 -in ./certificate.crt -subject -noout
  - cat web.yml
  ```bash
    tls_server_config:
        cert_file: /certs/certificate.crt
        key_file: /certs/private.key
    basic_auth_users:
        es_view: base64.encode(test)
  ```

  - Run : /home/prometheus/prometheus-2.35.0.linux-amd64/prometheus --config.file=/home/prometheus/prometheus-2.35.0.linux-amd64/prometheus.yml --storage.tsdb.path=/home/prometheus/prometheus-2.35.0.linux-amd64 --web.enable-lifecycle --web.config.file=/home/prometheus/prometheus-2.35.0.linux-amd64/config/web.yml
 
  - Query: Prometheus Query via API (http://localhost:9090/api/v1/query?query=es_health_metric{server_job="localhost"})
  - HA : Thanos, Thanos Side car & Querier (https://bcho.tistory.com/1375) - Installation (https://github.com/thanos-io/thanos/releases)


- Jupyter Notebook for TLS : You can start the notebook to communicate via a secure protocol mode by setting the certfile option to your self-signed certificate
  - https://jupyter-notebook.readthedocs.io/en/6.2.0/public_server.html
  - You can start the notebook to communicate via a secure protocol mode by setting the certfile option to your self-signed certificate, i.e. mycert.pem, with the command:
  - A self-signed certificate can be generated with openssl. For example, the following command will create a certificate valid for 365 days with both the key and certificate data written to the same file:
  - openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout mykey.key -out mycert.pem
  - jupyter notebook --ip 0.0.0.0 --certfile=./certs/mycert.pem --keyfile ./certs/mykey.key
  - openssl x509 -in ./mycert.pem -subject -noout
  - openssl x509 -enddate -noout -in ./mycert.pem 
    notAfter=Jan 18 20:58:27 2035 GMT

- Openssl allows us to retrieve the ssl expiration date from the remote serivce url. The openssl "s_client" command is a powerful tool for interacting with 
SSL/TLS servers 
  - openssl s_client -connect localhost:9200 -showcerts 
  - echo | openssl s_client -connect localhost:8480 | openssl x509 -noout -dates
  - To find a remote server's certificate expiration date using `Python's pyOpenSSL library`, you can use the SSL_get_peer_certificate() method to get the certificate and then inspect its get_notAfter() method, which returns a datetime object representing the expiration


- API Interface : DB Interface API to get the recors from the DB(https://github.com/euiyounghwang/DB-Interface-Export), ES Configuration API to get the configuration for all env's(https://github.com/euiyounghwang/es-config-interface), Kafka Interface API to get Offsets/ISR information(https://github.com/euiyounghwang/kafka_job_interface_service)


- Grafana : Add CSV plugin (unzip `/home/devuser/monitoring/grafana-8.0.0/data/plugins/marcusolsson-csv-datasource-0.6.21.linux_amd64.zip`) and then restart Grafana, Documentation(https://grafana.com/docs/grafana/latest/administration/plugin-management/, https://grafana.github.io/grafana-csv-datasource/installation/, https://deyoun.tistory.com/80)

- Gradio : Gradio is the fastest way to demo your machine learning model with a friendly web interface so that anyone can use it. Gradio is an open-source Python package that allows you to quickly build a demo or web application for your machine learning model, API, or any arbitrary Python function. You can then share a link to your demo or web application in just a few seconds using Gradio's built-in sharing features. No JavaScript, CSS, or web hosting experience needed!
```bash
import gradio as gr

def greet(name):
    return "Hello " + name + "!"

demo = gr.Interface(fn=greet, inputs="text", outputs="text")
demo.launch()   
```

- Fabric: Fabric(https://www.fabfile.org/) is a high level Python (2.7, 3.4+) library designed to execute shell commands remotely over SSH,
```bash
#!/bin/bash
set -e

SCRIPTDIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
# cd $SCRIPTDIR
echo $SCRIPTDIR
# echo $BASE_DIR

VENV=".venv"

# Python 3.11.7 with Window
if [ -d "$VENV/bin" ]; then
    source $BASE_DIR/$VENV/bin/activate
else
    source $BASE_DIR/$VENV/Scripts/activate
fi

export PYTHONDONTWRITEBYTECODE=1

cd $SCRIPTDIR

#-- Generial
# fab dev_nodes:user="test",services="update_node_deploy_service"

#-- ES Monitoring Apps on the instance
# fab dev_same_instance:user="test",services="update_deploy_service"

#-- ES Expoter on the instance
# fab es_exporter:user="test",services="update_deploy_service"

```

#### Python V3.9 Install
```bash
sudo yum install gcc openssl-devel bzip2-devel libffi-devel zlib-devel git sqlite-devel
wget https://www.python.org/ftp/python/3.9.0/Python-3.9.0.tgz 
tar –zxvf Python-3.9.0.tgz or tar -xvf Python-3.9.0.tgz 
cd Python-3.9.0 
./configure --libdir=/usr/lib64 
sudo make 
sudo make altinstall 
which python3.9
rm /usr/bin/python
ln -s /usr/local/bin/python3.9 /usr/bin/python

# python3 -m venv .venv --without-pip
sudo yum install python3-pip

sudo ln -s /usr/lib64/python3.9/lib-dynload/ /usr/local/lib/python3.9/lib-dynload

python3 -m venv .venv
source .venv/bin/activate

# pip install -r ./dev-requirement.txt
pip install prometheus-client
pip install requests
pip install JPype1
pip install psycopg2-binary
pip install jaydebeapi
pip install pytz
pip install httpx

# when error occur like this
# ImportError: urllib3 v2 only supports OpenSSL 1.1.1+, currently the 'ssl' module is compiled with 'OpenSSL 1.0.2k-fips  26 Jan 2017'. See: https://github.com/urllib3/urllib3/issues/2168
pip install urllib3==1.26.18
pip install pytz
```


### Using Poetry: Create the virtual environment in the same directory as the project and install the dependencies:
- Gunicorn is a Python WSGI HTTP Server that usually lives between a reverse proxy (e.g., Nginx) or load balancer (e.g., AWS ELB) and a web application such as Django or Flask.
- Better performance by optimizing Gunicorn config (https://medium.com/building-the-system/gunicorn-3-means-of-concurrency-efbb547674b7)
- The suggested number of workers is (2*CPU)+1.
- gunicorn --workers=5 --threads=2 --worker-class=gthread main:app, the maximum concurrent requests areworkers * threads 10 in our case.

- Poetry (https://velog.io/@qlgks1/python-poetry-%EC%84%A4%EC%B9%98%EB%B6%80%ED%84%B0-project-initializing-%ED%99%9C%EC%9A%A9%ED%95%98%EA%B8%B0)
```bash
python -m venv .venv
source .venv/bin/activate
pip install poetry

# --
poetry config virtualenvs.in-project true
poetry init
poetry add prometheus-client
poetry add psutil
poetry add pytz
poetry add JPype1
poetry add psycopg2-binary
poetry add jaydebeapi

# ------------------
# Sample
poetry add django
# 개발환경에서 필요한 패키지 설치
poetry add --group dev pytest
# 버전을 지정가능
poetry add django@^3.0.0
poetry add "django=3.0.0"
# 최신버전을 설치
poetry add django@latest
# 깃 저장소에 있는 패키지 설치
poetry add git+https://github.com/django/django.git
# 깃 저장소의 패키지에서 브랜치를 지정
poetry add git+https://github.com/django/django.git#stable/2.2.x
# 로컬에 디렉토리의 파일로 설치하기
poetry add ./my-package/
poetry add ./my-package/dist/my-package-0.1.0.tar.gz
poetry add ./my-package/dist/my-package-0.1.0.whl

# 의존성 설치
poetry install
# 개발환경의 의존성은 빼고 설치
poetry install --no-dev
# -E 또는 --extras 로 추가 의존성을 설정가능
poetry install --extras "mysql redis"
poerty install -E mysql -E redis
...
# ------------------
...

# start with gunicorn config
gunicorn.config.py

import multiprocessing
 
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
wsgi_app = "app.main:app"
timeout = 60
loglevel = "info"
bind = "0.0.0.0:8000"
max_requests = 1000
max_requests_jitter = 100

...
gunicorn -c app/gunicorn.config.py

gunicorn -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8004 --workers 4

..
uvicorn app.main:app --reload for dev
```
or you can run this shell script `./create_virtual_env.sh` to make an environment. then go to virtual enviroment using `source .venv/bin/activate`



### Architecture
- Prometheus, Loki(https://github.com/grafana/loki, API : https://grafana.com/docs/loki/latest/reference/loki-http-api/), Promtail, Grafana, Collector as export app (Exports data in the Prometheus format, which allows it to be scraped by a Prometheus server.)

- Prometheus login credentials
```bash
''' https://velog.io/@zihs0822/Prometheus-Security '''
openssl req -x509 -newkey rsa:4096 -nodes -keyout private.key -out certificate.crt 
cat web.yml
tls_server_config:
        cert_file: /certs/certificate.crt
        key_file: /certs/private.key

ExecStart=/home/prometheus/prometheus-2.35.0.linux-amd64/prometheus \
  --config.file=/home/prometheus/prometheus-2.35.0.linux-amd64/prometheus.yml \
  --storage.tsdb.path=/home/prometheus/prometheus-2.35.0.linux-amd64 \
  --web.enable-lifecycle \
  --web.config.file=/home/prometheus/prometheus-2.35.0.linux-amd64/config/web.yml
# -----------------------------
cat web.yml
basic_auth_users:
        dbaas: test_with_bcrypted
```

- Promtail(https://github.com/grafana/loki/releases/) is an agent which ships the contents of local logs to a private Grafana Loki. Loki is a horizontally scalable, highly available, multi-tenant log aggregation system inspired by Prometheus and developed by Grafana Labs. Loki(https://github.com/grafana/loki/releases/) aims to simplify effective and user-friendly collection and storage of logs.
- A Loki-based logging stack consists of 3 components:
  - promtail is the agent, responsible for gathering logs and sending them to Loki.
  - loki is the main server, responsible for storing logs and processing queries.
  - Grafana for querying and displaying the logs.
- Flow (./architecure/Data_Flow.PNG)
- https://rulyox.blog/2021-10-24-Prometheus-Loki-Grafana%EB%A5%BC-%EC%9D%B4%EC%9A%A9%ED%95%9C-%EB%AA%A8%EB%8B%88%ED%84%B0%EB%A7%81-%EC%8B%9C%EC%8A%A4%ED%85%9C-%EA%B5%AC%EC%B6%95/
- Installation : https://m.blog.naver.com/setopia1112/223123551825
- Grafana Loki Setup
```bash
wget https://github.com/grafana/loki/releases/download/v2.9.1/loki-linux-amd64.zip
unzip loki-linux-amd64.zip
./loki-linux-amd64 --config.file=./loki-config.yml
nohup ./loki-linux-amd64 -config.file=./loki-config.yaml 2>&1 &

# --
auth_enabled: false

server:
  http_listen_port: 3100
  grpc_listen_port: 9096

common:
  instance_addr: 0.0.0.0
  path_prefix: ./tmp/loki
  storage:
    filesystem:
      chunks_directory: ./tmp/loki/chunks
      rules_directory: ./tmp/loki/rules
  replication_factor: 1
  ring:
    kvstore:
      store: inmemory

query_range:
  results_cache:
    cache:
      embedded_cache:
        enabled: true
        max_size_mb: 100

schema_config:
  configs:
    - from: 2020-10-24
      store: boltdb-shipper
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 24h

ruler:
  alertmanager_url: http://localhost:9093

limits_config:
    enforce_metric_name: false
    ingestion_burst_size_mb: 20
    ingestion_rate_mb: 200
    ingestion_rate_strategy: global
    max_cache_freshness_per_query: 10m
    max_global_streams_per_user: 10000
    max_query_length: 12000h
    max_query_parallelism: 16
    max_streams_per_user: 0
    max_entries_limit_per_query: 1000000
    reject_old_samples: true
    reject_old_samples_max_age: 168h
# --
```
- Pushing Logs to Loki Without Using Promtail (https://medium.com/geekculture/pushing-logs-to-loki-without-using-promtail-fc31dfdde3c6, https://github.com/sleleko/devops-kb/blob/master/python/push-to-loki.py)
- Pushing Logs to Loki Without Using Promtail (https://medium.com/geekculture/pushing-logs-to-loki-without-using-promtail-fc31dfdde3c6, https://github.com/sleleko/devops-kb/blob/master/python/push-to-loki.py)
- Pushing Logs to Loki with "python-logging-loki"
- Push logs to Grafana-loki(`./Grafana-log/push_to_loki.sh`) via REST API (https://github.com/euiyounghwang/Prometheus-Grafana-Loki-API-Service)
- Grafana Dashboard : `sum(count_over_time({service=~"prometheus-monitoring-service|prometheus-grafana-loki-logging-service|prometheus-alert-service"}[$__interval]))`, `{service=~"prometheus-grafana-loki-logging-service", env=~"$Kafka_Data_Source_Env"}`
```bash
pip install python-logging-loki

import logging
import logging_loki
logging_loki.emitter.LokiEmitter.level_tag = "level"
# assign to a variable named handler 
handler = logging_loki.LokiHandler(
   url="http://loki:3100/loki/api/v1/push",
   version="1",
)
# create a new logger instance, name it whatever you want
logger = logging.getLogger("my-logger")
logger.addHandler(handler)

# now use the logging object's functions as you normally would
logger.error(
   "Something bad happened",
  
   extra={"tags": {"service": "my-service"}},
)
logger.warning(
   "Something bad happened but we can keep going",
   extra={"tags": {"service": "my-service"}},
)
# extra={"tags": {"service": "my-service", "one": "more thing"}}
```

- Grafana Promtail Setup
```bash
wget https://github.com/grafana/loki/releases/download/v2.8.0/promtail-linux-amd64.zip
unzip promtail-linux-amd64.zip
nohup ./promtail-linux-amd64 -config.file=promtail-config.yaml 2>&1 &
- How to use : https://kbcoding.tistory.com/122
# --
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
- job_name: logging
  static_configs:
  - targets:
      - localhost
    labels:
      job: logging
      __path__: /logs/*.log
# --
```
- Promtail Format

![Alt text](./architecture/LOKI_FORMAT.PNG)



### Installation
```bash
pip install prometheus-client
```


### POST JSON
- POST Json payload command
```bash
curl -X 'POST' \
  'https://localhost/triggers' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Basic test=' \
  -d '{
   "recipients": "TEST app",
   "summary": "[TEST] Prometheus Monitoring Alert",
   "description": "The alert is a message for testing",
   "priority": "MEDIUM"
}'
```


### Custom Promethues Exporter
- Expose my metrics for dev kafka cluster to http://localhost:9115
- Expose ES cluster/Kafka/Kibana/Logstash metrics by using this exporter based on ES API/socket library
- EXpose DB records as metrics from `DB-Interface-Export API` with HTTP POST Method
- Interface with `DB Interface Export` (https://github.com/euiyounghwang/DB-Interface-Export) by using FastAPI Framework to get the records as metrics from the specific databse
```bash
# HELP python_gc_objects_collected_total Objects collected during gc
# TYPE python_gc_objects_collected_total counter
python_gc_objects_collected_total{generation="0"} 302.0
python_gc_objects_collected_total{generation="1"} 342.0
python_gc_objects_collected_total{generation="2"} 0.0
...
kafka_health_metric{server_job="localhost"} 3.0
# HELP kafka_connect_nodes_metric Metrics scraped from localhost
# TYPE kafka_connect_nodes_metric gauge
kafka_connect_nodes_metric{server_job="localhost"} 3.0
# HELP kafka_connect_listeners_metric Metrics scraped from localhost
# TYPE kafka_connect_listeners_metric gauge
kafka_connect_listeners_metric{host="localhost",name="test_jdbc",running="RUNNING",server_job="localhost"} 1.0
# HELP zookeeper_health_metric Metrics scraped from localhost
# TYPE zookeeper_health_metric gauge
zookeeper_health_metric{server_job="localhost"} 3.0
# HELP kibana_health_metric Metrics scraped from localhost
# TYPE kibana_health_metric gauge
kibana_health_metric{server_job="localhost"} 1.0
# HELP logstash_health_metric Metrics scraped from localhost
# TYPE logstash_health_metric gauge
logstash_health_metric{server_job="localhost"} 1.0
...
```


### Run Custom Promethues Exporter
- Run this command : $ `python ./standalone-es-service-export.py` or `./standalone-export-run.sh`
```bash

#-- HTTP Server/Client Based
# HTTP Server
$  ./es-service-all-server-export-run.sh status/start/stop or ./server-export-run.sh
Server started.

# Client export
$  ./es-service-all-client-export-run.sh status/start/stop or ./client-export-run.sh

# Client only
./standalone-es-service-export.sh status/start/stop

...
[2024-05-20 20:44:06] [INFO] [prometheus_client_export] [work] http://localhost:9999/health?kafka_url=localhost:9092,localhost:9092,localhost:9092&es_url=localhost:9200,localhost:9200,localhost:9200,localhost:9200&kibana_url=localhost:5601&logstash_url=process
[2024-05-20 20:44:06] [INFO] [prometheus_client_export] [get_metrics_all_envs] 200
[2024-05-20 20:44:06] [INFO] [prometheus_client_export] [get_metrics_all_envs] <Response [200]>
[2024-05-20 20:44:06] [INFO] [prometheus_client_export] [get_metrics_all_envs] {'kafka_url': {'localhost:9092': 'OK', 'GREEN_CNT': 3, 'localhost:9092': 'OK', 'localhost:9092': 'OK'}, 'es_url': {'localhost:9200': 'OK', 'GREEN_CNT': 4, 'localhost:9200': 'OK', 'localhost:9200': 'OK', 'localhost:9200': 'OK'}, 'kibana_url': {'localhost:5601': 'OK', 'GREEN_CNT': 1}, 'logstash_url': 1}
...
```


### Create script with arguments with python
- Run this command : euiyoung.hwang@US-5CD4021CL1-L MINGW64 ~/Git_Workspace/python-prometheus-export/create-script (master) $ `python ./create-script-by-hosts.py`
```bash
euiyoung.hwang@US-5CD4021CL1-L MINGW64 ~/Git_Workspace/python-prometheus-export/create-script (master)
$ python ./create-script-by-hosts.py
2024-05-31 19:58:16,573 : INFO : {
  "dev": {
    "kibana": "kibana:5601",
    "es_url": [
      "es1:9200",
      "es2:9200",
      "es3:9200",
      "es4:9200"
    ],
    "kafka_url": [
      "data1:9092",
      "data2:9092",
      "data3:9092"
    ],
    "kafka_connect_url": [
      "data1:8083",
      "data2:8083",
      "data3:8083"
    ],
    "zookeeper_url": [
      "data1:2181",
      "data2:2181",
      "data3:2181"
    ]
  },
  "localhost": {
    "kafka_url": [
      "data11:9092",
      "data21:9092",
      "data31:9092"
    ],
    "kafka_connect_url": [
      "data11:8083",
      "data21:8083",
      "data31:8083"
    ],
    "zookeeper_url": [
      "data11:2181",
      "data21:2181",
      "data31:2181"
    ],
    "kibana": "kibana1:5601",
    "es_url": [
      "es11:9200",
      "es21:9200",
      "es31:9200",
      "es41:9200",
      "es51:9200"
    ]
  }
}


# dev ENV
python ./standalone-es-service-export.py --interface http --db_http_host localhost:8002 --url jdbc:oracle:thin:bi"$"reporting/None --db_run false --kafka_url data1:9092,data2:9092,data3:9092 --kafka_connect_url data1:8083,data2:8083,data3:8083 --zookeeper_url  data1:2181,data2:2181,data3:2181 --es_url es1:9200,es2:9200,es3:9200,es4:9200 --kibana_url kibana:5601 --interval 30 --sql "SELECT * FROM TEST*"


# localhost ENV
python ./standalone-es-service-export.py --interface http --db_http_host localhost:8002 --url jdbc:oracle:thin:bi"$"reporting/None --db_run false --kafka_url data11:9092,data21:9092,data31:9092 --kafka_connect_url data11:8083,data21:8083,data31:8083 --zookeeper_url  data11:2181,data21:2181,data31:2181 --es_url es11:9200,es21:9200,es31:9200,es41:9200,es51:9200 --kibana_url kibana1:5601 --interval 30 --sql "SELECT * FROM TEST*"
```


### Service Maintance
- Kafka Service
```bash
 /apps/kafka_2.11-0.11.0.0/bin/kafka-topics.sh --describe --zookeeper localhost.am.co.gxo.com:2181,localhost.am.co.gxo.com:2181,localhost.am.co.gxo.com:2181 --topic ELASTIC_PIPELINE_QUEUE

./test_jdbc.json
{
  "name": "test_jdbc",
  "config": {
    "connector.class": "io.confluent.connect.jdbc.JdbcSourceConnector",
    "timestamp.column.name": "ADDTS",
    "tasks.max": "1",
    "transforms.InsertKey.fields": "SRC_TBL_KEY",
    "transforms": "InsertKey,ExtractId",
    "batch.max.rows": "5000",
    "timestamp.delay.interval.ms": "1000",
    "table.types": "TABLE",
    "transforms.ExtractId.field": "SRC_TBL_KEY",
    "query": "select * from (SELECT * FROM test_schema.test_VM where status = 'N')",
    "mode": "timestamp",
    "topic.prefix": "TEST_QUEUE",
    "poll.interval.ms": "1000",
    "schema.pattern":"bi$reporting",
    "connection.backoff.ms":"60000",
    "connection.attempts":"10",
    "connection.pool.size": "5",
    "connection.url": "jdbc:oracle:thin:test/testw@localhost:1234/testdb",
    "transforms.InsertKey.type": "org.apache.kafka.connect.transforms.ValueToKey",
    "transforms.ExtractId.type": "org.apache.kafka.connect.transforms.ExtractField$Key"
  }
}


curl -XGET  'localhost:8083/connectors/test_jdbc/status' | jq
curl -XDELETE  'localhost:8083/connectors/test_jdbc' | jq
curl -X POST http://localhost:8083/connectors/test_jdbc/tasks/0/restart
curl -XPOST -H 'Content-type:application/json'   'localhost:8083/connectors' --data @./test_jdbc.json
curl -XPUT 'localhost:8083/connectors/test_jdbc/resume'

```


### Services
- Reference : https://whiteklay.com/kafka/
- What Is Kafka Connect
Kafka Connect is a framework which connects Kafka with external Systems. It helps to move the data in and out of the Kafka. Connect makes it simple to use existing connector.
Kafka Connect helps use to perform Extract (E) and Transform(T) of ETL Process. Connect contains the set of connectors which allows to import and export the data. 

Cconfiguration for common source and sink Connectors. Connectors comes in two flavors:

- Source Connector
Source Connector imports data from other System to Kafka Topic. For eg; Source Connector can ingest entire databases and stream table updates to Kafka topics.

- Sink Connector
Sink Connector exports data from Kafka topic to other Systems. For eg; Sink Connector can deliver data from Kafka topic to an HDFS File.

```bash

a.json
{
  "name": "a_jdbc",
  "config": {
    "connector.class": "io.confluent.connect.jdbc.JdbcSourceConnector",
    "timestamp.column.name": "ADDTS",
    "tasks.max": "1",
    "transforms.InsertKey.fields": "P_KEY",
    "transforms": "InsertKey,ExtractId",
    "batch.max.rows": "5000",
    "timestamp.delay.interval.ms": "1000",
    "table.types": "TABLE",
    "transforms.ExtractId.field": "P_KEY",
    "query": "select * from (SELECT * FROM user_schema.A_QUEUE_VW where status = 'N')",
    "mode": "timestamp",
    "topic.prefix": "A_QUEUE",
    "poll.interval.ms": "1000",
    "schema.pattern":"user_schema",
    "connection.backoff.ms":"60000",
    "connection.attempts":"10",
    "connection.pool.size": "5",
    "connection.url": "jdbc:oracle:thin:test/testt@localhost:1234/localhost.sid",
    "transforms.InsertKey.type": "org.apache.kafka.connect.transforms.ValueToKey",
    "transforms.ExtractId.type": "org.apache.kafka.connect.transforms.ExtractField$Key"
    }
}

sudo netstat -nlp | grep :8083
/apps/kafka_2.11-0.11.0.0/bin/kafka-topics.sh --list  --zookeeper  localhost1:2181,localhost2:2181,localhost3:2181
/apps/kafka_2.11-0.11.0.0/bin/kafka-topics.sh --describe  --zookeeper localhost1:2181,localhost2:2181,localhost3:2181 --topic A_QUEUE

/apps/kafka_2.11-0.11.0.0/bin/kafka-topics.sh --delete  --zookeeper localhost1:2181,localhost2:2181,localhost3:2181  --topic connect-configs
/apps/kafka_2.11-0.11.0.0/bin/kafka-topics.sh --delete  --zookeeper localhost1:2181,localhost2:2181,localhost3:2181  --topic connect-offsets
/apps/kafka_2.11-0.11.0.0/bin/kafka-topics.sh --delete  --zookeeper localhost1:2181,localhost2:2181,localhost3:2181  --topic connect-status
/apps/kafka_2.11-0.11.0.0/bin/kafka-topics.sh --list  --zookeeper  localhost1:2181,localhost2:2181,localhost3:2181

/apps/kafka_2.11-0.11.0.0/bin/kafka-topics.sh --create --zookeeper localhost1:2181,localhost2:2181,localhost3:2181 --topic connect-configs --replication-factor 3 --partitions 3 --config cleanup.policy=compact
/apps/kafka_2.11-0.11.0.0/bin/kafka-topics.sh --create --zookeeper localhost1:2181,localhost2:2181,localhost3:2181 --topic connect-offsets --replication-factor 3 --partitions 10 --config cleanup.policy=compact
/apps/kafka_2.11-0.11.0.0/bin/kafka-topics.sh --create --zookeeper localhost1:2181,localhost2:2181,localhost3:2181 --topic connect-status --replication-factor 3 --partitions 10 --config cleanup.policy=compact
/apps/kafka_2.11-0.11.0.0/bin/kafka-topics.sh --list  --zookeeper  localhost1:2181,localhost2:2181,localhost3:2181
/apps/kafka_2.11-0.11.0.0/bin/kafka-topics.sh --describe  --zookeeper localhost1:2181,localhost2:2181,localhost3:2181 --topic A_QUEUE

curl -XGET  'localhost:8083/connectors/' | jq
curl -XPOST -H 'Content-type:application/json'   'localhost1:8083/connectors' --data @./a.json

/apps/kafka_2.11-0.11.0.0/bin/kafka-topics.sh --list  --zookeeper localhost1:2181,localhost2:2181,localhost3:2181
/apps/kafka_2.11-0.11.0.0/bin/kafka-run-class.sh kafka.tools.GetOffsetShell --topic A_QUEUE--broker-list localhost1:9092,localhost2:9092,localhost3:9092

curl -XGET  'localhost:8083/connectors/' | jq
curl -XGET  'localhost:8083/connectors/a_jdbc/status' | jq

curl -XDELETE  'localhost:8083/connectors/a_jdbc' | jq
curl -XPOST -H 'Content-type:application/json'   'localhost:8083/connectors' --data @./a.json
curl -XPOST 'localhost:8083/connectors/a_jdbc/tasks/0/restart' | jq

curl -XDELETE  'localhost:8083/connectors/b_jdbc' | jq
curl -XPOST -H 'Content-type:application/json'   'localhost:8083/connectors' --data @./b.json
```



### H2 Database for log
H2 is an open source Java SQL Database. It can be run in both embedded and server mode. It is widely used as an In-memory database. In-memory database relies on system memory as oppose to disk space for storage of data. Because memory access is faster than disk access.

H2, the Java SQL database. The main features of H2(https://www.h2database.com/html/main.html) are:
- Very fast, open source, JDBC API
- Embedded and server modes; in-memory databases
- Browser based Console application
- Small footprint: around 2.5 MB jar file size
```bash
- H2 Database is running with JDK 11 (http://localhost:8082/)
  - Server Mode
  - Embedded Mode
  - In-Memory Mode

sudo netstat -nlp | grep :8082

# h2.sh
# --
#!/bin/sh

JAVA_HOME='/home/devuser/monitoring/openlogic-openjdk-11.0.23+9-linux-x64'
export PATH=$JAVA_HOME/bin:$PATH
export JAVA_HOME
echo $PATH

dir=$(dirname "$0")
java -cp "$dir/h2-2.3.232.jar:$H2DRIVERS:$CLASSPATH" org.h2.tools.Console "$@"

# --
# start.sh
--
#!/bin/bash
set -e
SCRIPTDIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

# Web/TCP
nohup $SCRIPTDIR/h2.sh -webAllowOthers -tcp -tcpAllowOthers -tcpPort 9092 &> /dev/null &
#nohup $SCRIPTDIR/h2.sh -webExternalNames localhost -webAllowOthers -tcp -tcpAllowOthers -tcpPort 9092 &> /dev/null &

''' http://localhost:8082/ '''
#- Embedded (Delete all when stopping the service)
jdbc:h2:~/monitoring/h2/data/monitoring
jdbc:h2:tcp://localhost/~/monitoring/h2/data/tcp_monitoring
--

create db file like vi 'test.mv.db'
ALTER USER SA SET PASSWORD 'test'

DROP TABLE MONITORING_LOG;
DROP TABLE ALERT;

# ACTIVE CHAR(1) DEFAULT 'Y' NOT NULL
#CREATE TABLE ALERT(ID INT PRIMARY KEY AUTO_INCREMENT, ENV_NAME VARCHAR(255) NOT NULL, IS_MAILING VARCHAR(255) NULL, IP_ADDRESS VARCHAR(20) NOT NULL, LOG TEXT NULL, CREATE_DATE DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL);

#CREATE TABLE MONITORING_LOG(ID INT PRIMARY KEY AUTO_INCREMENT, ENV_NAME VARCHAR(255) NOT NULL, HOST_NAME VARCHAR(20) NOT NULL, STATUS VARCHAR(20) NOT NULL, LOG TEXT NULL, CREATE_DATE DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL);

CREATE TABLE ALERT(ENV_NAME VARCHAR(255) NOT NULL, IS_MAILING VARCHAR(255) NULL, IP_ADDRESS VARCHAR(20) NOT NULL, LOG TEXT NULL, CREATE_DATE DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL);

CREATE TABLE MONITORING_LOG(ENV_NAME VARCHAR(255) NOT NULL, HOST_NAME VARCHAR(20) NOT NULL, STATUS VARCHAR(100) NOT NULL, IP VARCHAR(20) NOT NULL, LOG TEXT NULL, CREATE_DATE DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL);

#- INSERT SAMPLE
INSERT INTO ALERT (ENV_NAME, IS_MAILING, IP_ADDRESS, LOG) VALUES('DEV', 'TRUE', '127.0.0.1', 'TEST MESSAGE');
INSERT INTO MONITORING_LOG (ENV_NAME, HOST_NAME, STATUS, IP, LOG) VALUES('DEV', 'localhost', 'ES_RESTARTED', '127.0.0.1', 'TEST MESSAGE');
INSERT INTO MONITORING_LOG (ENV_NAME, HOST_NAME, STATUS, IP, LOG) VALUES('DEV',  'localhost', 'ES_RESET_REPLICA', '127.0.0.1', 'TEST MESSAGE');

#- SELECT
SELECT * FROM ALERT;
SELECT * FROM MONITORING_LOG;

DELETE FROM ALERT WHERE CREATE_DATE < CURRENT_TIMESTAMP() - 7;

SELECT ROWNUM, ENV_NAME,  IS_MAILING, IP_ADDRESS, LOG, CREATE_DATE FROM ALERT 
WHERE CREATE_DATE >= CURRENT_TIMESTAMP- 7
ORDER BY CREATE_DATE DESC;

SELECT ROWNUM, CREATE_DATE, ENV_NAME, HOST_NAME, STATUS, IP, LOG FROM MONITORING_LOG 
WHERE CREATE_DATE >= CURRENT_TIMESTAMP- 7
ORDER BY CREATE_DATE DESC;
```


### Heroku with Kaffeine
- Heroku is an AI platform as a service (AI PaaS) that enables developers to build, run, and scale applications entirely in the cloud.
- Reference : https://jnarin-development-story.tistory.com/163


### xMatters
- Matters service reliability platform helps DevOps, SREs, and Ops teams.
- xMatters is a service reliability platform used for incident management, specifically designed to automate workflows, ensure infrastructure and application reliability, and accelerate incident resolution. It helps teams respond to and resolve IT issues faster by automating communications, orchestrating workflows, and providing real-time insights. 
- Trigger Alerts by Webhook (https://help.xmatters.com/integrations/other/triggeralertsbywebhook.htm) : The Trigger Alerts by Webhook workflow is a pre-built workflow template designed to help you start notifying users and groups with minimal setup. It lets you create an alert and send notifications by simply sending an HTTP request to xMatters from any application capable of sending a webhook.

### Push Alert
- Gotify (https://gotify.net/) : Gotify is a self-hosted push notification service created for sending and receiving messages in real time. 



### Auto Start Script

```bash

sudo vi /etc/systemd/system/rc-local.service

--
[Unit]
 Description=/etc/rc.local Compatibility
 ConditionPathExists=/etc/rc.local

[Service]
 Type=forking
 ExecStart=/etc/rc.local start
 TimeoutSec=0
 StandardOutput=tty
 RemainAfterExit=yes
 SysVStartPriority=99

[Install]
 WantedBy=multi-user.target
--

sudo vi /etc/rc.d/rc.local
# /home/test/test/test-run.sh start

# sudo systemctl disable rc-local

sudo chmod 755 /etc/rc.local && sudo systemctl enable rc-local

# stop the service all
sudo systemctl status rc-local.service
sudo systemctl start rc-local.service

sudo service rc-local stop
sudo service rc-local status
sudo service rc-local start

# enable check
systemctl list-unit-files |grep rc.local

sudo service rc-local restart
sudo service rc-local status
sudo systemctl disable rc-local
```



### Register Service (SSH Web Server)
- Running this service that allows us to excute the command to start/stop the service
- sudo service es_ssh_monitoring_api status/stop/start/restart
```bash
#-- /etc/systemd/system/es_ssh_monitoring_api.service
[Unit]
Description=ES SSH Service

[Service]
User=devuser
Group=devuser
Type=simple
ExecStart=/bin/bash /home/devuser/es_ssh_monitoring_api/ssh_client_web.sh.sh
ExecStop= /usr/bin/killall /es_ssh_monitoring_api

[Install]
WantedBy=default.target


# Service command
sudo systemctl daemon-reload 
sudo systemctl enable es_ssh_monitoring_api.service
sudo systemctl start es_ssh_monitoring_api.service 
sudo systemctl status es_ssh_monitoring_api.service 
sudo systemctl stop es_ssh_monitoring_api.service 

sudo service es_ssh_monitoring_api status/stop/start
```

## Cronjob
- A cron job is a scheduled task in a Unix-like operating system that runs automatically at a specific time or interval, typically for repetitive system or application maintenance, like running scripts, performing backups, or sending out newsletters.

```bash

* * * * * <command_to_run>
- - - - -
| | | | |
| | | | +----- Day of the week (0-6) (Sunday is 0 or 7)
| | | +------- Month (1-12)
| | +--------- Day of the month (1-31)
| +----------- Hour (0-23)
+------------- Minute (0-59)


### ------
### alert update via this script and send to the REST API
### 1 : Monday
40 07 * * 1 /apps/rest_api/es_config_interface/scripts/alert_job_batch.sh localhost dev false
30 15 * * 1 /apps_rest_api/es_config_interface/scripts/alert_job_batch.sh localhost dev true

### Monday ~ Thursday
30 06 16 09 * /apps/rest_api/es_config_interface/scripts/alert_job_batch.sh localhost dev false
30 16 16 09 * /apps/rest_api/es_config_interface/scripts/alert_job_batch.sh localhost dev true

### Friday
40 22 19 09 5 /apps/rest_api/es_config_interface/scripts/alert_job_batch.sh localhost dev false
30 07 20 09 5 /apps/rest_api/es_config_interface/scripts/alert_job_batch.sh localhost dev true

### Saturday
40 22 20 09 6 /apps/rest_api/es_config_interface/scripts/alert_job_batch.sh localhost dev false
30 07 21 09 6 /apps/rest_api/es_config_interface/scripts/alert_job_batch.sh localhost dev true

### Sunday
00 16 21 09 0 /apps/rest_api/es_config_interface/scripts/alert_job_batch.sh localhost dev false
30 05 22 09 0 /apps/rest_api/es_config_interface/scripts/alert_job_batch.sh localhost dev true
```

### Jar file rebuild 
- Jar file
```bash
vi ~/.bashrc

#export JAVA_HOME=/apps/storage/ELK_UPGRADE/java-17-openjdk-17.0.14.0.7-1.portable.jdk.el.x86_64
#export PATH=$JAVA_HOME/bin:$PATH
#echo $JAVA_HOME

source ~/.bashrc
jar -xvf ./streamprocess_omx.jar

jar cf ./streamprocess_omx.jar .
mv ./streamprocess_omx.jar ../
```
