#!/bin/bash
set -e

# -- Export Variable
export GRAFANA_DASHBOARD_URL="http://localhost:3000/d/adm08055cf3lsa/es-team-dashboard?orgId=1'&'from=now-5m'&'to=now'&'refresh=5s"
export EMAIL_LIST="a@test.com"
# -- 

python ./mail_alert.py
