# -*- coding: utf-8 -*-\n
import json
import os.path
from achieve_hostname import node_hostname
from file_utils import find_file,chang_dir
from grafana_sql import get_grafana_sql

def get_cpu_condtion():
    cpu_sql = get_grafana_sql('cpu')
    cpu_condtion = add_nodes_query(cpu_sql)
    return cpu_condtion

def get_dfvalue_condtion():
    dfvalue_sql = get_grafana_sql('dfvalue')
    dfvalue_condtion = add_nodes_query(dfvalue_sql)
    return dfvalue_condtion

def get_diskRead_condtion():
    diskRead_sql = get_grafana_sql('disk_read')
    diskRead_condtion = add_nodes_query(diskRead_sql)
    return diskRead_condtion

def get_diskWrite_condtion():
    diskWrite_sql = get_grafana_sql('disk_write')
    diskWrite_condtion = add_nodes_query(diskWrite_sql)
    return diskWrite_condtion

def get_interfaceRe_condtion():
    interfaceRe_sql = get_grafana_sql('interface_rx')
    interfaceRe_condtion = add_nodes_query(interfaceRe_sql)
    return interfaceRe_condtion

def get_interfaceTx_condtion():
    interfaceTx_sql = get_grafana_sql('interface_tx')
    interfaceTx_condtion = add_nodes_query(interfaceTx_sql)
    return interfaceTx_condtion

def get_load_condtion():
    load_sql = get_grafana_sql('load')
    load_condtion = add_nodes_query(load_sql)
    return load_condtion

def get_memory_condtion():
    memory_sql = get_grafana_sql('memory')
    memory_condtion = add_nodes_query(memory_sql)
    return memory_condtion

def get_fileHandles_condtion():
    fileHandles_sql = get_grafana_sql('file_handle')
    fileHandles_condtion = add_nodes_query(fileHandles_sql)
    return fileHandles_condtion

def get_uni_pro_condtion():
    unichain_processes_sql = get_grafana_sql('unichain_processes')
    uni_pro_condtion = add_nodes_query(unichain_processes_sql)
    return uni_pro_condtion

def get_uniApi_pro_condtion():
    uniApi_pro_sql = get_grafana_sql('unichain_api_processes')
    uniApi_pro_condtion = add_nodes_query(uniApi_pro_sql)
    return uniApi_pro_condtion

def get_queue_gauge_condtion():
    queue_gauge_sql = get_grafana_sql('statsd_bc1__tx_queue_gauge')
    queue_gauge_condtion = add_nodes_query(queue_gauge_sql)
    return queue_gauge_condtion

def get_write_block_count_condtion():
    write_block_count_sql = get_grafana_sql('statsd_bc1__write_block_count')
    write_block_count_condtion = add_nodes_query(write_block_count_sql)
    return write_block_count_condtion

def get_write_transaction_count_condtion():
    write_transaction_count_sql = get_grafana_sql('statsd_bc1__write_transaction_count')
    write_transaction_count_condtion = add_nodes_query(write_transaction_count_sql)
    return write_transaction_count_condtion

def get_write_transaction_condtion():
    write_transaction_sql = get_grafana_sql('statsd_bc1__write_transaction_mean')
    write_transaction_condtion = add_nodes_query(write_transaction_sql)
    return write_transaction_condtion

def get_validate_transaction_condtion():
    validate_transaction_sql = get_grafana_sql('statsd_bc1__validate_transaction_mean')
    validate_transaction_condtion = add_nodes_query(validate_transaction_sql)
    return validate_transaction_condtion

def get_validate_block_condtion():
    validate_block_sql = get_grafana_sql('statsd_bc1__validate_block_mean')
    validate_block_condtion = add_nodes_query(validate_block_sql)
    return validate_block_condtion

def get_write_block_condtion():
    write_block_sql = get_grafana_sql('statsd_bc1__write_block_mean')
    write_block_condtion = add_nodes_query(write_block_sql)
    return write_block_condtion

