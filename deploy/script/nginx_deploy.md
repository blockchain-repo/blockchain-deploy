## nginx deploy tips

### 1. uninstall old nginx
```
bash nginx_uninstall.sh
```

### 2. install nginx
```
bash nginx_install.sh
```
it contains:

```
fab -f fabfile_nginx.py uninstall_nginx

fab -f fabfile_nginx.py clear_nginx_nodes

fab -f fabfile_nginx.py generate_nginx_node_info

fab -f fabfile_nginx.py download_nginx

fab -f fabfile_nginx.py create_nginx_user_group

fab -f fabfile_nginx.py send_nginx

fab -f fabfile_nginx.py install_nginx_dependency

./nginx_compile_install.sh

./nginx_config_conf.sh

fab -f fabfile_nginx.py config_nginx_service
```

### 4. generate the nginx upstream and servers template

```
bash nginx_servers_generate.sh <upstream_name> <server_port> <delete>"

```

`upstream_name` is also the generate filename!

If you have finished the file modify in `../sources/sys_config/nginx/servers/`,
you can go the next step!

### 5. send the OK servers config
```
bash nginx_servers_send.sh <upstream_name>
```

### 6. nginx cut log
`nginx_log_cut_days.sh` in `../sources/sys_config/nginx/base_conf/`

```
# bash nginx_log_cut.sh <m> <h> <dom> <mon> <dow> <user>

bash nginx_log_cut.sh 0 0

```