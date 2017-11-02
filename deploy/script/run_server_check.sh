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
# get port & check port & check process
echo -e "[INFO]===========detect rethinkdb==========="
for((i=0; i<${CLUSTER_BIGCHAIN_COUNT}; i++));do
    fab set_host:$i detect_rethinkdb:$i
done
#detect localdb
# get port & check port & check process
echo -e "[INFO]===========detect localdb==========="
fab detect_localdb

#detect unichain-pro
# get bigchain port & check port & check process
echo -e "[INFO]===========detect unichain=========="
for((i=0; i<${CLUSTER_BIGCHAIN_COUNT}; i++));do
    fab set_host:$i detect_unichain
done

#detect unichain-api
# get api port & check port & check api
echo -e "[INFO]===========detect unichain-api==========="
for((i=0; i<${CLUSTER_BIGCHAIN_COUNT}; i++));do
    fab set_host:$i detect_unichain_api
done

exit 0