def get_all_condtions():
    all_conditions = []
    all_conditions.append(get_cpu_condtion())
    all_conditions.append(get_memory_condtion())
    all_conditions.append(get_dfvalue_condtion())
    all_conditions.append(get_diskWrite_condtion())
    all_conditions.append(get_diskRead_condtion())
    all_conditions.append(get_interfaceRe_condtion())
    all_conditions.append(get_interfaceTx_condtion())
    all_conditions.append(get_load_condtion())
    all_conditions.append(get_fileHandles_condtion())
    all_conditions.append(get_uni_pro_condtion())
    all_conditions.append(get_uniApi_pro_condtion())
    all_conditions.append(get_queue_gauge_condtion())
    all_conditions.append(get_write_block_count_condtion())
    all_conditions.append(get_write_transaction_count_condtion())
    all_conditions.append(get_write_transaction_condtion())
    all_conditions.append(get_validate_transaction_condtion())
    all_conditions.append(get_validate_block_condtion())
    all_conditions.append(get_write_block_condtion())
    return all_conditions

def get_business():

    business = []

    business.append(get_write_block_count_condtion())
    business.append(get_uni_pro_condtion())
    business.append(get_uniApi_pro_condtion())
    business.append(get_queue_gauge_condtion())
    business.append(get_write_transaction_condtion())
    business.append(get_validate_transaction_condtion())
    business.append(get_validate_block_condtion())
    business.append(get_write_block_condtion())

    return business

def get_hardware2():
    hardware2 = []

    hardware2.append(get_diskRead_condtion())
    hardware2.append(get_diskWrite_condtion())
    hardware2.append(get_fileHandles_condtion())
    hardware2.append(get_dfvalue_condtion())
    hardware2.append(get_interfaceRe_condtion())
    hardware2.append(get_interfaceTx_condtion())
    hardware2.append(get_load_condtion())

    return hardware2



def add_nodes_query(grafana_sql=None):

    if grafana_sql == None:
        info = 'grafana_sql can not empty!'
        exit(info)

    conf_filename = 'query_temple.json'
    file_path = './grafana_temple'
    old_cwd = os.getcwd()
    query_condtion_path = find_file(conf_filename, file_path)

    # add query condtions
    final_queryStr = ''
    with open(query_condtion_path) as j:
        dict = json.load(j)
        queryStr = json.dumps(dict)
        node_length = len(node_hostname)
        # add query condtions and modify hostname
        for index in range(node_length):
            hostname = node_hostname[index]
            #除去收尾""
            grafana_sql_str = grafana_sql.strip('"')
            new_queryStrId = queryStr.replace('A', chr(index + 65))
            new_queryConStr = new_queryStrId.replace('query_condtion',grafana_sql_str)
            new_queryStr = new_queryConStr.replace('bc1', hostname)
            if (index == 0):
                final_queryStr = '[' + new_queryStr + ','
            elif (index == node_length - 1):
                final_queryStr = final_queryStr + new_queryStr + ']'
            else:
                final_queryStr = final_queryStr + new_queryStr + ','
    chang_dir(old_cwd)
    return final_queryStr

if __name__ == '__main__':
    print('get_cpu_condtion()',get_cpu_condtion())
    print('get_dfvalue_condtion()', get_dfvalue_condtion())
    print('get_diskRead_condtion()', get_diskRead_condtion())
    print('get_diskWrite_condtion()', get_diskWrite_condtion())
    print('get_fileHandles_condtion()', get_fileHandles_condtion())
    print('get_interfaceRe_condtion()', get_interfaceRe_condtion())
    print('get_interfaceTx_condtion()', get_interfaceTx_condtion())
    print('get_load_condtion()', get_load_condtion())
    print('get_memory_condtion()', get_memory_condtion())
    print('get_all_condtions()', get_all_condtions())




















