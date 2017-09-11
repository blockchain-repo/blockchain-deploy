# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import os
import sys

from hostlist import public_hosts
from monitor_server import gMonitorServer
from multi_apps_conf import app_config

nodeIp = sys.argv[1]
unichain_confiles = os.getcwd()

os.chdir("../script")
unichain_conf = os.getcwd()
# 获取原有节点公钥环,重新装配节点公钥环
conf_files = unichain_conf + "/unichain_conf"
print(conf_files)
with open(conf_files, 'r') as f:
    conf_dict = json.load(f)
    old_pubkeys = conf_dict['keyring']
    pubkey = conf_dict['keypair']['public']
    privatekey = conf_dict['keypair']['private']
    keyrings = conf_dict['keyring']


os.chdir("../conf/unichain_confiles")
new_conf_path = os.getcwd()
# 获取最新的配置信息
new_conf_path = new_conf_path+"/bcdb_conf1"
with open(new_conf_path, 'r') as f:
    new_conf_dict = json.load(f)
    new_conf_dict['keypair']['private'] = privatekey
    new_conf_dict['keypair']['public'] = pubkey
    # The keyring is the list of *all* public keys
    # minus the base_conf file's own public key
    keyring = list(keyrings)
    new_conf_dict['keyring'] = keyring
    # Allow incoming server traffic from any IP address
    # to port 9984
    new_conf_dict['server']['bind'] = '0.0.0.0:{}'.format(app_config['server_port'])
    # Set the api_endpoint
    new_conf_dict['api_endpoint'] = 'http://' + nodeIp + \
                                ':{}/uniledger/v1'.format(app_config['server_port'])
    # Set Statsd host
    new_conf_dict['statsd']['host'] = gMonitorServer

    # localdb restore app
    new_conf_dict['restore_server']['bind'] = '0.0.0.0:{}'.format(app_config['restore_server_port'])
    new_conf_dict['restore_server']['compress'] = True
    new_conf_dict['restore_endpoint'] = 'http://' + nodeIp + \
                                    ':{}/uniledger/v1/collect'.format(app_config['restore_server_port'])

    # multi apps configure
    new_conf_dict['app']['service_name'] = '{}'.format(app_config['service_name'])
    new_conf_dict['app']['setup_name'] = '{}'.format(app_config['setup_name'])



# 重新装配公钥环
print('Rewriting {}'.format(conf_files))
with open(conf_files, 'w') as f2:
    json.dump(new_conf_dict, f2)
