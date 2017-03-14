#!/bin/bash

echo -e "[INFO]==========begin install git=========="
cd deb/git
dpkg -i *.deb
git
echo -e "[INFO]==========Done=========="
echo -e "  "

echo -e "[INFO]==========begin install pip3=========="
cd ../pip3
dpkg -i *.deb
pip3
echo -e "[INFO]==========Done=========="
echo -e "  "

echo -e "[INFO]==========begin install docker=========="
cd ../docker
dpkg -i *.deb
docker
echo -e "[INFO]==========Done=========="
echo -e "  "

echo -e "[INFO]==========begin install docker-compose=========="
echo -e "    "
echo -e "[INFO]==========begin copy python packages=========="
cd ../docker_compose_package/dist-packages
cp -r ./ /usr/local/lib/python3.4/dist-packages
cd ../../
cp docker-compose /usr/local/bin
chmod +x /usr/local/bin/docker-compose
cd ..
docker-compose
echo -e "[INFO]==========Done=========="
echo -e "  "

