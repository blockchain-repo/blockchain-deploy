#! /bin/bash

# The set -e option instructs bash to immediately exit
# if any command has a non-zero exit status
set -e

CUR_INSTALL_PATH=$(cd "$(dirname "$0")"; pwd)
cd ../sources
rm -rf ./unichain
git clone http://36.110.71.170:99/unichain/unichain.git

tar -zcvf unichain-archive.tar.gz ./unichain
cp ../sources/unichain-archive.tar.gz ../script/
cd ../script

fab update_unichain_from_archive

rm -f ${CUR_INSTALL_PATH}/unichain-archive.tar.gz 2>/dev/null
