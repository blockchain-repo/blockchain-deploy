#!/bin/sh
set -e
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
echo   "$hostaname 硬件信息报告：" >> env_node_$hostaname
echo   " " >> env_node_$hostaname
echo   "系统操作信息：$system" >> env_node_$hostaname
echo   " " >> env_node_$hostaname
echo   "内核版本：$kernel" >> env_node_$hostaname
echo   " " >> env_node_$hostaname
echo   "cpu数量：$cpu_number 个" >> env_node_$hostaname
echo   " " >> env_node_$hostaname
echo   "cpu物理核心数：$cpu_kernel 个" >> env_node_$hostaname
echo   " " >> env_node_$hostaname
echo   "cpu逻辑核心数：$cpu_thread 个" >> env_node_$hostaname
echo   " " >> env_node_$hostaname
echo   "内存容量：$memory_g KB" >> env_node_$hostaname
echo   " " >> env_node_$hostaname
echo   "网卡数量：$net_number 个" >> env_node_$hostaname
echo   " " >> env_node_$hostaname
echo   "磁盘容量：$disk GB" >> env_node_$hostaname

exit 0
