# -*- coding: utf-8 -*-\n

import os.path

# import reg_utils # usage reg_utils.reg_nodes,...
from file_utils import find_file,chang_dir
from reg_utils import reg_nodes,reg_ip

node_hostname = []
node_hosts = []

conf_filename = 'blockchain_nodes'
file_path = '../conf'
old_cwd = os.getcwd()
blockchain_nodes_path = find_file(conf_filename,file_path)

with open(blockchain_nodes_path) as f:
    for line in f.readlines():
        line = line.strip()
        if  not len(line) or line.startswith('#'):
            continue

        groups = reg_nodes(line)
        if groups:
            length = len(groups)
            if length < 4:
                exit('error format...')
            username = groups[0]
            node_hostname.append(username)
            host = groups[1]
            node_hosts.append(host)
chang_dir(old_cwd)
