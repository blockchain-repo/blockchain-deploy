#! /bin/bash

# The set -e option instructs bash to immediately exit
# if any command has a non-zero exit status
set -e

# config the nginx base config [nginx.conf]
fab -f fabfile_nginx.py config_nginx_conf