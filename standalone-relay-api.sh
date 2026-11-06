#!/bin/sh
ES_SERVICE_ALL_EXPORT_PATH=/home/devuser/monitoring/relay_api
PATH=$PATH:$ES_SERVICE_ALL_EXPORT_PATH/bin
SERVICE_NAME=es-relay-api-service

: <<'END'
cat << "EOF"
       _,.
     ,` -.)
    '( _/'-\\-.
   /,|`--._,-^|            ,   ES Team
   \_| |`-._/||          ,'|  Monitoring
     |  `-, / |         /  /
     |     || |        /  /
      `r-._||/   __   /  /
  __,-<_     )`-/  `./  /
 '  \   `---'   \   /  /
     |           |./  /
     /           //  /
 \_/' \         |/  /
  |    |   _,^-'/  /
  |    , ``  (\/  /_
   \,.->._    \X-=/^
   (  /   `-._//^`
    `Y-.____(__}
     |     {__)
           ()`
EOF
END

SCRIPTDIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
cd $SCRIPTDIR

echo "Running Path .. $SCRIPTDIR"

VENV=".venv"

# Python 3.11.7 with Window
if [ -d "$VENV/bin" ]; then
    source $VENV/bin/activate
else
    source $VENV/Scripts/activate
fi

process_name='/home/biadmin/monitoring/relay_api/standalone-relay-api.py'

# -- Export Variable
export PYTHONDONTWRITEBYTECODE=1
# --

# -- Cronjob
# Monitoring API Service
# */30 * * * * su - biadmin -c "/home/devuser/monitoring/relay_api/standalone-relay-api.sh start"
# --

# See how we were called.
case "$1" in
  start)
        PID=$(ps -ef | grep $process_name | grep -v grep)
        test=$?
        if [ $test -eq 0 ]
        then
          PID=$(ps -ef | grep $process_name | grep -v grep | tr -s ' ' | cut -d " " -f2)
          echo $SERVICE_NAME is Running as $PID
          #kill -9 $PID
        else
          # Start daemon.
          echo "🦄 Starting $SERVICE_NAME";
          # nohup python $SCRIPTDIR/standalone-relay-api.py --port 3002 &> /dev/null &
          python $SCRIPTDIR/standalone-relay-api.py --port 3002
        fi
        ;;
  stop)
        # Stop daemons.
        echo "🦄 Shutting down $SERVICE_NAME";
        pid=`ps ax | grep -i '/standalone-relay-api.py' | grep -v grep | awk '{print $1}'`
        if [ -n "$pid" ]
          then
          kill -9 $pid
         else
          echo "🦄 $SERVICE_NAME was not Running"
        fi
        ;;
  restart)
        $0 stop
        sleep 2
        $0 start
        # Need to wait for two seconds to start python script via Fabric
        sleep 2
        ;;
  status)
        pid=`ps ax | grep -i '/standalone-relay-api.py' | grep -v grep | awk '{print $1}'`
        if [ -n "$pid" ]
          then
          echo "🦄 $SERVICE_NAME is Running as PID: $pid"
        else
          echo "🦄 $SERVICE_NAME is not Running"
        fi
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
esac

