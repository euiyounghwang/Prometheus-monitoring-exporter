# Configuration

DT_NODE_1="localhost_1"
DT_NODE_2="localhost_2"
DT_NODE_3="localhost_3"

HOSTS=("$DT_NODE_1" "$DT_NODE_2" "$DT_NODE_3")
PORT="9092"

TIMEOUT=3

echo
echo "***"
echo "Checking connectivity to ${HOST}:${PORT} for Kafka service.."

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
        echo "[Kafka Service #$PROGRESS] SUCCESS: Port ${PORT} on ${HOST} is ALIVE and reachable."
    else
        #echo "Port ${PORT}: [ CLOSED / BLOCKED ]"
        echo "[Kafka Service #$PROGRESS] FAILED: Port ${PORT} on ${HOST} is DOWN or blocked."
    fi
done


echo
echo "***"
echo "Checking connectivity for Kafka Connect service.."

PORT="2181"
#for HOST in "${HOSTS[@]}"; do
for ((i=0; i<TOTAL_HOSTS; i++)); do
    HOST=${HOSTS[$i]}
    # Calculate Human-friendly progress index (1-based instead of 0-based)
    PROGRESS=$((i + 1))

    # Run netcat with a timeout
    if nc -w "$TIMEOUT" -z "$HOST" "$PORT" > /dev/null 2>&1; then
        #echo "Port ${PORT}: [ OPEN ]"
        echo "[Kafka Connect Service #$PROGRESS] SUCCESS: Port ${PORT} on ${HOST} is ALIVE and reachable."
    else
        #echo "Port ${PORT}: [ CLOSED / BLOCKED ]"
        echo "[Kafka Connect Service #$PROGRESS] FAILED: Port ${PORT} on ${HOST} is DOWN or blocked."
    fi
done


echo
echo "***"
echo "Checking connectivity for Spark cluster service.."

HOST="$DT_NODE_1"
PORT="8480"
if nc -w "$TIMEOUT" -z "$HOST" "$PORT" > /dev/null 2>&1; then
    echo "[Spark cluster Service] SUCCESS: Port ${PORT} on ${HOST} is ALIVE and reachable."
    exit 0
else
    echo "[Spark cluster Service] FAILED: Port ${PORT} on ${HOST} is DOWN or blocked."
#    exit 1
fi

echo
echo "***"
