#!/bin/bash

echo -e "[INFO]==========stop and delete docker container=========="
docker rm -f `docker ps -a -q`
echo -e "[INFO]==========Done=========="

