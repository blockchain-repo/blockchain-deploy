# -*- coding: utf-8 -*-
import os
import json
from copy import deepcopy

## 定义数据字典
node_dict = {}

## 获取当前目录路径信息
old_cwd = os.getcwd()
## 切换目录
conf_path = os.chdir("../report/conf")

## 获取所有节点配置文件
node_conf_lists = os.listdir("./")
for node_conf in node_conf_lists:
    conf_file= open(node_conf)
    try:
        keyring_list = []
        conf_str = conf_file.read()
        unichain_dict = json.loads(conf_str)
        public_key = unichain_dict["keypair"]["public"]
        keyring = unichain_dict["keyring"]
        for key in keyring:
            keyring_list.append(key)
        keyring_list.append(public_key)
        node_dict[node_conf] = keyring_list
    finally:
        conf_file.close()

temp_dict = deepcopy(node_dict)
## 定义判断所有公钥环是否一致标志
all_node_flag = True
for key1 in node_dict:
    keyring1 = node_dict[key1]
    ## 定义判节点公约环是否一致标志
    del temp_dict[key1]
    for key2 in temp_dict:
        keyring2 = node_dict[key2]
        for pub_key in keyring1:
            if pub_key in keyring2:
                continue
            else:
                all_node_flag = False
                print("\033[0;31m%s\033[0m" % "{} 节点与 {} 节点公钥环不一致，请及时处理！！！".format(key1, key2))
                break

if all_node_flag:
    print("\033[0;34m%s\033[0m" % "所有节点公钥环一致，请继续其他操作！！")


