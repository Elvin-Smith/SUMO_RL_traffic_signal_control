import configparser
import sys 
import os
sys.path.append(os.getcwd())
from configs import EXP_CONFIGS
import json

def write_list_to_json(file_path, data_list):
    with open(file_path, 'w') as json_file:
        json.dump(data_list, json_file)

def read_list_from_json(file_path):
    with open(file_path, 'r') as json_file:
        data_list = json.load(json_file)
    return data_list







if __name__ == "__main__":
    # 示例用法
    my_list = [1, 2, 3, 'abc', {'key': 'value'}]

    # 写入列表到JSON文件
    write_list_to_json('my_list.json', my_list)

    # 从JSON文件中读取列表
    loaded_list = read_list_from_json('my_list.json')

    print(loaded_list)
