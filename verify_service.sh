
#!/bin/bash
set -e

echo "Verifing the spark app"
sh -c 'sudo su - spark -c "./utils/sparkSubmitWMx.sh status"'
echo "Finished."

sh -c 'sudo ~/utils/kafkaUtil.sh status'
sh -c 'sudo ~/utils/connectUtil.sh status'

echo "Verifing the Elsticsearch"
sh -c 'sudo su - elasticsearch -c "/apps/elasticsearch/latest/bin/elasticsearch -d"'
echo "Finished."