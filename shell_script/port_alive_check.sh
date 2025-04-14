
#!/bin/bash
set -e

# Redis port : 6379

# sudo netstat -tulnp | grep -w "6379"
# if [ $? -ne 0 ]
# then
#         echo "🦄 Port is down"
# else
#         echo "🦄 Port is up"
# fi


set -e

port_list=$1

if [[ -n "$port_list" ]]; then
    echo $port_list
else
    echo "'port_list' argument error"
    exit 0
fi

port_lists=$(echo $port_list | tr "," "\n")

# [devuser@localhost UtilityScripts]$ /home/devuser/UtilityScripts/port_alive_check.sh 6379,9116,7090
# 6379,9116,7090
# varification port : 6379
# 🦄 Port is  up
# varification port : 9116
# 🦄 Port is  up
# varification port : 7090
# 🦄 Port is  up


# Redis port : 6379, Alert_Update_Script from Redis : 9116,  7090: UI for the alert, 3100: Grafana-Loki, 7001: Airflow
for varification_port in $port_lists
do
        echo "varification port : $varification_port"
        #sudo netstat -tulnp | grep -w $varification_port
        #if [ $? -ne 0 ]
        if [ -z "$(sudo netstat -tupln | grep $varification_port)" ];
        then
                echo "🦄 Port is  down"
                echo "Trying to active with $varification_port"
                if [ $varification_port == "6379" ]; then
                        sudo /home/devuser/monitoring/redis-5.0.7/redis_service.sh start
                elif [ $varification_port == "9116" ]; then
                        sudo /home/devuser/monitoring/custom_export/standalone-redis-server.sh start
                elif [ $varification_port == "7090" ]; then
                        sudo /apps/monitoring_script/jupyter_notebook/alert-update-start.sh start
                fi

                fi

        else
                echo "🦄 Port is  up"

        fi
done


# -----
# Alert Service
# 10 * * * * /home/devuser/UtilityScripts/port_alive_check.sh 6379,9116,7090
# ----


