import os


def extract_filename(file_path):
    # 使用os.path.basename获取文件名（包含扩展名）
    base_name = os.path.basename(file_path)
    
    # 使用os.path.splitext获取文件名和扩展名的元组
    filename, _ = os.path.splitext(base_name)
    
    return filename


def find_json_file(file_path):
    # 获取输入文件的目录和文件名
    directory, filename = os.path.split(file_path)

    # 获取目录下所有文件
    all_files = os.listdir(directory)

    # 寻找同名但扩展名为.ini的文件
    for file in all_files:
        if os.path.isfile(os.path.join(directory, file)) and file.lower().endswith('.json'):
            # 构建同名但扩展名为.ini的文件的绝对路径
            ini_file_path = os.path.join(directory, file)
            return ini_file_path

    # 如果找不到对应的.ini文件，则返回None
    return None

if __name__ == "__main__":
    file_path = r'E:\code\mycode\network\5x5grid.sumocfg'
    result = find_json_file(file_path)
    print(result)