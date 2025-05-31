import csv
import json
import os
import regex as re

def read_input_data(file_path):
    data = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                if len(row) >= 8:  # 确保有8个字段
                    data.append(row)
    except Exception as e:
        print(f"读取输入文件失败: {str(e)}")
        raise
    return data

def save_json_output(output_path, data):
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存JSON文件失败: {str(e)}")
        raise


def read_json_file(file_path: str, encoding: str = 'utf-8') -> dict | list:
    """
    读取 JSON 文件并返回解析后的内容（字典或列表）

    参数:
        file_path (str): JSON 文件的完整路径（例如: "data/product.json"）
        encoding (str): 文件编码（默认: utf-8，可指定如 'gbk' 等）

    返回:
        dict | list: 解析后的 JSON 数据（字典或列表）

    异常处理:
        - 文件不存在时抛出 FileNotFoundError
        - JSON 格式错误时抛出 json.JSONDecodeError
        - 其他 IO 错误时抛出异常
    """
    try:
        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")

        # 读取文件内容
        with open(file_path, 'r', encoding=encoding) as f:
            data = json.load(f)  # 解析 JSON 数据

        return data  # 返回解析后的字典或列表

    except FileNotFoundError as e:
        print(f"错误: {e}")
        raise  # 重新抛出异常（可选，可根据需求决定是否捕获）
    except json.JSONDecodeError as e:
        print(f"JSON 格式错误: {e}，请检查文件内容是否符合 JSON 规范")
        raise
    except Exception as e:
        print(f"读取文件时发生未知错误: {e}")
        raise


def recursive_print_json(data, indent=0):
    """
    递归遍历 JSON 数据并格式化输出，每层数据换行显示

    参数:
        data (dict/list): JSON 数据（字典或列表）
        indent (int): 缩进层级（用于控制空格数，默认 0）
    """
    # 处理字典类型（对象）
    if isinstance(data, dict):
        print('{')
        for key, value in data.items():
            print(' ' * (indent + 2) + f'"{key}": ', end='')
            recursive_print_json(value, indent + 2)  # 递归处理值
            print(',')  # 键值对后添加逗号（除最后一个）
        print(' ' * indent + '}')  # 闭合字典

    # 处理列表类型（数组）
    elif isinstance(data, list):
        print('[')
        for item in data:
            print(' ' * (indent + 2), end='')
            recursive_print_json(item, indent + 2)  # 递归处理元素
            print(',')  # 元素后添加逗号（除最后一个）
        print(' ' * indent + ']')  # 闭合列表

    # 处理基础类型（字符串、数字、布尔值、null）
    else:
        # 字符串需添加双引号，其他类型直接转换为字符串
        if isinstance(data, str):
            print(f'"{data}"', end='')
        else:
            print(str(data), end='')

def extract_and_parse_json(text):
    """
    从文本中提取JSON字符串并解析

    参数:
        text (str): 包含JSON内容的文本段落

    返回:
        dict/list: 解析后的JSON数据
    """
    # 正则表达式匹配JSON内容（支持大括号和中括号包裹的结构）
    pattern = r'(?s)(\{(?:[^{}]|(?R))*\})|(\[(?:[^\[\]]|(?R))*\])'

    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)

    if not match:
        raise ValueError("未在文本中找到有效的JSON结构")
    # 提取匹配到的JSON字符串
    json_str = match.group()

    try:
        # 解析JSON字符串
        data = json.loads(json_str)
        print("成功提取并解析JSON数据：")
        return data
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON解析失败：{e}")