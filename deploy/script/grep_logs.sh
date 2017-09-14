#!/bin/sh
fab get_logs
cd /tmp/remote_log
if  [ ! -n "$1" ] ;then
    grep -r ''
else
    grep -r "$1"
fi
