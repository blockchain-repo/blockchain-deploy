
# for multi apps, you should specify the app service name, setup_name and database.name
# and modify the port in server.bind, api_endpoint, restore_server.bind, restore_endpoint
# and make them unique and free

_app_config = {
    'server_port': 9984,
    'restore_server_port': 9986,
    'service_name': 'unichain',
    'setup_name': 'UnichainDB',
    'db_name':'bigchain'
}
