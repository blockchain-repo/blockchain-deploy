#! /bin/bash

set -e

for i in $@
do
echo -e "[INFO]==========begin load "$i" images=========="
docker load --input $i
done
echo -e "[INFO]==========Done=========="

echo -e "[INFO]==========images list=========="
docker images
echo -e "[INFO]==========Done=========="

exit 0