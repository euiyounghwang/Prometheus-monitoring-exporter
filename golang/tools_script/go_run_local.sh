
#!/bin/bash
set -e

SET_ENV_NAME=localhost

# Arguments for the script
export DB_URL=oracle://test:1@localhost:1234/test
export SQL=SELECT A,B FROM TB

go run ./tools_run.go
