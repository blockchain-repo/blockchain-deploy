#! /bin/bash

# The set -e option instructs bash to immediately exit
# if any command has a non-zero exit status
set -e

# 0. init control
echo -e "[INFO]========== init control =========="
./run_init_env.sh

# 1. update_node apt, third apt
echo -e "[INFO]========== 1. update_node apt, third apt =========="
fab -f fabfile_origin.py node_apt_update

# 2. install_base_software
echo -e "[INFO]========== 2. install_base_software =========="
fab -f fabfile_origin.py install_base_software

# 3. sync_zone_datetime
echo -e "[INFO]========== 3. sync_zone_datetime =========="
fab -f fabfile_origin.py sync_zone_datetime
