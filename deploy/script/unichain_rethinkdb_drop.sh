#!/usr/bin/env bash

source ./blockchain_nodes_conf_util.sh
source ./common_lib.sh

CLUSTER_BIGCHAIN_COUNT=`get_cluster_nodes_num`
[ ${CLUSTER_BIGCHAIN_COUNT} -eq 0 ] && {
    echo -e "[ERROR] blockchain_nodes num is 0"
    exit 1
}

## 设置密码
read -t 30 -s -p "请输入初始化数据库密码:" password

if [ "123456" != ${password} ]; then
    exit 1
fi

## 停止unichain服务
fab stop_unichain

## 初始化数据库
fab set_host:0 unichain_drop_init:${CLUSTER_BIGCHAIN_COUNT}

## 开始unichain服务
fab start_unichain

