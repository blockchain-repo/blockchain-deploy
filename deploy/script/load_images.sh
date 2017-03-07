#! /bin/bash

for i in $@
do
echo -e "[INFO]==========begin load "$i" images=========="
docker load --input $i
done
echo -e "[INFO]==========Done=========="
