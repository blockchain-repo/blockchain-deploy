# Deploy for unichain

## app 配置
```
app 配置文件位置 deploy/conf/__init__.py
```

## 1. Install
```
安装程序，将自动安装 Fabric3
```

## 2. 更新节点源配置

源配置在`deploy/sources`下，apt配置为`sources.list`, pip配置为`pip.conf`

## 3. 获取应用基本配置模板及安装包

- 获取配置文件模板并放到`deploy/conf/template/`下，命名为`unichain.conf.template`
- 获取程序安装包并放到`deploy/sources/`下，命名为`unichain-archive.tar.gz`

## 4. 安装或更新操作
在执行安装或更新操作前，请务必先执行获取模板及安装包的操作！
执行脚本 `run_pre_check.sh` 根据提示获取相关文件即可！

