#!/bin/bash

SCRIPTDIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

# go test -v ./tests/
# go test -v ./tests/test_api_test.go

goconvey --workDir=$SCRIPTDIR/tests --port=7090
# goconvey --port=7090