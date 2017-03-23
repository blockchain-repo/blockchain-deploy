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

`Fabric3` install maybe need:

```
sudo apt-get -y install git gcc g++ python3-dev libssl-dev libffi-dev python3-setuptools \
python3-pip ntp screen

sudo pip3 install --upgrade pip
sudo pip3 install --upgrade setuptools

sudo pip3 install fabric3
```

### 2. 下载部署项目
```
git clone https://git.oschina.net/uni-ledger/unichain_deploy.git
```

### 3. 源更新

如果控制机源未修改，建议修改后再操作，源配置文件参考 /sources/ 下 `sources.list` `pip.conf`

或者执行 `fab local_update_apt_pip`

### 4. 下载unichain
```
cd unichain_deploy/deploy/script/

# 运行 脚本下载或更新 unichain 至 /deploy/sources/ 下
bash build.sh unichain_init -du

# 生成 unichain-archive.tar.gz 并拷贝至 /sources/ 下
```
最终 sources/下文件及目录如下：
`unichain-archive.tar.gz` `unichain` `unichain.conf.template` `sources.list` `pip.conf` ...

### 5. 更新unichain
```
bash build.sh unichain_init -up
```

### 6. 集群安装 unichain
```
#配置节点信息
vi conf/blockchain_nodes

bash build.sh first_setup

```

### 7. 集群更新 unichain
```
bash build.sh update
```

### 8. unichain_init.sh 说明
```
Usage:
    $0 [-g -b branch_name -s https://xxx.com -udp]
Options:
    -h  使用帮助
    -g  使用git方式对代码进行更新打包
    -b  git方式操作对应的分支
    -s  下载代码仓库地址
    -u  更新代码，如果不存在则使用git方式下载代码
    -p  对代码进行打包，生成unichain-archive.tar.gz，并copy至sources下
        如果选择git方式打包，则使用git archive, 否则默认为tar & gzip 打包
    -d  删除下载的unichain代码及生成的unichain-archive.tar.gz文件

```

