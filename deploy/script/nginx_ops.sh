#! /bin/bash

# The set -e option instructs bash to immediately exit
# if any command has a non-zero exit status
set -e

items_nginx="[start|stop|restart|reload|force-reload|status|test]"

function printErr()
{
     echo "usage: ./nginx_servers_send.sh ${items_nginx}"
     echo "No argument $1 supplied"
}

if [ $# -lt 1 ]; then
    printErr "op should not be empty"
    exit 1
fi

[[ ${items_nginx} =~ "$1" ]] || (echo -e "param $1 error, should in ${items_nginx}" && exit 1)

fab -f fabfile_nginx.py nginx_ops:$1