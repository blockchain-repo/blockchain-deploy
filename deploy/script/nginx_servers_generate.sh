#! /bin/bash

# The set -e option instructs bash to immediately exit
# if any command has a non-zero exit status
set -e

function printErr()
{
     echo "usage: ./nginx_servers_generate.sh <upstream_name> <server_port> <delete>"
     echo "No argument $1 supplied"
}

if [ $# -lt 2 ]; then
    printErr "upstream_name, server_port should not be empty"
    exit 1
fi

# generate the base servers file
if [ $# -eq 2 ]; then
    fab -f fabfile_nginx.py generate_nginx_server_conf:$1,$2
    exit 0
elif [ $# -eq 3 ]; then
    fab -f fabfile_nginx.py generate_nginx_server_conf:$1,$2,$3
    exit 0
fi



