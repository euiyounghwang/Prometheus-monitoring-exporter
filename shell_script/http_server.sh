#!/bin/bash

while true;
    pid=`ps ax | grep -i 'logstash' | grep -v grep | awk '{print $1}'`
    if [ -n "$pid" ]
        then
        #echo "logstash is Running as PID: $pid"
        RESPONSE="HTTP/1.1 200 OK\r\nConnection: keep-alive\r\n\r\n${2:-"OK"}\r\n"
    else
        #echo "logstash is not Running"
        RESPONSE="HTTP/1.1 200 OK\r\nConnection: keep-alive\r\n\r\n${2:-"FAIL"}\r\n"
    fi
  do echo -e "$RESPONSE" \
  | nc -l "${1:-8100}";
  sleep 1
done



