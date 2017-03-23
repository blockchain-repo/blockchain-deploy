#! /bin/bash

# The set -e option instructs bash to immediately exit
# if any command has a non-zero exit status
set -e

# compile and install
# echo -e "[INFO]========== compile_nginx =========="
fab -f fabfile_nginx.py compile_nginx

# echo -e "[INFO]========== make_install_nginx =========="
fab -f fabfile_nginx.py make_install_nginx