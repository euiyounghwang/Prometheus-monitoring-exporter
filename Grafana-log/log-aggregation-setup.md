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

cd /lib/python2.7/site-packages
cp -r /home/devuser/.local/lib/python2.7/site-packages/python_logstash-0.4.8.dist-info .
sudo cp -r /home/devuser/.local/lib/python2.7/site-packages/logstash .

sudo cp -r home/devuser/.local/lib/python2.7/site-packages/logstash /lib/python2.7/site-packages/
sudo cp -r home/devuser/.local/lib/python2.7/site-packages/python_logstash-0.4.8.dist-info /lib/python2.7/site-packages/



[install pip for python2.7] python ./get-pip.py ➜ [install the library] pip install python-logstash
(.venv) ➜  python ./Grafana-log/push_to_logstash_script.py --path ./Grafana-log --filename test.log --hostname Data_Transfer_Node_#1

#-- 
# Copy libraries from dt to new dts
sudo scp -r devuser@kibana:/home/devuser/monitoring/python_lib/python2.7/* .
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
