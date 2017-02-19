#!/bin/bash

# The set -e option instructs bash to immediately exit
# if any command has a non-zero exit status
set -e

CUR_PATH=$(cd "$(dirname "$0")"; pwd)
CLUSTER_CHAINNODES_CONF=${CUR_PATH}/../conf/blockchain_nodes

filename_templeate_conf="unichain.conf.template"
CLUSTER_UNICHAIN_TEMPLATE_CONF=${CUR_PATH}/../conf/template/$filename_templeate_conf

filename_app_tar_gz="unichain-archive.tar.gz"
CLUSTER_APP_TAR_GZ=${CUR_PATH}/../sources/$filename_app_tar_gz

if [ ! -f $CLUSTER_UNICHAIN_TEMPLATE_CONF ]; then
    echo -e "\033[31m conf/template/$filename_templeate_conf not exist!\033[0m"
    exit 1
fi

if [ ! -f $CLUSTER_APP_TAR_GZ ]; then
    echo -e "\033[31m conf/template/$filename_app_tar_gz not exist!\033[0m"
    exit 1
fi

exit 0
