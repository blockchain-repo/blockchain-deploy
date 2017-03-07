#!/bin/bash
#####################################
##  Install the deployment portal  ##
#####################################
set -e

mkdir -p ../log

function echo_green
{
    local content=$@
    echo -e "\033[1;32m${content}\033[0m"
    return 0
}

function usage
{
    echo_green "
Options:
    install     install unichain monitor
    uninstall   uninstall unichain monitor
    load *.tar  load docker images  
    "
    return 0
}

chmod +755 *.sh 2>/dev/null
chmod +755 *.py 2>/dev/null

case $1 in
    h|help|-h|-help)
        usage
    ;;
    install)
	./setup_monitor.sh | tee ../log/setup_monitor.log
	;;
    uninstall)
	./uninstall_monitor.sh | tee ../log/uninstall_monitor.log
    ;;
    load)
	if [ $# == 1 ]
	then
   		echo "please add load images tar"
   		echo "Usage: ./bulid_monitor.sh load *.tar"
   		exit 1
	fi

	for i in $@
	do
	if [ "$i" != "load" ]
	then
		./load_images.sh $i | tee ../log/load_images.log
	fi
	done
esac

exit 0

