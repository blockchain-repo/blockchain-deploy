#! /bin/bash

# The set -e option instructs bash to immediately exit
# if any command has a non-zero exit status
set -e

# steps:
# uninstall old nginx install
fab -f fabfile_nginx.py uninstall_nginx

