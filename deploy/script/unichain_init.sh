#!/bin/bash

# The set -e option instructs bash to immediately exit
# if any command has a non-zero exit status
set -e

CUR_PATH=$(cd "$(dirname "$0")"; pwd)

function usage()
{
    echo_green "
Usage:
    $0 [-g -b branch_name -s https://xxx.com -udp]
Options:
    -h  usage help
    -g  use git update and pack the code
    -b  the branch of the git repo, default dev
    -s  the url of the code repo
    -u  update the code, if choose g will use git pull
    -p  pack the code
    -d  delete the code and unichain-archive.tar.gz
    -t  template files re-download
    "
    return 0
}

project_name=unichain
use_git=false

pack_local_code=false
git_branch="dev"
repo_url="https://git.oschina.net/uni-ledger/unichain.git"

# sources 下文件
filename_templeate_conf="unichain.conf.template"
filename_app_tar_gz="unichain-archive.tar.gz"

function echo_green()
{
    local content=$@
    echo -e "\033[1;32m${content}\033[0m"
    return 0
}

function echo_red()
{
    local content=$@
    echo -e "\e[1;31m${content}\e[0m"
    return 0
}

function check_exist_dir()
{
    if [ -z "$1" ]; then
        echo "目录或路径输入错误"
        exit 1
    fi

    if [ ! -d "$1" ]; then
	    unichain_exist=0
	else
	    unichain_exist=1
    fi
}

function check_exist_file()
{
    if [ -z "$1" ]; then
        echo "文件名或路径输入错误"
        exit 1
    fi

    if [ ! -f "$1" ]; then
	    unichain_conf_file_exist=0
	else
	    unichain_conf_file_exist=1
    fi
}

# 0 not exist download, 1 exist, 2 delete and download
function download_confile()
{
    cd ${CUR_PATH}/../sources/
    if [ "$1" == 0 ]; then
        echo_red "下载模板文件 ${filename_templeate_conf} !"
        wget -P . http://ojarf7dqy.bkt.clouddn.com/unichain.conf.template
        cp ${filename_templeate_conf} ${CUR_PATH}/../conf/template/
    elif [  "$1" == 2 ]; then
        mv "${filename_templeate_conf}" "${filename_templeate_conf}.bak"
        rm -f "${filename_templeate_conf}"
        echo_red "下载模板文件 ${filename_templeate_conf} !"
        wget -P . http://ojarf7dqy.bkt.clouddn.com/unichain.conf.template
        cp ${filename_templeate_conf} ${CUR_PATH}/../conf/template/
    fi
    return 0
}

function download_code()
{
    echo -e "即将从仓库 ${repo_url}\n下载分支为 ${git_branch} 的代码至目录 ${project_name} 中!"
    cd ${CUR_PATH}/../sources/
    git clone ${repo_url} ${project_name} -b ${git_branch}
    return 0
}

function delete_code()
{
    cd ${CUR_PATH}/../sources/
    rm -f  ${filename_app_tar_gz}
    rm -rf ${project_name}
    return 0
}

#only choose git can update the code use the repo
function update_code()
{
    cd ${CUR_PATH}/../sources/${project_name}/
    if [ "${1}" == true ]; then
        echo_red "使用git更新代码，地址:${repo_url}, 分支: ${git_branch}"
        #git pull origin ${git_branch}
    fi
    git pull origin
    return 0
}

function pack_code()
{
    cd ${CUR_PATH}/../sources/${project_name}/

    rm -f ${filename_app_tar_gz}
    if [ "${1}" == true ]; then
        echo_red "使用 git archive 打包本地代码并生成 ${filename_app_tar_gz}"
        git archive ${git_branch} --format=tar | gzip > ${filename_app_tar_gz}
    else
        echo_red "使用 tar & gzip 打包本地代码并生成 ${filename_app_tar_gz}"
        tar -cf unichain-archive.tar *
        gzip -f unichain-archive.tar
        #gzip unichain-archive.tar
    fi
    cp  ${filename_app_tar_gz} ..
    return 0
}

function main() {
    local OPTIND
    while getopts gb:s:updt OPT; do
       case $OPT in
          g)
            use_git=true
            ;;
          b)
            git_branch=$OPTARG
            ;;
          s)
            repo_url=$OPTARG
            ;;
          u)
            update_local_code=true     # update the unichain code
            ;;
          p)
            pack_local_code=true       # pack the unichain code
            ;;
          d)
            delete_local_code=true     # delete the unichain code and unichain-archive.tar.gz
            ;;
          t)
            re_download_template=true  # re download the unichain template
            ;;
          h)
            usage
            exit 0
            ;;
          \?)
            usage
            exit 1
            ;;
          *)
            usage
            exit 1
            ;;
       esac
    done
}

main $@
project_dir=${CUR_PATH}/../sources/${project_name}
path_unichain_conf_file=${CUR_PATH}/../sources/${filename_templeate_conf}

if [ "${delete_local_code}" == true ]; then
    # check the unichain is exist
    check_exist_dir ${project_dir}

    #echo -e "Will delete the local unichain code and the unichain-archive.tar.gz."
    if [ ${unichain_exist} == 1 ]; then
        #echo -e "exist unichain and will delete it"
        echo_red "删除已存在的unichain代码"
        delete_code
    #else
    #   echo -e "not exist unichain"
    fi

fi

if [ "${update_local_code}" == true ]; then
    # check the unichain is exist
    check_exist_dir ${project_dir}

    #echo -e "Update the local unichain code and generate the unichain-archive.tar.gz."
    if [ ${unichain_exist} == 0 ]; then
        #echo -e "unichain代码不存在"
        download_code
        pack_code ${use_git}
    else
        #echo -e "unichain代码已存在"
        update_code ${use_git}
    fi
fi

if [ "${pack_local_code}" == true ]; then
    check_exist_dir ${project_dir}

    #echo -e "Update the local unichain code and generate the unichain-archive.tar.gz."
    if [ ${unichain_exist} == 0 ]; then
        #echo -e "not exist unichain and will download it"
        download_code
        pack_code ${use_git}
    else
        pack_code ${use_git}
    fi

fi

check_exist_file ${path_unichain_conf_file}
if [ "${re_download_template}" == true ]; then
    # if the template not exist, download

    if [ ${unichain_conf_file_exist} == 0 ]; then
        download_confile 0
    else
        download_confile 2
    fi
else
    download_confile ${unichain_conf_file_exist}
fi

exit 0
