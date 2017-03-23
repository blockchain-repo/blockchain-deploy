#! /bin/bash

# The set -e option instructs bash to immediately exit
# if any command has a non-zero exit status
set -e

# steps:
# 1 uninstall old nginx install
echo -e "[INFO]========== 1 uninstall old nginx install =========="
fab -f fabfile_nginx.py uninstall_nginx

# 2.1 clear_nginx_nodes
echo -e "[INFO]========== 2.1 clear_nginx_nodes =========="
fab -f fabfile_nginx.py clear_nginx_nodes

# 2.2 generate_nginx_node_info
echo -e "[INFO]========== 2.2 generate_nginx_node_info =========="
fab -f fabfile_nginx.py generate_nginx_node_info

# 2.2 download_nginx
echo -e "[INFO]========== 2.2 download_nginx =========="
fab -f fabfile_nginx.py download_nginx

# 2.3 create_nginx_user_group
echo -e "[INFO]========== 2.3 create_nginx_user_group =========="
fab -f fabfile_nginx.py create_nginx_user_group

# 3.1 send nginx tar.gz
echo -e "[INFO]========== 3.1 send nginx tar.gz=========="
fab -f fabfile_nginx.py send_nginx:delete=True

# 3.2 install_nginx_dependency
echo -e "[INFO]========== 3.2 install_nginx_dependency=========="
fab -f fabfile_nginx.py install_nginx_dependency

# 4 nginx_compile_install
echo -e "[INFO]========== 4 nginx_compile_install=========="
./nginx_compile_install.sh

# 5 config the nginx base config [nginx.conf]
echo -e "[INFO]========== 5 config the nginx base config [nginx.conf] =========="
./nginx_config_conf.sh

# 6 config_nginx_service
echo -e "[INFO]========== 6 config_nginx_service=========="
fab -f fabfile_nginx.py config_nginx_service