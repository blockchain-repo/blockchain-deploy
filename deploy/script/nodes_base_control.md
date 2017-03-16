# node base info control

Include node password, host change and add or delete new user.

## 1.1 generates_origin_node_info

```
fab -f fabfile_origin.py generates_origin_node_info
```

## 1.2 update_origin_node_password
```
fab -f fabfile_origin.py update_origin_node_password
```

## 1.3 update_node_hostname
```
fab -f fabfile_origin.py update_node_hostname
```

## 2.1 clear_blockchain_nodes [error here, need fix!!!!]
```
#fab -f fabfile_origin.py clear_blockchain_nodes
```

## 2.2 generates_new_user_node_info
```
fab -f fabfile_origin.py generates_new_user_node_info
```

## 2.3 create_new_user

fab update_node_apt update_node_third_apt update_node_pip update
```
fab -f fabfile_origin.py create_new_user
```

## 3. update_node apt, third apt
```
fab -f fabfile_origin.py node_apt_update
```

## 4. install_base_software
```
fab -f fabfile_origin.py install_base_software
```

## 5. sync_zone_datetime
```
fab -f fabfile_origin.py sync_zone_datetime
```