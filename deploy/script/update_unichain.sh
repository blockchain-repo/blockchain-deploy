#! /bin/bash

# The set -e option instructs bash to immediately exit
# if any command has a non-zero exit status
set -e

CONFDIR=../conf/unichain_confiles

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

CONPATH=$CONFDIR"/bcdb_conf"1
echo "Writing "$CONPATH
cp $UNICHAIN_TEMPLATE_FILE $CONPATH

NUM_NODES=$1
for (( HOST=0 ; HOST<$NUM_NODES ; HOST++ )); do
fab set_host:$HOST update_unichain_config:$HOST
done

exit 0
