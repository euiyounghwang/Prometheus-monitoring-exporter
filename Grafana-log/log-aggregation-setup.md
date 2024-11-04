# Log Aggregaation
<i>Log Aggregaation

Currently, Grafana (v.10.x) that we are using does not support ES v.5 to access and add a new data source, so I found a possible Grafana version that can connect with ES v.5 and additionally set up a lower version (v.8.0.0) of Grafana for text logs. This version of Grafana provide users to add ES v.5 as a data source to get data from the index.

So, I am proceeding with the following steps:

- Filebeat to read the logs
    - Rather than sending all lines to logstash using Filebeat, I thought it would be better to send only ERROR log lines regarding to "Spark apps". So I am implementing python-based agent to send only ERROR logs) instead of Filebeat    <Doing>
    - The Python script continuously reads the last line of the log file in real time. It also takes multiple log file names as parameters and reads error log lines from multiple log files. And then It passes them to logstash.
- Ship to logstash ("Python-based agent" transmit only 'ERROR' logs to logstash)
    - Use grok filter from the ERROR line to create json format  <Doing>
- Ingest "Error logs" into Elasticsearch (Dev) and create indices ("logstash-logger-yyyy-mm-dd"). 
- In Grafana, Create a dashboard that displays text logs. <Will>


To save spark text log, we need to pass it to filebeat-logstash-es cluster. However, if we pass all lines in the spark log or archive log files to logstash using filebeat, a lot of traffic will be generated.
So, instead of filebeat, I implemented a python script as agent to read only error logs and pass them to logstash.
- `./Grafana-log/push_to_logstash.sh start` (This script will be run as agent to send text logs to logstash using TCP socket)
- Then, The Grafana dashboard(Variable with "All" Options: https://stackoverflow.com/questions/72316944/grafana-variable-return-all-elastic-documents-when-selecting-all-and-the-attr, sample : * OR (NOT _exists_:provision_org.keyword)) will read the ES log index in ES cluster and show ERROR logs in near real time.


#### Setup/Run Logstash-Agent/Filebeat
- Run the script : `./Grafana-log/push_to_logstash.sh start` or `python $LOGGING_SERVICE_ALL_EXPORT_PATH/push_to_logstash_script.py --path $path --filename $logging_file_list --hostname $hostname --logs ERROR`
```bash
python ./get-pip.py --proxy http://localhost:8080
pip install python-logstash --proxy http://localhost:8080

cd /lib/python2.7/site-packages
cp -r /home/devuser/.local/lib/python2.7/site-packages/python_logstash-0.4.8.dist-info .
sudo cp -r /home/devuser/.local/lib/python2.7/site-packages/logstash .

sudo cp -r home/devuser/.local/lib/python2.7/site-packages/logstash /lib/python2.7/site-packages/
sudo cp -r home/devuser/.local/lib/python2.7/site-packages/python_logstash-0.4.8.dist-info /lib/python2.7/site-packages/



[install pip for python2.7] python ./get-pip.py ➜ [install the library] pip install python-logstash
(.venv) ➜  python ./Grafana-log/push_to_logstash_script.py --path ./Grafana-log --filename test.log --hostname Data_Transfer_Node_#1

#-- 
# Check whether pip tool was installed on the particular instance
pip list
python ./get-pip.py --proxy http://localhost:8080

# Copy libraries from dt to new dts
sudo scp -r devuser@kibana:/home/devuser/monitoring/python_lib/python2.7/* /lib/python2.7/site-packages/
scp -r devuser@data_transfer_node_#3:/home/devuser/monitoring/log_to_logstash/* .
#-- 


sudo vi /etc/rc.d/rc.local

touch /var/lock/subsys/local
/home/devuser/monitoring/metrics_socket/prometheus-gather-server.sh start
/home/devuser/monitoring/log_to_logstash/push_to_logstash.sh start

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

# sudo systemctl disable rc-local

sudo chmod 755 /etc/rc.local && sudo systemctl enable rc-local

# stop the service all
sudo systemctl status rc-local.service

sudo service rc-local stop
sudo service rc-local restart
sudo service rc-local status

sudo systemctl start rc-local.service
sudo service rc-local start
```
- Run Filebeat : /home/biadmin/monitoring/filebeat-5.6.16-linux-x86_64/ home/biadmin/monitoring/filebeat-5.6.16-linux-x86_64



#### Alert
- Run the script : `./Grafana-log/log-aggregation-alert.sh start/stop/status` (In Dev Losgstash, run `/home/biadmin/monitoring/custom_export/log-aggregation-alert.sh start/stop/status`)
- Get the results from Dev ES cluster which has text error logs from the spark custom apps
```bash

# --
# Log Search
GET logstash-logger-*/_search
{
  "query": {
    "bool": {
      "must": [
        {
          "query_string": {
            "query": "Dev or TEST* or Service*",
            "fields": ["env"],
            "lenient": true
          }
        }
      ]
    }
  },
  "sort": [
    {
      "@timestamp": {
        "order": "desc"
      }
    }
  ]
}
# --

# --
# Log Aggregation
GET logstash-logger-*/_search
{
  "size": 0, 
  "query": {
    "bool": {
      "must": [
        {
          "range": {
            "@timestamp": {
              "gte": "2024-10-30T18:00:00"
            }
          }
        }
      ]
    }
  },
  "sort": [
    {
      "@timestamp": {
        "order": "desc"
      }
    }
  ],
  "aggs": {
    "spark_log": {
      "terms": {
        "field": "env.keyword",
        "size": 100
      }
    }
  }
}
```