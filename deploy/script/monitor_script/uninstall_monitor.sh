#! /bin/bash

echo -e "[INFO]==========begin kill docker processes=========="
killall -9 docker*
echo -e "[INFO]==========Done=========="

echo -e "[INFO]==========begin delete docker container=========="
docker rm -f `docker ps -a -q`
echo -e "[INFO]==========Done=========="

echo -e "[INFO]==========begin delete docker container=========="
docker rmi `docker images -a`
echo -e "[INFO]==========Done=========="

echo -e "[INFO]==========begin uninstall docker=========="
apt-get autoremove docker-engine
echo -e "[INFO]==========Done=========="

echo -e "[INFO]==========begin uninstall docker-compose=========="
pip3 uninstall docker-compose
echo -e "[INFO]==========Done=========="


