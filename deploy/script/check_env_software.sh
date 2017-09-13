#!/usr/bin/env bash

source ./check_tools_util.sh
echo -e "[INFO]=======check python_3 begin======="
python_3=`check_python_3`
if [ -z "$python_3" ];then
    echo "Python Not installed"
else
    echo "Python Has been installed"
fi
echo -e "[INFO]=======check python_3 end======="
echo -e ""

echo -e "[INFO]=======check collectd begin======="
collectd_version=`check_collectd`

if [ -z "$collectd_version" ];then
    echo "Collectd Not installed"
else
    echo "Collectd Has been installed"
fi
echo -e "[INFO]=======check docker end======="
echo -e ""




if [ -z "$python_3" ]  && [ -z "$collectd_version" ];then
    echo "ready go!"
else
    echo "please install python3 collectd tools"
fi

