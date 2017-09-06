#! /bin/bash

# The set -e option instructs bash to immediately exit
# if any command has a non-zero exit status
set -e

function printErr()
{
     echo "usage: ./nginx_log_cut.sh <m> <h> <dom> <mon> <dow> <user>"
     echo "argument error, should $1"
}

if [ $# -eq 1 ] && [ $1 == "help" -o $1 == "h" ]; then
     printErr "m, h, dom, mon, dow, user should not be empty"
     exit 1
fi

# steps:
# send the script to /nginx/script/
#fab -f fabfile_nginx.py config_nginx_log_cut

# add the task into crontab

if [ $# -eq 0 ]; then
    fab -f fabfile_nginx.py config_nginx_log_crontab
    exit 0
elif [ $# -eq 1 ]; then
    fab -f fabfile_nginx.py config_nginx_log_crontab:m=$1
    exit 0
elif [ $# -eq 2 ]; then
    fab -f fabfile_nginx.py config_nginx_log_crontab:m=$1,h=$2
    exit 0
elif [ $# -eq 3 ]; then
    fab -f fabfile_nginx.py config_nginx_log_crontab:m=$1,h=$2,dom=$3
    exit 0
elif [ $# -eq 4 ]; then
    fab -f fabfile_nginx.py config_nginx_log_crontab:m=$1,h=$2,dom=$3,mon=$4
    exit 0
elif [ $# -eq 5 ]; then
    fab -f fabfile_nginx.py config_nginx_log_crontab:m=$1,h=$2,dom=$3,mon=$4,dow=$5
    exit 0
elif [ $# -eq 6 ]; then
    fab -f fabfile_nginx.py config_nginx_log_crontab:m=$1,h=$2,dom=$3,mon=$4,dow=$5,user=$6
    exit 0
else
    printErr "m, h, dom, mon, dow, user should not be empty"
fi


