# Deploy for unichain

## app 配置
```
app 配置文件位置 deploy/conf/__init__.py

_app_config

可以修改部署的程序 服务名、端口、安装名
```

## 1. Install
```
控制机需要安装Fabric3
```

## 2. 更新节点源配置

源配置在`deploy/sources`下，apt配置为`sources.list`, pip配置为`pip.conf`

## 3. 检查应用基本配置模板及安装包

- 检测配置模板文件 `deploy/conf/template/unichain.conf.template` 是否存在
- 检测程序安装包文件 `deploy/sources/unichain-archive.tar.gz` 是否存在

## 4. 安装或更新操作
在执行安装或更新操作前，请务必先执行获取模板及安装包的操作！

代码下载或更新 `unichain_init.sh`

节点安装
run_first_setup.sh

节点更新
run_update.sh




