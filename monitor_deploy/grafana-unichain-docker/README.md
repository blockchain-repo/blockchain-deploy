# Grafana Docker image

## Env
```
sudo apt-get install python3-pip
```

## Install
```
sudo bash setu_up.sh
```

## added the docker volumes files

- 1. added the files to docker dir

- 2. modify the set_up.sh and added the ops

- 3. added the statement in docker-compose-monitor.yml

## start
```
INFLUXDB_DATA=/monitor/data INIT_SCRIPT=$PWD/init_script.influxql docker-compose -f ../docker-compose-monitor.yml up
```
