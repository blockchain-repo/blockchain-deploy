# -*- coding: utf-8 -*-\n
import json
import os.path

import sys
from query_condtion import get_all_condtions,get_all_business
from file_utils import find_file,chang_dir

def read_jsonFile(fileNum):

    all_conditions = get_all_business()
    condtions_length = len(all_conditions)

    conf_filename = choose_jsonFile(fileNum)
    file_path = './grafana_temple'
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
    file_path = '../../../grafana-unichain-docker/grafana_json'
    old_cwd = os.getcwd()
    json_files_path = find_file(conf_filename,file_path)
    # write grafana query condition into json file
    with open(json_files_path, 'w') as w:
        json.dump(newDic, w)
    chang_dir(old_cwd)

def choose_jsonFile(fileNum):
    if fileNum == 1:
        return 'uni-ledger-business.json'
    elif fileNum == 2:
        return 'uni-ledger-hardware2.json'
#    elif fileNum == 3:
#        return 'uni-ledger-hardware1.json'

if __name__ == '__main__':

    write_jsonFile(1)
    write_jsonFile(2)















