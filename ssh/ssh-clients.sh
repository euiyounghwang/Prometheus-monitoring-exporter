#!/bin/bash
set -e


# Activate virtualenv && run serivce

ROOTDIR=$(pwd)
SCRIPTDIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"


VENV=".venv"

# Python 3.11.7 with Window
if [ -d "$VENV/bin" ]; then
    source $ROOTDIR/$VENV/bin/activate
else
    source $ROOTDIR/$VENV/Scripts/activate
fi

# python $SCRIPTDIR/ssh-client.py --service elasticsearch --cmd "ls -l"
python $SCRIPTDIR/ssh-clients.py --service elasticsearch --cmd "ps ax | grep -i '/elasticsearch' | grep -v grep | awk '{print \$1}'"
