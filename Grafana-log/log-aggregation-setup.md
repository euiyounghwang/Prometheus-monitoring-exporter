# Log Aggregaation
<i>Log Aggregaation

To save spark text log, we need to pass it to filebeat-logstash-es cluster. However, if we pass all lines in the spark log or archive log files to logstash using filebeat, a lot of traffic will be generated.
So, instead of filebeat, I implemented a python script as agent to read only error logs and pass them to logstash.
- ./push_to_logstash.sh start (This script will be run as agent to send text logs to logstash using TCP socket)
- Then, The Grafana dashboard will read the ES log index in ES cluster and show ERROR logs in near real time.


#### Setup/Run Logstash-Agent
- Run the script : `./Grafana-log/push_to_logstash.sh start` or `python $LOGGING_SERVICE_ALL_EXPORT_PATH/push_to_logstash_script.py --path $path --filename $logging_file_list --hostname $hostname --logs ERROR`
```bash
python ./get-pip.py
pip install python-logstash

[install pip for python2.7] python ./get-pip.py ➜ [install the library] pip install python-logstash
(.venv) ➜  python ./Grafana-log/push_to_logstash_script.py --path ./Grafana-log --filename test.log --hostname Data_Transfer_Node_#1
```
