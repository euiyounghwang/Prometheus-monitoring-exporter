#!/bin/bash
set -e

SCRIPTDIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
echo $SCRIPTDIR

#-- 
# Generic H2 (Server)
# jdbc:h2:tcp://localhost/~/monitoring/h2/data/tcp_monitoring

# --
# Generic H2 (Embedded)
# jdbc:h2:~/monitoring/h2/data/tcp_monitoring

# -- local
#$SCRIPTDIR/h2.sh -webAllowOthers
#$SCRIPTDIR/h2.sh -webAllowOthers -tcp -tcpAllowOthers -tcpPort 9092
# - local
#nohup $SCRIPTDIR/local-h2.sh &> /dev/null &
# - tcp
nohup $SCRIPTDIR/h2.sh -webAllowOthers -tcp -tcpAllowOthers -tcpPort 9092 &> /dev/null &
#nohup $SCRIPTDIR/h2.sh -webExternalNames localhost -webAllowOthers -tcp -tcpAllowOthers -tcpPort 9092 &> /dev/null &
