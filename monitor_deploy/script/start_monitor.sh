#!/bin/bash
set -e
# cp the default config for grafana-unichian-docker to /grafana/
mkdir -p /grafana
grafana_docker_config_files=../grafana-unichain-docker/defaults.ini
grafana_docker_config1_files=../grafana-unichain-docker/home.json
grafana_json_files1=../grafana-unichain-docker/grafana_json/uni-ledger-business.json
grafana_json_files2=../grafana-unichain-docker/grafana_json/uni-ledger-hardware1.json
grafana_json_files3=../grafana-unichain-docker/grafana_json/uni-ledger-hardware2.json

grafana_default_config_files=/grafana/defaults.ini
grafana_home_json_files=/grafana/home.json
grafana_json_file1=/grafana/uni-ledger-business.json
grafana_json_file2=/grafana/uni-ledger-hardware1.json
grafana_json_file3=/grafana/uni-ledger-hardware2.json

if [ ! -f ${grafana_default_config_files} ]; then
    cp -f ${grafana_docker_config_files} ${grafana_default_config_files}
fi

if [ ! -f ${grafana_home_json_files} ]; then
    cp -f ${grafana_docker_config1_files} ${grafana_home_json_files}
fi

if [ ! -f ${grafana_json_file1} ]; then
    cp -f ${grafana_json_files1} ${grafana_json_file1}
fi

if [ ! -f ${grafana_json_file2} ]; then
    cp -f ${grafana_json_files2} ${grafana_json_file2}
fi

if [ ! -f ${grafana_json_file3} ]; then
    cp -f ${grafana_json_files3} ${grafana_json_file3}
fi

echo -e "[INFO]==========Create containers and startup containers=========="
INFLUXDB_DATA=/monitor/data INIT_SCRIPT=$PWD/init_script.influxql docker-compose -f ../conf/docker-compose-monitor.yml up -d
echo -e "[INFO]==========Done=========="

echo -e "[INFO]==========Containers run status=========="
docker ps
# INFLUXDB_DATA=/monitor/data INIT_SCRIPT=$PWD/init_script.influxql docker-compose -f ../../docker-compose-monitor-dev.yml up
exit 0