#!/bin/bash
if [ -z "${EXIST_HOME}" ]; then
    echo "$EXIST_HOME is unset or set to the empty string. Please set this variable"
    exit 1 # terminate and indicate error
fi
if [ ! -f $EXIST_HOME/bin/client.sh ]; then
   echo "eXist client.sh script not available at $EXIST_HOME/bin/client.sh"
   exit 1
fi
if [ $# -lt 1 ]; then
    echo $0: usage: myscript compressed_archive.tar.gz
    exit 1
fi

WORK_DIR=`mktemp -d`
tar -xzf $1 -C $WORK_DIR
echo "eXist Username?:"
read username
echo "exist Password?:"
read password
$EXIST_HOME/bin/client.sh -u $username -P $password -s -c /db/laceData --parse $WORK_DIR 
