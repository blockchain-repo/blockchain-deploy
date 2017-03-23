#! /bin/bash

# The set -e option instructs bash to immediately exit
# if any command has a non-zero exit status
set -e

function printErr()
{
     echo "usage: ./nginx_servers_send.sh <upstream_name>"
     echo "No argument $1 supplied"
}

if [ $# -lt 1 ]; then
    printErr "upstream_name(filename) should not be empty"
    exit 1
fi


# configure the reomote nginx servers
fab -f fabfile_nginx.py config_nginx_server:$1