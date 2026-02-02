#!/bin/sh
ES_SERVICE_ALL_EXPORT_PATH=/home/devuser/monitoring/custom_export
PATH=$PATH:$ES_SERVICE_ALL_EXPORT_PATH/bin
SERVICE_NAME=gRPC-client

: <<'END'
cat << "EOF"
       _,.
     ,` -.)
    '( _/'-\\-.
   /,|`--._,-^|            ,   
   \_| |`-._/||          ,'|  gRPC
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

export PYTHONDONTWRITEBYTECODE=1

# See how we were called.
case "$1" in
  start)
        # Start daemon.
        echo "🦄 Starting $SERVICE_NAME";
        
        # gRPC
        # nohup python $SCRIPTDIR/RPC/gRPC/gRPC_client.py --file ./RPC/gRPC/gRPC_config.json --gRPC_server_host localhost --env localhost &> /dev/null &
        # python $SCRIPTDIR/RPC/gRPC/gRPC_client.py --file ./RPC/gRPC/gRPC_config.json --gRPC_server_host localhost --env localhost

        # gRPC Stream
        # python $SCRIPTDIR/RPC/gRPC_Stream/gRPC_client.py

        # gRPC client establish the connection with gRPC server using Golang
        python $SCRIPTDIR/RPC/golang_gRPC/gRPC_client.py
        ;;
  stop)
        # Stop daemons.
        echo "🦄 Shutting down $SERVICE_NAME";
        pid=`ps ax | grep -i '/gRPC_client.py' | grep -v grep | awk '{print $1}'`
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
        pid=`ps ax | grep -i '/gRPC_client.py' | grep -v grep | awk '{print $1}'`
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

