
<i>Redis (REmote DIctionary Server) is an open source, in-memory, NoSQL key/value store that is used primarily as an application cache or quick-response database.

Redis (link resides outside ibm.com) stores data in memory, rather than on a disk or solid-state drive (SSD), which helps deliver unparalleled speed, reliability, and performance.

#### Redis
```bash
sudo netstat -npat | grep redis
./src/redis-server ./redis.conf --protected-mode no
```


#### Redis Cluster
```bash
[root@localhost redis-5.0.5]# src/redis-cli
127.0.0.1:6379> set for bar
OK
127.0.0.1:6379> get for
"bar"
127.0.0.1:6379>
```


#### Register Service
```bash
#-- sudo vi /etc/systemd/system/redis_service.service

# ./redis_service.sh
#!/bin/sh
/home/devuser/monitoring/redis-5.0.7/src/redis-server /home/devuser/monitoring/redis-5.0.7/redis.conf --protected-mode no

--
[Unit]
Description=Redis Service

[Service]
User=devuser
Group=devuser
Type=simple
ExecStart=/bin/bash /home/devuser/monitoring/redis-5.0.7/redis_service.sh
ExecStop= /usr/bin/killall /redis_service

[Install]
WantedBy=default.target
--


# Service command
sudo systemctl daemon-reload
sudo systemctl enable redis_service.service
sudo systemctl start redis_service.service 
sudo systemctl status redis_service.service 
sudo systemctl stop redis_service.service 

sudo service redis_service status/stop/start


#-- sudo vi /etc/systemd/system/alert_service.service

# ./standalone-redis-server.sh
#!/bin/sh

--
[Unit]
Description=Alert Service

[Service]
User=devuser
Group=devuser
Type=simple
ExecStart=/bin/bash /home/devuser/monitoring/custom_export/standalone-redis-server-direct.sh
ExecStop= /usr/bin/killall /alert_service

[Install]
WantedBy=default.target
--


# Service command
sudo systemctl daemon-reload
sudo systemctl enable alert_service.service
sudo systemctl start alert_service.service 
sudo systemctl status alert_service.service 
sudo systemctl stop alert_service.service 

sudo service alert_service status/stop/start
```bash