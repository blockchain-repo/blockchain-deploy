import json
import os.path
from file_utils import find_file,chang_dir

def get_grafana_sql(query_name=None):

    if query_name == None:
        info = 'query name can not empty!'
        exit(info)

    conf_filename = 'grafana_sql.json'
    file_path = '../conf/grafana_temple'
    old_cwd = os.getcwd()

    query_condtion_path = find_file(conf_filename, file_path)

    with open(query_condtion_path) as j:
        dict = json.load(j)
        grafana_sql = dict[query_name]
        sqlStr = json.dumps(grafana_sql)
    chang_dir(old_cwd)
    return sqlStr

if __name__ == '__main__':
    get_grafana_sql()