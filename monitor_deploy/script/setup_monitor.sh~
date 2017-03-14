#!/bin/bash
set -e

echo -e "[INFO]==========Decompression tar package=========="
./decompression.sh
echo -e "[INFO]==========Done=========="
echo -e "  "

echo -e "[INFO]==========begin install docker tools=========="
./install_docker_local.sh
echo -e "[INFO]==========Done=========="
echo -e "  "

echo -e "[INFO]==========begin create nodes grafana query=========="
./add_nodes_json.sh
echo -e "[INFO]==========Done=========="
echo -e "  "

echo -e "[INFO]==========begin load docker images=========="
./load_images.sh futurever-docker-telegraf-statsd.tar hub.c.163.com-library-debian.tar tutum-influxdb.tar unichain_grafana.tar
echo -e "[INFO]==========Done=========="
echo -e "  "

echo -e "[INFO]==========begin start =========="
./start_monitor.sh
echo -e "[INFO]==========Done=========="
echo -e "  "

exit 0
