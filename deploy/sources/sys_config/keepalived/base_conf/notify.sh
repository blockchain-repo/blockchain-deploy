#!/bin/bash
#description: An example of notify script

vip={vip}
contact='278810732@qq.com wx_cs_db_88@163.com'
host_info="`hostname`(`hostname -I`)"
senduser= "-- -`hostname -a`"
notify(){
    mail_subject="`hostname` to be $1: $vip floating"
    mail_body="`date '+%F %H:%M:%S'`: vrrp transition, ${host_info} changed to be $1"
    echo $mail_body | mail -s "$mail_subject" $contact ${senduser}
}
case "$1" in
    master)
        notify master
         /etc/init.d/nginx start
        exit 0
    ;;
    backup)
        notify backup
         /etc/init.d/nginx stop
        exit 0
    ;;
    fault)
        notify fault
         /etc/init.d/nginx stop
        exit 0
    ;;
    stop)
        notify stop
        /etc/init.d/nginx stop
        exit 0
    ;;
    *)
        echo 'Usage: `basename $0` {master|backup|fault}'
        exit 1
    ;;
esac