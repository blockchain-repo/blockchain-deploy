#!/bin/bash

set -e
source ./blockchain_nodes_conf_util.sh
source ./common_lib.sh

CLUSTER_BIGCHAIN_COUNT=`get_cluster_nodes_num`
[ $CLUSTER_BIGCHAIN_COUNT -eq 0 ] && {
    echo -e "[ERROR] blockchain_nodes num is 0"
    exit 1
}

#detect rethinkdb
echo -e "[INFO]===========检测rethinkdb进程及分片及副本数==========="
for((i=0; i<${CLUSTER_BIGCHAIN_COUNT}; i++));do
    fab set_host:$i detect_rethinkdb:$i
done
#detect localdb
echo -e "[INFO]===========检测localdb==========="
fab detect_localdb

#detect unichain-pro
echo -e "[INFO]===========检测unichain集群个数及进程数=========="
fab detect_unichain

#detect unichain-api
echo -e "[INFO]===========检测unichain集群个数及api进程数==========="
fab detect_unichain_api

echo -e "[INFO]===========检测unichain的公约环==========="
fab set_host:0 detect_unichain_config

exit 0
