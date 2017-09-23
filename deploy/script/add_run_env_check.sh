#!/bin/bash

set -e
env_check_report="env_check_report.txt"
report="../report"
if [ "`ls -A $report`"="" ];then
    rm -rf ../report/*
fi

if [ -d "$env_check_report" ];then
    rm -f $env_check_report
fi
#check control
echo -e "[INFO]==========check control=========="
./check_env_master.sh

##check hardinfo
#echo -e "[INFO]==========check node info=========="
fab check_node_info
fab -f fabfile_modify.py check_node_info
touch $env_check_report
hostname=`hostname`
for file in ../report/*
do
    if test -f $file
    then
        testfile=$file
        x=`wc -l $testfile |awk '{print $1}'`
        i=1
        while [ $i -le $x ]
        do
            echo "`head -$i  $testfile | tail -1`" >> $env_check_report
            i=`expr $i + 1`
        done
#        cat $file | while read LINE
#        do
#            echo $LINE >> $env_check_report
#        done
    fi
done

mv $env_check_report ../report/
exit 0
