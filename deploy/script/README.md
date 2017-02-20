# Deploy for unichain


## unichain 配置文件
```
配置文件位置 deploy/conf/__init__.py

默认值，如下：
server_port: 9984,
restore_server_port: 9986,
service_name: 'unichain',
setup_name: 'UnichainDB',
db_name:'bigchain'

```
## 操作说明

### 1. 控制机环境
`Python3.4+`, `Fabric3`, `git`, `ssh`

### 2. 下载部署项目
```
git clone https://git.oschina.net/wxcsdb88/unichain_deploy.git
```

### 3. 源更新

如果控制机源未修改，建议修改后再操作，源配置文件参考 /sources/ 下 `sources.list` `pip.conf`

或者执行 `fab local_update_apt_pip`

### 4. 下载unichain
```
cd unichain_deploy/deploy/script/

# 运行 脚本下载或更新 unichain 至 /deploy/sources/ 下
bash unichain_init.sh

# 生成 unichain-archive.tar.gz 并拷贝至 /sources/ 下
```
最终 sources/下文件及目录如下：
`unichain-archive.tar.gz` `unichain` `unichain.conf.template` `sources.list` `pip.conf` ...

### 5. 更新unichain
```
bash unichain_init.sh update
```

### 6. 集群安装 unichain
```
#配置节点信息
vi conf/blockchain_nodes

bash run_first_setup.sh

```

### 7. 集群更新 unichain
```
bash run_update.sh
```





