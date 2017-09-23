#!/usr/bin/env bash

function get_all_python
{
    for p_python in `whereis python|sed "s/$/ /g"|grep -oE "/[a-zA-Z/]+/bin/python[.0-9]+[ ]+"|sort -u`
    do
        bin_python=`echo -e "$p_python"|awk -F"/" '{print $NF}'`
        #v_cmd_python="${bin_python} --version"
        echo -e "$bin_python|$p_python"
    done
    return 0
}

function check_python_3
{
    for t_line in `get_all_python`
    do
        bin_python=`echo $t_line|awk -F"|" '{print $1}'`
        if [ ! -z `echo $bin_python|grep "python3"` ];then
            echo $bin_python
            return 0
        fi
    done
    return 1
}

function get_python_bin_path
{
    local python_bin=$1
    if [ -z $python_bin ];then
        return 1
    fi
    whereis $python_bin|sed "s/$/ /g"|grep -o "/[a-zA-Z/]+/bin/${python_bin} "
    return 0
}

function check_pip_3
{
    local pip_3_version=`pip3 --version|grep -i "/usr/"`
    if [ ! -z "$pip_3_version" ];then
        echo $pip_3_version
        return 0
    fi
    return 1
}

function check_fabric_3
{
    local fab_version=`fab --version|grep -i "fabric3"`
    if [ ! -z "$fab_version" ];then
        echo $fab_version
        return 0
    fi
    return 1
}

function check_collectd
{
    local collectd_process=`ps -e |grep collectd`
    if [ ! -z "$collectd_process" ];then
        echo $collectd_process
        return 0
    fi
    return 1
}
#############################检查节点硬件信息###################################
#获取操作系统信息
system=`lsb_release -a|grep "Description"|awk '{print $2,$3,$4}'`
#获取内核版本
kernel=`cat /proc/version|awk '{print $1,$2,$3}'`
#获取cpu数量
cpu_number=`cat /proc/cpuinfo| grep "physical id"| sort| uniq| wc -l`
#获取cpu物理核心数
cpu_kernel=`cat /proc/cpuinfo| grep "cpu cores"| uniq|awk '{print $4}'`
#获取cpu逻辑核心数
cpu_thread=`cat /proc/cpuinfo| grep "processor"| wc -l`
#获取内存容量
memory=`cat /proc/meminfo|grep "MemTotal"|awk '{print $2}'`
((memory_g=$memory/1024))
#获取网卡数量
net_number=`cat /proc/net/dev|grep "eth"|wc -l`
#获取磁盘容量
disk=`fdisk -l|head -2|awk '{print $3}'|sed /^$/d`
#获取该节点主机名
hostaname=`hostname`
echo   " " >> env_node_$hostaname.txt
echo   "==============节点( $hostaname )系统配置检查开始================= " >>  env_node_$hostaname.txt
echo   " " >> env_node_$hostaname.txt
echo -e  "硬件信息报告：" >> env_node_$hostaname.txt
echo   " " >> env_node_$hostaname.txt
echo   "    系统操作信息：$system" >> env_node_$hostaname.txt
echo   " " >> env_node_$hostaname.txt
echo   "    内核版本：$kernel" >> env_node_$hostaname.txt
echo   " " >> env_node_$hostaname.txt
echo   "    cpu数量：$cpu_number 个" >> env_node_$hostaname.txt
echo   " " >> env_node_$hostaname.txt
echo   "    cpu物理核心数：$cpu_kernel 个" >> env_node_$hostaname.txt
echo   " " >> env_node_$hostaname.txt
echo   "    cpu逻辑核心数：$cpu_thread 个" >> env_node_$hostaname.txt
echo   " " >> env_node_$hostaname.txt
echo   "    内存容量：$memory_g KB" >> env_node_$hostaname.txt
echo   " " >> env_node_$hostaname.txt
echo   "    网卡数量：$net_number 个" >> env_node_$hostaname.txt
echo   " " >> env_node_$hostaname.txt
echo   "    磁盘容量：$disk GB" >> env_node_$hostaname.txt

#############################检查节点服务环境信息###################################
echo   " " >> env_node_$hostaname.txt
#获取该节点主机名
hostaname=`hostname`
echo   "节点服务环境安装信息报告：" >> env_node_$hostaname.txt
echo   " " >> env_node_$hostaname.txt

echo -e "[INFO]=======check python_3 begin======="
python_3=`check_python_3`
if [ -z "$python_3" ];then
    echo "Python Not installed"
    echo   "    python_3：未安装" >> env_node_$hostaname.txt
    echo   " " >>  env_node_$hostaname.txt
else
    echo "Python Has been installed"
    echo   "    python_3：已安装" >> env_node_$hostaname.txt
    echo   " " >>  env_node_$hostaname.txt
fi
echo -e "[INFO]=======check python_3 end======="
echo -e ""

echo -e "[INFO]=======check pip_3 begin======="
pip_3=`check_pip_3`
if [ -z "$pip_3" ];then
    echo "pip_3 Not installed"
    echo   "    pip_3：未安装" >> env_node_$hostaname.txt
    echo   " " >>  env_node_$hostaname.txt
