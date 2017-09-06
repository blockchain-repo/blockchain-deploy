# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import os


unichain_confiles = os.getcwd()

keypairs_path = os.chdir('../script')
if os.path.isfile('keypairs.py'):
    from keypairs import keypairs_list

os.chdir('../conf')
keyring_path = os.getcwd()

num_keypairs = len(keypairs_list)
pubkeys = [keypair[1] for keypair in keypairs_list[:num_keypairs]]

keyrings_path = keyring_path+"/keyring"


with open(keyrings_path, 'r') as f:
    keyrings_bak_dict = json.load(f)
    keyrings_bak = keyrings_bak_dict['keyring']

# 备份所有节点公钥
with open(keyrings_path, 'w') as f2:
    keyring_new = list(pubkeys)
    for pubkey in keyring_new:
        if pubkey not in keyrings_bak:
            keyrings_bak.append(pubkey)
    json.dump(keyrings_bak_dict, f2)

