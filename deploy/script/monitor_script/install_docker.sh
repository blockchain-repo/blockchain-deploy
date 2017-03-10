#!/bin/bash
set -e

echo -e "[INFO]==========begin install docker=========="
echo deb https://apt.dockerproject.org/repo ubuntu-trusty main > /etc/apt/sources.list.d/docker.list
apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D
apt-get update
apt-get -y --force-yes install docker-engine
echo -e "[INFO]==========Done=========="

#Mode A:pip3 install docker-compose
#echo -e "[INFO]==========begin install docker-compose=========="
#pip3 install -U docker-compose==1.8.0
#echo -e "[INFO]==========Done=========="

#Mode B:wget install docker-compose
echo -e "[INFO]==========begin install docker-compose=========="
wget -O /usr/local/bin/docker-compose https://github.com/docker/compose/releases/download/1.8.0/docker-compose-`uname -s`-`uname -m`
# curl -L "https://github.com/docker/compose/releases/download/1.8.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
echo -e "[INFO]==========Done=========="
exit 0