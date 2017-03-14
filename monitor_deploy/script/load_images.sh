#! /bin/bash

set -e

cd unichain
for i in $@
do
echo -e "[INFO]==========begin load "$i" images=========="
docker load --input $i
done
echo -e "[INFO]==========Done=========="
cd ..
echo -e "[INFO]==========images list=========="
docker images
echo -e "[INFO]==========Done=========="

exit 0
