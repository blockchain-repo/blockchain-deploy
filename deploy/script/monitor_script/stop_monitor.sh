#!/bin/bash
set -e

echo -e "[INFO]==========stop and delete docker container=========="
docker rm -f `docker ps -a -q`
echo -e "[INFO]==========Done=========="

exit 0