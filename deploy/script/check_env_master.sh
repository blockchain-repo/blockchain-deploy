#!/usr/bin/env bash

source ./check_tools_util.sh
#获取该节点主机名
hostaname=`hostname`
echo   "$hostaname 中控机服务环境安装信息报告：" >> ../report/env_master_$hostaname
echo   " " >>  ../report/env_master_$hostaname
echo -e "[INFO]=======check python_3 begin======="
python_3=`check_python_3`
if [ -z "$python_3" ];then
    echo "Python Not installed"
    echo   "python_3：未安装" >> ../report/env_master_$hostaname
    echo   " " >>  ../report/env_master_$hostaname
else
    echo "Python Has been installed"
    echo   "python_3：已安装" >> ../report/env_master_$hostaname
    echo   " " >>  ../report/env_master_$hostaname
fi
echo -e "[INFO]=======check python_3 end======="
echo -e ""

echo -e "[INFO]=======check fabric_3 begin======="
fabric_3=`check_fabric_3`
if [ -z "$fabric_3" ];then
    echo "Fabric Not installed"
    echo   "fabric_3：未安装" >> ../report/env_master_$hostaname
    echo   " " >>  ../report/env_master_$hostaname
    echo ""
else
    echo "Fabric Has been installed"
    echo   "fabric_3：已安装" >> ../report/env_master_$hostaname
    echo   " " >>  ../report/env_master_$hostaname
fi
echo -e "[INFO]=======check fabric_3 end======="
echo -e " "

if [ ! -z "$python_3" ]  && [ ! -z "$fabric_3" ];then
    echo "ready go!"
    echo   "中控节点基本环境安装已ok，请开始下一步操作！" >> ../report/env_master_$hostaname
    echo   " " >>  ../report/env_master_$hostaname
else
    echo "please install python3 fabric_3 tools"
    echo   "中控节点python_3或fabric_3未安装，请安装服务基本环境！" >> ../report/env_master_$hostaname
    echo   " " >>  ../report/env_master_$hostaname
fi