else
    echo "pip_3 Has been installed"
    echo   "    pip_3：已安装" >> env_node_$hostaname.txt
    echo   " " >>  env_node_$hostaname.txt
fi
echo -e "[INFO]=======check pip_3 end======="
echo -e ""

echo -e "[INFO]=======check collectd begin======="
collectd_version=`check_collectd`

if [ -z "$collectd_version" ];then
    echo "Collectd Not installed"
    echo   "    collectd：未安装" >> env_node_$hostaname.txt
    echo   " " >>  env_node_$hostaname.txt
else
    echo "Collectd Has been installed"
    echo   "    collectd：已安装" >> env_node_$hostaname.txt
    echo   " " >>  env_node_$hostaname.txt
fi
echo -e "[INFO]=======check docker end======="
echo -e ""

if [ ! -z "$python_3" ]  && [ ! -z "$collectd_version" ] && [ ! -z "$pip_3" ];then
   echo "ready go!"
    echo   "基本环境安装已ok，请开始下一步操作！" >> env_node_$hostaname.txt
    echo   " " >>  env_node_$hostaname.txt
else
    echo "please install python3 fabric_3 tools"
    echo   "注意：python_3,pip_3或fabric_3未安装，请安装服务基本环境！" >> env_node_$hostaname.txt
    echo   " " >>  env_node_$hostaname.txt
fi


#############################检查节点区块链服务信息###################################
#获取该节点主机名
hostaname=`hostname`
echo   "区块链服务安装信息报告：" >> env_node_$hostaname.txt
echo   " " >> env_node_$hostaname.txt

rethinkdb_number=`ps -aux|grep -E "/usr/bin/rethinkdb"|grep -v grep|wc -l`
if [ $rethinkdb_number -eq 0 ];then
    echo   "    rethinkdb 进程数为：0" >> env_node_$hostaname.txt
    echo   " " >> env_node_$hostaname.txt
else
    echo   "    rethinkdb 进程数为：$rethinkdb_number" >> env_node_$hostaname.txt
    echo   " " >> env_node_$hostaname.txt
fi

driver_port=`netstat -nlap|grep "28015"`
if [ -z $driver_port ];then
    echo   "    rethinkdb：28015未被使用" >> env_node_$hostaname.txt
    echo   " " >> env_node_$hostaname.txt
else
    echo   "    rethinkdb：28015已被使用" >> env_node_$hostaname.txt
    echo   " " >> env_node_$hostaname.txt
fi
cluster_port=`netstat -nlap|grep "29015"`
if [ -z $cluster_port ];then
    echo   "    rethinkdb：29015未被使用" >> env_node_$hostaname.txt
    echo   " " >> env_node_$hostaname.txt
else
    echo   "    rethinkdb：29015已被使用" >> env_node_$hostaname.txt
    echo   " " >> env_node_$hostaname.txt
fi
http_port=`netstat -nlap|grep "8080"`
if [ -z $http_port ];then
    echo   "    rethinkdb：8080未被使用" >> env_node_$hostaname.txt
    echo   " " >> env_node_$hostaname.txt
else
    echo   "    rethinkdb：8080已被使用" >> env_node_$hostaname.txt
    echo   " " >> env_node_$hostaname.txt
fi
unichain_number=`ps -aux|grep -E "/usr/local/bin/unichain -y start|SCREEN -d -m unichain -y start"|grep -v grep|wc -l`
if [ $unichain_number -eq 0 ];then
    echo   "    unichain 进程数为：0" >> env_node_$hostaname.txt
    echo   " " >> env_node_$hostaname.txt
else
    echo   "    unichain 进程数为：$unichain_number" >> env_node_$hostaname.txt
    echo   " " >> env_node_$hostaname.txt
fi
unichain_port=`netstat -nlap|grep "9984"`
if [ -z $unichain_port ];then
    echo   "    unichain：9984未被使用" >> env_node_$hostaname.txt
    echo   " " >> env_node_$hostaname.txt
else
    echo   "    unichain：9984已被使用" >> env_node_$hostaname.txt
    echo   " " >> env_node_$hostaname.txt
fi

if [ $rethinkdb_number -gt 0 ] && [ $unichain_number -gt 0 ] && [ ! -z "$driver_port" ]  && [ ! -z "$cluster_port" ] && [ ! -z "$http_port" ] && [ ! -z "$driver_port" ];then
   echo "ready go!"
    echo   "区块链服务安装已ok，请开始下一步操作！" >> env_node_$hostaname.txt
    echo   " " >>  env_node_$hostaname.txt
else
    echo "please install python3 fabric_3 tools"
    echo   "注意：unichain或rethinkdb未安装，请安装服务！" >> env_node_$hostaname.txt
    echo   " " >>  env_node_$hostaname.txt
fi
echo   "==============节点( $hostaname )系统配置检查结束================= " >>  env_node_$hostaname.txt







