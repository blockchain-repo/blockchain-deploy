# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import os


unichain_confiles = os.getcwd()

keypairs_path = os.chdir('../script')
# 获取原有节点公钥环,重新装配节点公钥环
conf_files = "unichain_conf"
with open(conf_files, 'r') as f:
    conf_dict = json.load(f)
    old_pubkeys = conf_dict['keyring']
    pubkey = conf_dict['keypair']['public']

os.chdir('../conf')
keyrings_path = os.getcwd()
# 获取最新的公钥环
keyrings_path = keyrings_path+"/keyring"
with open(keyrings_path, 'r') as f:
    keyrings_bak_dict = json.load(f)
    keyrings_bak = keyrings_bak_dict['keyring']

# 删除节点公钥
print('Rewriting {}'.format(conf_files))
with open(keyrings_path, 'w') as f2:
    keyring = list(keyrings_bak)
    keyring.remove(pubkey)
    keyrings_bak_dict['keyring'] = keyring
    json.dump(keyrings_bak_dict, f2)
