# Deploy for unichain

## app 配置
```
app 配置文件位置 deploy/conf/__init__.py

_app_config

```

## 1. Install
```
安装程序，将自动安装 Fabric3
```

## 2. 更新节点源配置

源配置在`deploy/sources`下，apt配置为`sources.list`, pip配置为`pip.conf`

## 3. 检查应用基本配置模板及安装包

- 检测配置模板文件 `deploy/conf/template/nichain.conf.template` 是否存在
- 检测程序安装包文件 `deploy/sources/unichain-archive.tar.gz` 是否存在

## 4. 安装或更新操作
在执行安装或更新操作前，请务必先执行获取模板及安装包的操作！
执行脚本 `run_pre_check.sh` 根据提示获取相关文件即可！

