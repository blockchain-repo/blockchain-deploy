#! /bin/bash
echo deb https://apt.dockerproject.org/repo ubuntu-trusty main > /etc/apt/sources.list.d/docker.list
apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D
apt-get update
apt-get -y --force-yes install docker-engine

pip3 install -U docker-compose==1.8.0

#pip3 install -U docker-compose
#wget -O /usr/local/bin/docker-compose https://github.com/docker/compose/releases/download/1.8.0/docker-compose-`uname -s`-`uname -m`
# curl -L "https://github.com/docker/compose/releases/download/1.8.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# cp the default config for grafana-unichian-docker to /grafana/
mkdir -p /grafana
grafana_docker_config_files=../../grafana-unichain-docker/defaults.ini
grafana_docker_config1_files=../../grafana-unichain-docker/home.json
grafana_default_config_files=/grafana/defaults.ini
grafana_home_json_files=/grafana/home.json

if [ ! -f ${grafana_default_config_files} ]; then
    cp -f ${grafana_docker_config_files} ${grafana_default_config_files}
    echo "not exit"
fi

if [ ! -f ${grafana_home_json_files} ]; then
    cp -f ${grafana_docker_config1_files} ${grafana_home_json_files}
    echo "not exit"
fi

INFLUXDB_DATA=/monitor/data INIT_SCRIPT=$PWD/init_script.influxql docker-compose -f ../../docker-compose-monitor.yml up
# INFLUXDB_DATA=/monitor/data INIT_SCRIPT=$PWD/init_script.influxql docker-compose -f ../../docker-compose-monitor-dev.yml up
