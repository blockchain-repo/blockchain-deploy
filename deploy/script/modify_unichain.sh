#! /bin/bash

# The set -e option instructs bash to immediately exit
# if any command has a non-zero exit status
set -e

function printErr()
{
    echo "usage: ./configure_unichain.sh <number_of_files>"
    echo "No argument $1 supplied"
}

if [ -z "$1" ]; then
    printErr "<number_of_files>"
    exit 1
fi

CONFDIR=../conf/unichain_confiles
NUMFILES=$1

# If $CONFDIR exists, remove it
if [ -d "$CONFDIR" ]; then
    rm -rf $CONFDIR
fi

# Create $CONFDIR
mkdir $CONFDIR

UNICHAIN_TEMPLATE_FILE=../conf/template/unichain.conf.template

if [ ! -f "$UNICHAIN_TEMPLATE_FILE" ]; then
    echo "loss the config file $UNICHAIN_TEMPLATE_FILE "
    exit 1
fi

# Use the unichain configure command to create
# $NUMFILES BigchainDB config files in $CONFDIR
for (( i=0; i<$NUMFILES; i++ )); do
    CONPATH=$CONFDIR"/bcdb_conf"$i
    echo "Writing "$CONPATH
    cp $UNICHAIN_TEMPLATE_FILE $CONPATH
done


num_pairs=$1
NUM_NODES=$1

python3 write_keypairs_file.py $num_pairs
# 节点公钥备份
UNICHAIN_NODE_KEYRING=../conf
mkdir -p $UNICHAIN_NODE_KEYRING/keyring_bak
if [ -f "$UNICHAIN_NODE_KEYRING/keyring" ]; then
    datestr=`date +%Y-%m-%d-%H-%M`
    cp $UNICHAIN_NODE_KEYRING/keyring $UNICHAIN_NODE_KEYRING/keyring_bak/keyring_$datestr
fi
python3 unichain_keyrings_bak.py
python3 modify_clusterize_confiles.py -k $CONFDIR $NUM_NODES

# Send one of the config files to each instance
for (( HOST=0 ; HOST<$NUM_NODES ; HOST++ )); do
    CONFILE="bcdb_conf"$HOST
    echo "Sending "$CONFILE
    fab set_host:$HOST send_confile:$CONFILE
    fab -f fabfile_modify.py modify_node_confile
done


exit 0
