#!/bin/bash

# The set -e option instructs bash to immediately exit
# if any command has a non-zero exit status
set -e

# noupdate 0 update 1 download 2
if [[ $# -eq 1 && $1 == "noupdate" ]]; then
    UPDATE_FLAG=0
elif [[ $# -eq 1 && $1 == "update" ]]; then
    UPDATE_FLAG=1
elif [[ $# -eq 1 && $1 == "download" ]]; then
    UPDATE_FLAG=2
else
    UPDATE_FLAG=0
fi

CUR_INSTALL_PATH=$(cd "$(dirname "$0")"; pwd)

# git仓库地址
UNICHAIN_URL=https://git.oschina.net/uni-ledger/unichain.git
UNICHAIN_NAME=unichain
# 分之或者tag名
UNICHAIN_TAG=dev

#部署安装包名称
filename_deploy_app_tar_gz="unichain-deploy.tar.gz"

# sources 下文件
filename_templeate_conf="unichain.conf.template"
filename_app_tar_gz="unichain-archive.tar.gz"


# 1. 检测项目是否存在
cd ../sources/
if [ ! -d ${UNICHAIN_NAME} ]; then
   # 程序不存在,则需要新下载!
	UPDATE_FLAG=2
	echo "${UNICHAIN_NAME} 不存在, 进入项目下载操作!"
fi

# 2. 操作项目
if [ ${UPDATE_FLAG} -eq 0 ]; then
    echo "项目存在,不更新!"
elif [ ${UPDATE_FLAG} -eq 1 ]; then
    echo "项目存在,即将更新!"
	echo -e "地址：${UNICHAIN_URL}, 分支或标记: ${UNICHAIN_TAG}"
	git pull origin ${UNICHAIN_TAG}
	echo "项目更新完成!"
elif [ ${UPDATE_FLAG} -eq 2 ]; then
    echo "清空程序目录"
    rm -rf ${UNICHAIN_NAME}
	echo "下载程序"
	echo -e "地址：${UNICHAIN_URL}, 分支或标记: ${UNICHAIN_TAG}"
	git clone ${UNICHAIN_URL} ${UNICHAIN_NAME} -b ${UNICHAIN_TAG}
	echo "下载程序完成"
fi

# 重新打包生成应用
rm -f  ${filename_app_tar_gz}

cd ${UNICHAIN_NAME}
git archive $UNICHAIN_TAG --format=tar | gzip > ${filename_app_tar_gz}

# local compress and tar
# tar -cf unichain-archive.tar *
# gzip unichain-archive.tar

cp  ${filename_app_tar_gz} ..

cd ../../

# wget -P sources http://ojarf7dqy.bkt.clouddn.com/unichain.conf.template

# 3. 检测 sources目录下是否存在文件 unichain.conf.template, unichain-archive.tar.gz
check_flag=0
if [ ! -f "sources/${filename_templeate_conf}" ]; then
    wget -P sources http://ojarf7dqy.bkt.clouddn.com/unichain.conf.template
    if [ ! -f "sources/${filename_templeate_conf}" ]; then
        echo -e "\033[31m sources/$filename_templeate_conf not exist!\033[0m"
    #  check_flag=1
    fi
fi

if [ ! -f "sources/${filename_app_tar_gz}" ]; then
    echo -e "\033[31m sources/${filename_app_tar_gz} not exist!\033[0m"
    check_flag=1
fi

if [ ${check_flag} != 0 ]; then
	echo "sources目录文件缺失，请检查后再操作！"
	exit 1
fi

#git archive --format=tar.gz --remote=origin ${UNICHAIN_DEPLOY_TAG}| gzip >${filename_app_tar_gz}

# 4. 复制文件
cp sources/${filename_templeate_conf} conf/template/



# 5. 打包部署程序及安装文件

#tar -zcvf ${dir_deploy_app}/${filename-deploy_app_tar_gz} ${UNICHAIN_DEPLOY_NAME}/*
#latest_time=`date --date='0 days ago' +"%Y-%m-%d %H:%M:%S"`
##bak_app_name=`date --date='0 days ago' +"%Y%m%d%H%M%S"`_${deploy_app_tar_gz}
#bak_app_name=`date --date='0 days ago' +"%Y%m%d%H%M%S"`_${UNICHAIN_DEPLOY_TAG}_${deploy_app_tar_gz}
#
#cp ${dir_deploy_app}/${deploy_app_tar_gz} ${dir_deploy_app}/${bak_app_name}
#
#echo -e "最近更新时间:${latest_time}\n部署程序地址:${UNICHAIN_DEPLOY_URL}\n分支或标记:${UNICHAIN_DEPLOY_TAG}\n\
#压缩包:${bak_app_name}\n" >>record.txt
#
#echo -e "部署包 ${deploy_app_tar_gz} 已生成!\n"

echo -e "地址：${UNICHAIN_URL}, 分支或标记: ${UNICHAIN_TAG}"
echo -e "执行结束!"
exit 0