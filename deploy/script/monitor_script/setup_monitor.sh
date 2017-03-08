#!/bin/bash

echo -e "[INFO]==========begin install docker tools=========="
./install_docker_pip3.sh
echo -e "[INFO]==========Done=========="

echo -e "[INFO]==========begin load docker images=========="
./load_images.sh futurever-docker-telegraf-statsd.tar hub.c.163.com-library-debian.tar tutum-influxdb.tar unichain_grafana.tar
echo -e "[INFO]==========Done=========="

echo -e "[INFO]==========begin start =========="
./start_monitor.sh
echo -e "[INFO]==========Done=========="

