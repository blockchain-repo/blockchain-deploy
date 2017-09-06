#! /bin/bash

# The set -e option instructs bash to immediately exit
# if any command has a non-zero exit status
set -e

function printErr()
{
     echo "usage: ./first_setup.sh <number_of_files>"
     echo "No argument $1 supplied"
}
##get it from ../conf/blockchain_nodes 
#if [ -z "$1" ]; then
#    printErr "<number_of_files>"
#    exit 1
#fi

if [[ $# -eq 1 && $1 == "nostart" ]];then
    AUTO_START_FLAG=0
else
    AUTO_START_FLAG=1
fi
source ./blockchain_nodes_conf_util.sh
source ./common_lib.sh

##check blocknodes_conf format
echo -e "[INFO]==========check cluster nodes conf=========="
check_cluster_nodes_conf || {
    echo -e "[ERROR] $FUNCNAME execute fail!"
    exit 1
}

echo -e "[INFO]==========cluster nodes info=========="
cat $CLUSTER_CHAINNODES_CONF|grep -vE "^#|^$"
echo -e ""

echo -e "[WARNING]please confirm cluster nodes info: [y/n]"
read cluster_str
if [ "`echo "$cluster_str"|tr A-Z  a-z`" == "y" -o "`echo "$cluster_str"|tr A-Z  a-z`" == "yes" ];then
     echo -e "[INFO]=========begin first_setup=========="
else
    echo -e "[ERROR]input invalid or cluster nodes info invalid"
    echo -e "[ERROR]=========first_setup aborted==========="
    exit 1
fi

CLUSTER_BIGCHAIN_COUNT=`get_cluster_nodes_num`
[ $CLUSTER_BIGCHAIN_COUNT -eq 0 ] && {
    echo -e "[ERROR] blockchain_nodes num is 0"
    exit 1
}

MODIFY_NODES_COUNT=`get_modify_nodes_num`
[ $MODIFY_NODES_COUNT -eq 0 ] && {
    echo -e "[ERROR] modify_nodes num is 0"
    exit 1
}

ALL_NODES=$[$CLUSTER_BIGCHAIN_COUNT+$MODIFY_NODES_COUNT]

#init env:python3 fabric3
echo -e "[INFO]=========init control machine env========="
./run_init_env.sh

#generate the unichain-archive.tar.gz
echo -e "[INFO]==========download and generate the unichain-archive.tar.gz=========="
./unichain_init.sh -p

echo -e "[INFO]=========check control machine deploy files is ok!========="
./run_pre_check.sh

echo -e "[INFO]=========check control machine deploy files is ok!========="
./run_pre_check.sh

#must remove old
echo -e "[INFO]==========init all nodes env=========="
fab init_all_nodes:shred=True,times=1,show=False,config_del=True

#collectd install&configure
echo -e "[INFO]==========install collectd========="
fab install_collectd
echo -e "[INFO]==========configure collectd========="
./configure_collectd.sh

#rethinkdb install&configure
echo -e "[INFO]==========install  rethinkdb=========="
fab install_rethinkdb
echo -e "[INFO]==========configure  rethinkdb=========="
./modify_rethinkdb.sh

#localdb install
echo -e "[INFO]==========install localdb=========="
fab install_localdb
#init localdb ,init the data store dirs /data/localdb_service_name/*
fab init_localdb

#unichain install&configure&init&shards&replicas
echo -e "[INFO]==========install unichain=========="
./install_unichain_archive.sh "local_tar_gz"

echo -e "[INFO]=========configure unichain========="
./modify_unichain.sh ${CLUSTER_BIGCHAIN_COUNT}

echo -e "[INFO]==========set shards unichain=========="
fab set_shards:${ALL_NODES}

echo -e "[INFO]==========set replicas unichain=========="
REPLICAS_NUM=`gen_replicas_num ${CLUSTER_BIGCHAIN_COUNT}`
fab set_replicas:${ALL_NODES}

#bak conf
echo -e "[INFO]==========bak current conf=========="
./bak_conf.sh "new"

if [[ -z $AUTO_START_FLAG || $AUTO_START_FLAG -eq 1 ]];then
    #start unichain nodes
    echo -e "[INFO]==========start unichain nodes=========="
    ./modify_clustercontrol.sh start
    ./modify_run_server_check.sh
else
    fab stop_rethinkdb
fi

exit 0
