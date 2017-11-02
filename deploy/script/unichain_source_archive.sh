#! /bin/bash

## 获取最新源码 并打tar.gz包
set -e

SOURCES_TAR_GZ='unichain-archive.tar.gz'
SOURCES_ADDRESS_YF='http://192.168.0.249:99/unichain/unichain.git'
SOURCES_ADDRESS_OTHER='http://36.110.71.170:99/unichain/unichain.git'
SOURCES_BRANCH='dev'
SOURCES_NAME='unichain'
NEW="new"

## 到sources目录下
cd ../sources

## 输入参数转变为小写
typeset -l INPUT
INPUT=$1

## 清除已有代码并下载打包最新代码
if [ $# -gt 0 ];then
    if [  ${INPUT} == ${NEW} ]; then
        rm -rf ./unichain
        git clone ${SOURCES_ADDRESS_OTHER} ${SOURCES_NAME} -b ${SOURCES_BRANCH}
        tar -zcvf unichain-archive.tar.gz ./unichain
    fi
else
    ## 判断源码包是否存在，不存在则下载并打包
    if [ ! -f ${SOURCES_TAR_GZ} ]; then
        git clone ${SOURCES_ADDRESS_OTHER} ${SOURCES_NAME} -b ${SOURCES_BRANCH}
        tar -zcvf unichain-archive.tar.gz ./unichain
    fi
fi

cp ../sources/unichain-archive.tar.gz ../script/

## 返回到script目录下
cd ../script

exit 0

