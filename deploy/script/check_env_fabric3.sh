#!/usr/bin/env bash

source ./check_tools_util.sh
echo -e "[INFO]=======check fabric_3 begin======="
fabric_3=`check_fabric_3`
if [ -z "$fabric_3" ];then
    echo "Fabric Not installed"
else
    echo "Fabric Has been installed"
fi
echo -e "[INFO]=======check fabric_3 end======="
echo -e " "


