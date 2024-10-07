
#!/bin/bash
set -e

sudo journalctl -u alert_service.service -f
