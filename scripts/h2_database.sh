
#!/bin/bash
set -e

JAVA_HOME=~/openlogic-openjdk-11.0.23+9-linux-x64
export PATH=$JAVA_HOME/bin:$PATH
export JAVA_HOME


# Activate virtualenv && run serivce

SCRIPTDIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
cd $SCRIPTDIR

PATH="/home/biadmin/monitoring/custom_export"

VENV=".venv"

# Python 3.11.7 with Window
if [ -d "$PATH/$VENV/bin" ]; then
    source $PATH/$VENV/bin/activate
else
    source $PATH/$VENV/Scripts/activate
fi


python $SCRIPTDIR/h2_database_script.py --db_url jdbc:h2:tcp://localhost/~/monitoring/h2/data/tcp_monitoring --user "test,test" --sql "SELECT * FROM MONITORING_LOG"