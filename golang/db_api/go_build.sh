#!/bin/bash
set -e

# compile a go file/project on windows for Linux: `env GOOS=linux go build -o ./bin/prometheus` (Run this command `chmod 755 filname` after copying to linux server)

env GOOS=linux go build -o ./output/db_api_agent
# env GOOS=windows GOARCH=amd64 go build -o ./output/db_api_agent.exe ./go_db.go
