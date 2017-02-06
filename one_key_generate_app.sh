#! /bin/bash

# The set -e option instructs bash to immediately exit
# if any command has a non-zero exit status
set -e

if [[ $# -eq 1 && $1 == "noupdate" ]];then
    UPDATE_DEPLOY_FLAG=0
else
    UPDATE_DEPLOY_FLAG=1
fi

CUR_INSTALL_PATH=$(cd "$(dirname "$0")"; pwd)
DEVOPS_NAME=unichain_devops

# ssh方式 git仓库地址
UNICHAIN_DEPLOY_URL=git@git.oschina.net:wxcsdb88/unichain_deploy.git
UNICHAIN_DEPLOY_NAME=unichain_deploy
# 分之或者tag名
UNICHAIN_DEPLOY_TAG=v1.0

#部署安装包名称
filename_deploy_app_tar_gz="unichain_deploy.tar.gz"
dir_deploy_app="apps"

# sources 下文件
filename_templeate_conf="unichain.conf.template"
filename_app_tar_gz="unichain-archive.tar.gz"


# 1. 创建需要的目录
echo "初始化安装包目录"
if [ ! -d ${DEVOPS_NAME} ]; then
	mkdir ${DEVOPS_NAME}
fi

cd ${DEVOPS_NAME}

if [ ! -d sources ]; then
	mkdir sources
fi

if [ ! -d ${dir_deploy_app} ]; then
	mkdir ${dir_deploy_app}
fi

echo "初始化安装包目录完成"

# 2. 获取最新的部署程序
if [ ${UPDATE_DEPLOY_FLAG} -eq 1 ]; then
	rm -rf ${UNICHAIN_DEPLOY_NAME}
	echo "下载最新部署程序"
	echo -e "地址：${UNICHAIN_DEPLOY_URL}, 分支或标记: ${UNICHAIN_DEPLOY_TAG}"
	git clone ${UNICHAIN_DEPLOY_URL} ${UNICHAIN_DEPLOY_NAME} -b ${UNICHAIN_DEPLOY_TAG}
	echo "下载最新部署程序完成"
else
	echo "部署程序不更新"
fi

# wget -P sources http://ojarf7dqy.bkt.clouddn.com/unichain-archive.tar.gz
# wget -P sources http://ojarf7dqy.bkt.clouddn.com/unichain.conf.template

# 3. 检测 sources目录下是否存在文件 unichain.conf.template, unichain-archive.tar.gz
check_flag=0
if [ ! -f "sources/${filename_templeate_conf}" ]; then
    echo -e "\033[31m sources/$filename_templeate_conf not exist!\033[0m"
    check_flag=1
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

# 4. 复制文件到部署程序目录
cp sources/${filename_templeate_conf} ./${UNICHAIN_DEPLOY_NAME}/deploy/conf/template/
cp -r sources/${filename_app_tar_gz} ./${UNICHAIN_DEPLOY_NAME}/deploy/sources/

# 5. 打包部署程序及安装文件

tar -zcvf ${dir_deploy_app}/${filename_deploy_app_tar_gz} ${UNICHAIN_DEPLOY_NAME}/*
latest_time=`date --date='0 days ago' +"%Y-%m-%d %H:%M:%S"`
#bak_app_name=`date --date='0 days ago' +"%Y%m%d%H%M%S"`_${filename_deploy_app_tar_gz}
bak_app_name=`date --date='0 days ago' +"%Y%m%d%H%M%S"`_${UNICHAIN_DEPLOY_TAG}_${filename_deploy_app_tar_gz}

cp ${dir_deploy_app}/${filename_deploy_app_tar_gz} ${dir_deploy_app}/${bak_app_name}

echo -e "最近更新时间:${latest_time}\n部署程序地址:${UNICHAIN_DEPLOY_URL}\n分支或标记:${UNICHAIN_DEPLOY_TAG}\n\
压缩包:${bak_app_name}\n" >>record.txt

echo -e "部署包 ${filename_deploy_app_tar_gz} 已生成!\n"

exit 0 