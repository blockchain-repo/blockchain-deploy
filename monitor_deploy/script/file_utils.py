# -*- coding: utf-8 -*-\n
import json
import os.path

# find files
import types


def find_file(conf_filename=None,file_path=None):
    '''

    :param conf_filename: file name
    :param file_path: file path
    :return: file_path/file_name
    '''
    # cwd = current working directory
    old_cwd = os.getcwd()
    # change working directory
    os.chdir(file_path)
    conf_path = os.getcwd()

    file_full_path= conf_path + "/" + conf_filename
    # To determine whether the file
    existJsonFile = os.path.isfile(file_full_path)
    # To determin whether the file exists
    if not existJsonFile:
        info = 'You lose the file {} in "{}"'.format(conf_filename, conf_path)
        os.chdir(old_cwd)
        exit(info)
    return file_full_path

def chang_dir(old_cwd):
    os.chdir(old_cwd)

def modify_grafana_json(dict,oldTarget,newTarget):
    tmp = dict
    for k,v in tmp.items():
        if k == 'rows':
            a = v[0]
            for o,p in a.items():
                if o == 'panels':
                    b = p[0]
                    print(b)
                    for i,j in b.items():
                        if i == 'targets':
                            if b['targets'] == oldTarget:
                                b['targets'] = newTarget
                                return dict
                        else:
                            return