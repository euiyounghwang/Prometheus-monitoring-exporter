
#!/bin/bash
set -e

# Redis port : 6379

sudo netstat -tulnp | grep -w "6379"
if [ $? -ne 0 ]
then
        echo "🦄 Port is down"
else
        echo "🦄 Port is up"
fi

