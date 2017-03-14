#! /bin/bash
set -e

echo -e "[INFO]==========begin kill docker processes=========="
killall -9 docker*
echo -e "[INFO]==========Done=========="

echo -e "[INFO]==========begin delete docker container=========="
docker rm -f `docker ps -a -q`
echo -e "[INFO]==========Done=========="

echo -e "[INFO]==========begin delete docker container=========="
docker rmi `docker images -a`
echo -e "[INFO]==========Done=========="

echo -e "[INFO]==========begin uninstall git=========="
dpkg --purge git
echo -e "[INFO]==========Done=========="

echo -e "[INFO]==========begin uninstall docker=========="
dpkg --purge docker-engine
echo -e "[INFO]==========Done=========="

echo -e "[INFO]==========begin uninstall pip3=========="
dpkg --purge pip3
echo -e "[INFO]==========Done=========="

echo -e "[INFO]==========begin uninstall docker-compose=========="
rm /usr/local/bin/docker-compose
echo -e "[INFO]==========Done=========="

exit 0
