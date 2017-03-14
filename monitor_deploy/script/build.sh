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
    tools       install docker tools default use local package
    tools_net   install docker tools use pip3
    start       create containers and startup containers
    stop        close unichain monitor and remove the docker containers
    uninstall   uninstall unichain monitor
    add_nodes   add nodes grafana query conditions
    load *.tar  load docker images  
    "
    return 0
}

chmod -f +755 *.sh 2>/dev/null
chmod -f +755 *.py 2>/dev/null || [[ $? -ne 0 ]] 

case $1 in
    h|help|-h|-help)
        usage
    ;;
    install)
	./setup_monitor.sh | tee ../log/setup_monitor.log
    ;;
    tools)
        ./install_docker_local.sh | tee ../log/install_docker_local.log
    ;;
    tools_net)
        ./install_docker_pip3.sh | tee ../log/install_docker_pip3.log
    ;;
    start)
        ./start_monitor.sh | tee ../log/start_monitor.log
    ;;
    stop)
	./stop_monitor.sh | tee ../log/stop_monitor.log
    ;;
    uninstall)
	./uninstall_monitor.sh | tee ../log/uninstall_monitor.log
    ;;
    add_nodes)
    ./add_nodes_json.sh | tee ../log/add_nodes_json.log
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
      ;;
      *)
       usage
       ;;
esac

exit 0

