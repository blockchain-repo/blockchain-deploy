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

while [ 1 -eq 1 ]
do
    if [ ! -f $CLUSTER_UNICHAIN_TEMPLATE_CONF ]; then
        echo -e "\033[31m conf/template/$filename_templeate_conf not exist!\033[0m"
        echo -e "Please choose the way to get the file($filename_templeate_conf)"
        echo -e "1. wget from url"
        echo -e "2. specify it manually"
        echo -en "you choose(1 or 2): "
        read choose
        if [ -n "$choose" ];then
            if [ $choose == "1" ]; then
                echo -en "Please input the url= "
                read url
                filename=${url##*/}
                if [ -n "$filename" ] && [ "$filename" == "$filename_templeate_conf" ]; then
                    wget -P ${CUR_PATH}/../conf/template/ $url
                else
                	echo -e "\033[31m suffix of the url($filename) must be equal the filename($filename_templeate_conf)! \033[0m\n"
                fi
            elif [  $choose == "2" ]; then
                echo -e "Please copy or write file into it, and then input (yes or y) continue!"
                echo -en "input(yes or y)= "
                read input1
                if [ -n "$input1" ] && [ $input1 != "yes" -a  $input1 != "y" ]; then
                    echo "input must be yes or y !"
                fi
            else
                echo "error input, you should input in 1 or 2 !"

            fi
         else
            echo "input is null!"
         fi
     else
         echo -e "\033[32m conf/template/${filename_templeate_conf} exist!\033[0m\n"
         break
     fi
done

while [ 1 -eq 1 ]
do
    if [ ! -f $CLUSTER_APP_TAR_GZ ]; then
        echo -e "\033[31m conf/template/$filename_app_tar_gz not exist!\033[0m"
        echo -e "Please choose the way to get the file($filename_app_tar_gz)"
        echo -e "1. wget from url"
        echo -e "2. specify it manually"
        echo -en "you choose(1 or 2): "
        read choose
        if [ -n "$choose" ];then
            if [ $choose == "1" ]; then
                echo -en "Please input the url= "
                read url
                filename=${url##*/}
                if [ -n "$filename" ] && [ "$filename" == "$filename_app_tar_gz" ]; then
                    wget -P ${CUR_PATH}/../sources/ $url
                else
                	echo -e "\033[31m suffix of the url($filename) must be equal the filename($filename_app_tar_gz)! \033[0m\n"
                fi
            elif [  $choose == "2" ]; then
                echo -e "Please copy or write file into it, and then input (yes or y) continue!"
                echo -en "input(yes or y)= "
                read input1
                if [ -n "$input1" ] && [ $input1 != "yes" -a  $input1 != "y" ]; then
                    echo "input must be yes or y !"
                fi
            else
                echo "error input, you should input in 1 or 2 !"

            fi
         else
            echo "input is null!"
         fi
     else
     	 echo -e "\033[32m sources/${filename_app_tar_gz} exist!\033[0m\n"
         break
     fi
done
exit 0
