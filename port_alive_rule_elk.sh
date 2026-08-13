#!/bin/bash

# Configuration
ES_DATA_NODE_1="localhost_1"
ES_DATA_NODE_2="localhost_2"
ES_DATA_NODE_3="localhost_3"


HOSTS=("$ES_DATA_NODE_1" "$ES_DATA_NODE_2" "$ES_DATA_NODE_3")
PORT="9200"

TIMEOUT=3

echo
echo "***"
echo "Checking connectivity to ${HOST}:${PORT} for Elasticsearch service.."

# Run netcat port scan
# -z: Zero-I/O mode (scans for listening daemons without sending data)
# -v: Verbose output
# -w: Timeout in seconds
#if nc -w "$TIMEOUT" -z "$HOST1" "$PORT1" > /dev/null 2>&1; then
#    echo "[Kafka Service #1] SUCCESS: Port ${PORT} on ${HOST} is ALIVE and reachable."
#    exit 0
#else
#    echo "[Kafka Service #1] FAILED: Port ${PORT} on ${HOST} is DOWN or blocked."
#    exit 1
#fi

# Get the total count of ports in the array
TOTAL_HOSTS=${#HOSTS[@]}

#for HOST in "${HOSTS[@]}"; do
for ((i=0; i<TOTAL_HOSTS; i++)); do
    HOST=${HOSTS[$i]}
    # Calculate Human-friendly progress index (1-based instead of 0-based)
    PROGRESS=$((i + 1))

    # Run netcat with a timeout
    if nc -w "$TIMEOUT" -z "$HOST" "$PORT" > /dev/null 2>&1; then
        #echo "Port ${PORT}: [ OPEN ]"
        echo "[Elasticsearch Service #$PROGRESS] SUCCESS: Port ${PORT} on ${HOST} is ALIVE and reachable."
    else
        #echo "Port ${PORT}: [ CLOSED / BLOCKED ]"
        echo "[Elasticsearch Service #$PROGRESS] FAILED: Port ${PORT} on ${HOST} is DOWN or blocked."
    fi
done


echo
echo "***"
echo "Checking connectivity for Kibana service.."

HOST="$ES_DATA_NODE_3"
PORT="5601"

if nc -w "$TIMEOUT" -z "$HOST" "$PORT" > /dev/null 2>&1; then
    echo "[Kibana Service] SUCCESS: Port ${PORT} on ${HOST} is ALIVE and reachable."
    #exit 0
else
    echo "[Kibana Service] FAILED: Port ${PORT} on ${HOST} is DOWN or blocked."
#    exit 1
fi


echo
echo "***"
echo "Checking connectivity for Logstash service.."

HOST="$ES_DATA_NODE_2"
PORT="5044"

if nc -w "$TIMEOUT" -z "$HOST" "$PORT" > /dev/null 2>&1; then
    echo "[Logstash Service] SUCCESS: Port ${PORT} on ${HOST} is ALIVE and reachable."
    exit 0
else
    echo "[Logstash Service] FAILED: Port ${PORT} on ${HOST} is DOWN or blocked."
#    exit 1
fi

echo
echo "***"

