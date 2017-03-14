# -*- coding: utf-8 -*-\n
import json
import os.path

import sys
from query_condtion import get_hardware,get_business
from file_utils import find_file,chang_dir

def read_jsonFile(fileNum):

    if fileNum == 1:
        all_conditions = get_business()
    elif fileNum == 2:
        all_conditions = get_hardware()
#    elif fileNum == 3:
#
    condtions_length = len(all_conditions)

    conf_filename = choose_jsonFile(fileNum)
    file_path = '../conf/grafana_temple'
    old_cwd = os.getcwd()
    json_files_path = find_file(conf_filename,file_path)
    # add nodes grafana query condition
    with open(json_files_path) as j:
        dict = json.load(j)
        jsonStr = json.dumps(dict)
        for index in range(condtions_length):
            query_condtion = all_conditions[index]
            j = index + 1000
            jsonStr = jsonStr.replace(str(j),query_condtion)
        newDic = json.loads(jsonStr)
    chang_dir(old_cwd)
    return newDic

def write_jsonFile(fileNum):
    newDic = read_jsonFile(fileNum)
    conf_filename = choose_jsonFile(fileNum)
    file_path = '../conf/grafana_json'
    old_cwd = os.getcwd()
    json_files_path = find_file(conf_filename,file_path)
    # write grafana query condition into json file
    with open(json_files_path, 'w') as w:
        json.dump(newDic, w)
    chang_dir(old_cwd)

def choose_jsonFile(fileNum):
    if fileNum == 1:
        return 'unichain_hardware.json'
    elif fileNum == 2:
        return 'unichain_business.json'
#    elif fileNum == 3:
#        return 'uni-ledger-hardware1.json'

if __name__ == '__main__':

    write_jsonFile(1)
    write_jsonFile(2)















