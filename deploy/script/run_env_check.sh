#!/bin/bash

set -e

#check hardinfo
echo -e "[INFO]==========check hardinfo=========="
fab check_hardinfo

#check python3  collectd fabric3
echo -e "[INFO]==========check python3 fabric3 and collectd=========="
fab check_env_software

#check rethinkdb
echo -e "[INFO]==========check rethinkdb=========="
fab check_rethinkdb

##check localdb
#echo -e "[INFO]==========check localdb=========="
#fab check_localdb

#check unichain-pro
echo -e "[INFO]==========check unichain pro=========="
fab check_unichain

exit 0
