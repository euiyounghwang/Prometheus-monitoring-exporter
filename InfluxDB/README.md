
# Influx-DB
<i>Influx-DB

InfluxDB(https://docs.influxdata.com/influxdb/v2/install/?t=Linux#manually-download-and-install-the-influxd-binary) is a time series database (TSDB) developed by the company InfluxData. It is used for storage and retrieval of time series data in fields such as operations monitoring, application metrics, Internet of Things sensor data, and real-time analytics.

InfluxDB is a push-based system. It requires an application to actively push data into InfluxDB. Prometheus is a pull-based system. An application publishes the metrics at a given endpoint, and Prometheus fetches them periodically.

- Telegraf Download: Telegraf is written in Go and compiles into a single binary with no external dependencies, requiring a minimal memory footprint. It can easily collect and send metrics and events from databases, systems, and IoT sensors. 
```bash
wget https://dl.influxdata.com/telegraf/releases/telegraf-1.34.2_linux_amd64.tar.gz
tar xf telegraf-1.34.2_linux_amd64.tar.gz
```
1. Install the Latest Telegraf
You can install the latest Telegraf by visiting the InfluxData Downloads page(https://www.influxdata.com/downloads/). If you already have Telegraf installed on your system, make sure it's up to date. You will need version 1.9.2 or higher.
    - Telegraf GitHub : https://github.com/influxdata/telegraf?tab=readme-ov-file

2. Configure your API Token
Your API token is required for pushing data into InfluxDB. You can copy the following command to your terminal window to set an environment variable with your API token.
    - Prometheus-monitoring-exporter Github : INFLUX_DB_API_TOKEN for this token
    - export INFLUX_TOKEN=<INFLUX_TOKEN>

Input plugins are responsible for collecting data. You can use different input plugins to get data from different sources. Below is an example of an input plugin that collects CPU metrics.(https://betwe.tistory.com/entry/Linux-Telegraf-%EC%84%A4%EC%B9%98-%EB%B0%8F-%EB%8B%A4%EC%96%91%ED%95%9C-%EC%98%88%EC%A0%9C)

```bash
[[inputs.cpu]]
  percpu = true
  totalcpu = true
  collect_cpu_time = false
```

Filter plugins are used to transform or modify input data. You can use filters to process data and extract only the information you need. Below is an example of a filter plugin that changes field names.
```bash
[[processors.rename]]
  [[processors.rename.replace]]
    field = "old_field_name"
    dest = "new_field_name"
```

Output plugins are responsible for storing collected data or sending it to other systems. Below is an example of an output plugin that sends data to InfluxDB
```bash
[[outputs.influxdb]]
  urls = ["http://localhost:8086"]
  database = "mydb
```

Update Bucket such as retention period and others: https://docs.influxdata.com/influxdb/v2/admin/buckets/update-bucket/

3. Start Telegraf
Telegraf is an agent written in Go for collecting metrics and writing them into InfluxDB. Finally, you can run the following command to start the Telegraf agent running on your machine.
    
telegraf --config https://localhost:8086/api/v2/telegrafs/0ebbdc1f95098000

```bash
[[outputs.http]]
    url = "http://127.0.0.1:8080/telegraf"
    timeout = "5s"
    method = "POST"
    data_format = "json"

    [outputs.http.headers]
      Content-Type = "application/json"
```
telegraf option to run (https://yundevnote.tistory.com/80)
- telegraf --config /path/to/telegraf.conf
- telegraf --config-directory /path/to/config-directory
- telegraf --config /path/to/telegraf.conf --test
- telegraf --debug
- telegraf --config /path/to/telegraf.conf --once
- telegraf --config /path/to/telegraf.conf --watch-config

- telegraf --config telegraf.conf


- Gafana : Telegraf System Dashboard (https://grafana.com/grafana/dashboards/928-telegraf-system-dashboard/), Grafana Datasource/Create Graph with Flux Query (https://docs.influxdata.com/influxdb/v2/query-data/get-started/query-influxdb/)
```bash
from(bucket:"ES")
 |> range(start: -15m)
    |> filter(fn: (r) => r._measurement == "cpu")

from(bucket:"ES")
 |> range(start: -15m)
    |> filter(fn: (r) => r._measurement == "system" and r._field == "load1")
```

- Docker build
```bash
docker search influxdb
docker pull influxdb
docker network create influxdb
docker run -d --net=influxdb --name=grafana -p 3000:3000 grafana/grafana
docker run -d --net=influxdb --name=influxdb -p 8086:8086 influxdb
docker run -p 8086:8086 \
      -v influxdb:/var/lib/influxdb \
      -e DOCKER_INFLUXDB_INIT_MODE=upgrade \
      -e DOCKER_INFLUXDB_INIT_USERNAME=my-user \        — 사용할 ID
      -e DOCKER_INFLUXDB_INIT_PASSWORD=my-password \    — 사용할 PW
      -e DOCKER_INFLUXDB_INIT_ORG=my-org \            — 사용할 조직명
      -e DOCKER_INFLUXDB_INIT_BUCKET=my-bucket \  — 초기 생성할 버킷명
      influxdb
docker exec -it influxdb /bin/bash

docker run -d -p 8086:8086 --name influxdb2 -v /tmp/influxdb2:/var/lib/influxdb2 influxdb:2.0
docker stop influxdb2
docker run -d -p 8086:8086 --name influxdb -v /tmp/influxdb2:/var/lib/influxdb2 influxdb:latest
docker run -d --name=telegraf -v [download_file]:/etc/telegraf/telegraf.conf:ro telegraf
docker logs telegraf -f
```

Metricbeat is designed for Elasticsearch, while Telegraf is mainly used with Influxdb. The decision between the two is more of a decision between the Elastic stack and the TICK stack.

If you have the requirment, or might have in the future, to also collect logs and tracing data besides metrics, then the Elastic stack and Metricbeat are IMO a better choice, because the TICK stack(Telegraf, InfluxDB, Chronograf, Kapacitor) is focused only on metrics.