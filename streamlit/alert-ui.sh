#!/bin/bash
set -e


SCRIPTDIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
cd $SCRIPTDIR

VENV=".venv"

# Python 3.11.7 with Window
if [ -d "$VENV/bin" ]; then
    source $VENV/bin/activate
else
    source $VENV/Scripts/activate
fi


PROMETHEUS_HOST="dev:localhost,dev1:localhost"
API_HOST="localhost"

export PROMETHEUS_HOST
export API_HOST

# streamlit run [streamlit-filenam.py] [--server.port 30001]
streamlit run $SCRIPTDIR/main.py --server.port 7001
#streamlit run $SCRIPTDIR/main.py
