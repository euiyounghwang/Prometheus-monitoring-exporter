#!/bin/sh
ES_SERVICE_ALL_EXPORT_PATH=/home/devuser/monitoring/rest_api/app_db_interface
PATH=$PATH:$ES_SERVICE_ALL_EXPORT_PATH/bin
SERVICE_NAME=app_db_interface-service-all-service

JAVA_HOME='/apps/java/latest'
export PATH=$JAVA_HOME/bin:$PATH
export JAVA_HOME


: <<'END'
cat << "EOF"
       _,.
     ,` -.)
    '( _/'-\\-.
   /,|`--._,-^|            ,   
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


VENV=".venv"

# Python 3.11.7 with Window
if [ -d "$ES_SERVICE_ALL_EXPORT_PATH/$VENV/bin" ]; then
    source $ES_SERVICE_ALL_EXPORT_PATH/$VENV/bin/activate
else
    source $ES_SERVICE_ALL_EXPORT_PATH/$VENV/Scripts/activate
fi


export PYTHONDONTWRITEBYTECODE=1

# See how we were called.
case "$1" in
  start)
        # Start daemon.
        echo "🦄 Starting $SERVICE_NAME";
        # nohup python $ES_SERVICE_ALL_EXPORT_PATH/db_interface_app_api.py &> /dev/null &
        python $ES_SERVICE_ALL_EXPORT_PATH/db_interface_app_api.py
        # python $ES_SERVICE_ALL_EXPORT_PATH/db_interface_app_api.py --server_mode grpc
        # python $ES_SERVICE_ALL_EXPORT_PATH/db_interface_app_api.py --server_mode socket
        ;;
  stop)
        # Stop daemons.
        echo "🦄 Shutting down $SERVICE_NAME";
        pid=`ps ax | grep -i '/db_interface_app_api.py' | grep -v grep | awk '{print $1}'`
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
        pid=`ps ax | grep -i '/db_interface_app_api.py' | grep -v grep | awk '{print $1}'`
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

