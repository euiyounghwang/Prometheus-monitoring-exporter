### Guide
```
https://github.com/prometheus-community/elasticsearch_exporter
https://blog.naver.com/PostView.naver?blogId=whddbsml&logNo=222405287424
https://github.com/prometheus-community/elasticsearch_exporter/releases
```

### Docker Version
```
  elasticsearch_exporter:
    # http://localhost:9200/_prometheus/metrics
    # http://localhost:9210/_prometheus/metrics
    image: justwatch/elasticsearch_exporter:1.1.0
    container_name: elasticsearch_exporter
    depends_on:
      - prometheus
    command:
     - '--es.uri=http://elastic:1@host.docker.internal:9200'
     - '--es.all'
     - '--es.snapshots'
     - '--es.indices'
    restart: always
    ports:
    - "9115:9114"
```


### Download and unpack
```
wget https://github.com/prometheus-community/elasticsearch_exporter/releases/download/v1.6.0/elasticsearch_exporter-1.6.0.linux-amd64.tar.gz
tar -xzvf elasticsearch_exporter-1.2.0.linux-amd64.tar.gz

devuser@ubuntu-master-1:~/ES$ tar -zxvf elasticsearch_exporter-1.6.0.linux-amd64.tar.gz
elasticsearch_exporter-1.6.0.linux-amd64/
elasticsearch_exporter-1.6.0.linux-amd64/CHANGELOG.md
elasticsearch_exporter-1.6.0.linux-amd64/elasticsearch.rules
elasticsearch_exporter-1.6.0.linux-amd64/dashboard.json
elasticsearch_exporter-1.6.0.linux-amd64/deployment.yml
elasticsearch_exporter-1.6.0.linux-amd64/elasticsearch_exporter
elasticsearch_exporter-1.6.0.linux-amd64/README.md
elasticsearch_exporter-1.6.0.linux-amd64/LICENSE

cd elasticsearch_exporter-1.2.0.linux-amd64
sudo cp elasticsearch_exporter /usr/local/bin/elasticsearch_exporter
sudo chown devuser /usr/local/bin/elasticsearch_exporter
 ```
 
 
### Test configuration file
```
/usr/local/bin/elasticsearch_exporter --es.uri=http://elastic:gsaadmin@localhost:9200 --es.all --es.indices --es.timeout 20s --es.snapshots
```

### Register the service for elastic_exporter systemd 
```
sudo vi /etc/systemd/system/elastic_exporter.service

[Unit]
Description=Prometheus elasticsearch_exporter
After=local-fs.target network-online.target network.target
Wants=local-fs.target network-online.target network.target

[Service]
User=devuser
Group=devuser
Type=simple
WorkingDirectory=/home/devuser/ES/elasticsearch_exporter-1.6.0.linux-amd64
ExecStart=/home/devuser/ES/elasticsearch_exporter-1.6.0.linux-amd64/elasticsearch_exporter --es.uri=http://elastic:1@localhost:9200 --es.all --es.indices --es.timeout 20s --es.snapshots
ExecStop= /usr/bin/killall elasticsearch_exporter

[Install]
WantedBy=default.target

# Run service
systemctl daemon-reload
# Autostart when rebooting
sudo systemctl enable elastic_exporter.service
systemctl start elastic_exporter
```
 
 
### Grafana Log
```
devuser@ubuntu-master-1:~/ES/elasticsearch_exporter-1.6.0.linux-amd64$ systemctl status elastic_exporter.service
● elastic_exporter.service - Prometheus elasticsearch_exporter
     Loaded: loaded (/etc/systemd/system/elastic_exporter.service; enabled; vendor preset: enabled)
     Active: active (running) since Thu 2023-09-28 21:38:36 CDT; 7s ago
   Main PID: 179529 (elasticsearch_e)
      Tasks: 11 (limit: 976)
     Memory: 21.9M
        CPU: 236ms
     CGroup: /system.slice/elastic_exporter.service
             └─179529 /usr/libexec/qemu-binfmt/x86_64-binfmt-P /home/devuser/ES/elasticsearch_exporter-1.6.0.linux-amd64/elasticsearch_exporter /home/devuser/ES/elasticsearch_>

Sep 28 21:38:36 ubuntu-master-1 systemd[1]: Started Prometheus elasticsearch_exporter.
Sep 28 21:38:36 ubuntu-master-1 elasticsearch_exporter[179529]: level=info ts=2023-09-29T02:38:36.825669058Z caller=clusterinfo.go:214 msg="triggering initial cluster info cal>
Sep 28 21:38:36 ubuntu-master-1 elasticsearch_exporter[179529]: level=info ts=2023-09-29T02:38:36.830529548Z caller=clusterinfo.go:183 msg="providing consumers with updated cl>
Sep 28 21:38:36 ubuntu-master-1 elasticsearch_exporter[179529]: level=info ts=2023-09-29T02:38:36.874496922Z caller=main.go:246 msg="started cluster info retriever" interval=5>
Sep 28 21:38:36 ubuntu-master-1 elasticsearch_exporter[179529]: level=info ts=2023-09-29T02:38:36.884466491Z caller=tls_config.go:274 msg="Listening on" address=[::]:9114
Sep 28 21:38:36 ubuntu-master-1 elasticsearch_exporter[179529]: level=info ts=2023-09-29T02:38:36.884649579Z caller=tls_config.go:277 msg="TLS is disabled." http2=false addres>
lines 1-16/16 (END)
```
 
 ### Run
```
http://localhost:9114/metrics
```