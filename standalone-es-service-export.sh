#!/bin/sh
ES_SERVICE_ALL_EXPORT_PATH=/home/devuser/monitoring/custom_export
PATH=$PATH:$ES_SERVICE_ALL_EXPORT_PATH/bin
SERVICE_NAME=es-service-all-service

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
        nohup $ES_SERVICE_ALL_EXPORT_PATH/standalone-export-run.sh &> /dev/null &
        ;;
  stop)
        # Stop daemons.
        echo "🦄 Shutting down $SERVICE_NAME";
        pid=`ps ax | grep -i '/standalone-es-service-export.py' | grep -v grep | awk '{print $1}'`
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
        sleep 2
        ;;
  status)
        pid=`ps ax | grep -i '/standalone-es-service-export.py' | grep -v grep | awk '{print $1}'`
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

