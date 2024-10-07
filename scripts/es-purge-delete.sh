# - touch -t 202409291500 ./sparkU.log.2024-09-27

# - +0 means older than 24 hours and 0 within the last 24 hours.
# -- spark logs
sudo find /apps/var/spark/logs/*log* -mtime +0 -exec rm {} \;
# -- kafka logs
sudo find /apps/kafka_2.11-0.11.0.0/logs -name '*log*' -type f -mtime +0 -exec rm -f {} \;
