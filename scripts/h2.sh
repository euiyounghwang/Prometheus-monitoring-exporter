#!/bin/sh

JAVA_HOME='/home/devuser/monitoring/openlogic-openjdk-11.0.23+9-linux-x64'
export PATH=$JAVA_HOME/bin:$PATH
export JAVA_HOME
echo $PATH

JAR_PATH="/home/devuser/monitoring/h2/bin"

dir=$(dirname "$0")
echo $dir
#java -cp "$JAR_PATH/h2-2.3.232.jar:$H2DRIVERS:$CLASSPATH" org.h2.tools.Console "$@"
#java -cp "$JAR_PATH/h2-2.3.232.jar:$H2DRIVERS:$CLASSPATH" org.h2.tools.Server -webAllowOthers -tcpAllowOthers
java -cp "$JAR_PATH/h2-2.3.232.jar:$H2DRIVERS:$CLASSPATH" org.h2.tools.Server -webAllowOthers -tcpAllowOthers -webExternalNames localhost
