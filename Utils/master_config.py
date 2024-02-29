import configparser
import sys 
import os
sys.path.append(os.getcwd())
from configs import EXP_CONFIGS


def write_config(filename, config_data):
    config = configparser.ConfigParser()

    for key, value in config_data.items():
        config['DEFAULT'][key] = str(value)

    with open(filename, 'w') as configfile:
        config.write(configfile)

def read_config(filename):
    config = configparser.ConfigParser()
    config.read(filename)

    config_data = {}
    for key, value in config['DEFAULT'].items():
        config_data[key] = value

    return config_data




if __name__ == "__main__":
    # 将 EXP_CONFIGS 写入配置文件
    write_config('config.ini', EXP_CONFIGS)

    # 从配置文件中读取配置
    loaded_config = read_config('config.ini')
    print(loaded_config)
