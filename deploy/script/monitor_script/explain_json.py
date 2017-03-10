# -*- coding: utf-8 -*-\n
import json
import os.path
from query_condtion import get_all_condtions,get_all_business
from file_utils import find_file,chang_dir

def read_jsonFile():

    all_conditions = get_all_business()
    condtions_length = len(all_conditions)

    conf_filename = 'hardware.json'
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



def write_jsonFile():
    newDic = read_jsonFile()
    conf_filename = 'hardware.json'
    file_path = '../../../grafana-unichain-docker/grafana_json'
    old_cwd = os.getcwd()
    json_files_path = find_file(conf_filename,file_path)
    # write grafana query condition into json file
    with open(json_files_path, 'w') as w:
        json.dump(newDic, w)
    chang_dir(old_cwd)

if __name__ == '__main__':
    write_jsonFile()














