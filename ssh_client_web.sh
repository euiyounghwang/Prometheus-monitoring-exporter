#!/bin/bash
set -e

export PYTHONDONTWRITEBYTECODE=1

SCRIPTDIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
cd $SCRIPTDIR

VENV=".venv"

# Python 3.11.7 with Window
if [ -d "$VENV/bin" ]; then
    source $VENV/bin/activate
else
    source $VENV/Scripts/activate
fi

SERVICE_NAME=ssh-client-web-service

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

# See how we were called.
case "$1" in
  start)
        # Start daemon.
        echo "🦄 Starting $SERVICE_NAME";
        # nohup python $SCRIPTDIR/ssh_client_web.py &> /dev/null &
        python $SCRIPTDIR/ssh_client_web.py
        # gunicorn ssh_client_web:app --bind 0.0.0.0:8000 --workers 4
        ;;
  stop)
        # Stop daemons.
        echo "🦄 Shutting down $SERVICE_NAME";
        pid=`ps ax | grep -i '/ssh_client_web.py' | grep -v grep | awk '{print $1}'`
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
        pid=`ps ax | grep -i '/ssh_client_web.py' | grep -v grep | awk '{print $1}'`
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

