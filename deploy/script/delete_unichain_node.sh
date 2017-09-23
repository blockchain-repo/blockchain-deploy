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

ALL_NODES=$[$CLUSTER_BIGCHAIN_COUNT-$MODIFY_NODES_COUNT]

#init env:python3 fabric3
echo -e "[INFO]=========init control machine env========="
./run_init_env.sh


echo -e "[INFO]==========configure  rethinkdb=========="
fab -f fabfile_modify.py stop_rethinkdb
./configure_rethinkdb_norestart.sh

echo -e "[INFO]=========configure unichain========="
fab -f fabfile_modify.py stop_unichain
fab -f fabfile_modify.py delete_node_confile
fab modify_node_confile

echo -e "[INFO]==========set replicas unichain=========="
REPLICAS_NUM=`gen_replicas_num ${CLUSTER_BIGCHAIN_COUNT}`
fab set_shards:${CLUSTER_BIGCHAIN_COUNT}
fab set_replicas:${CLUSTER_BIGCHAIN_COUNT}
fab set_shards:${CLUSTER_BIGCHAIN_COUNT}
echo -e "[INFO]==========set shards unichain=========="

#bak conf
echo -e "[INFO]==========bak current conf=========="
./bak_conf.sh "new"

if [[ -z $AUTO_START_FLAG || $AUTO_START_FLAG -eq 1 ]];then
    #start unichain nodes
    echo -e "[INFO]==========start unichain nodes=========="
    for (( i=0; i<$CLUSTER_BIGCHAIN_COUNT; i++ )); do
            fab set_host:$i stop_unichain
            fab set_host:$i start_unichain
    done
    ./run_server_check.sh
else
    fab stop_rethinkdb
fi

exit 0
