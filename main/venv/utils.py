import csv
import json
import os
import regex as re


def read_input_data(file_path):
	"""
    从TSV文件读取输入数据，提取至少包含8个字段的行

    参数:
        file_path (str): TSV文件路径

    返回:
        list: 包含有效行数据的列表，每行是一个字符串列表

    异常处理:
        - 文件不存在时抛出FileNotFoundError
        - 文件读取错误时抛出IOError
    """
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
	"""
    将数据保存为JSON文件，自动创建目录

    参数:
        output_path (str): JSON输出文件路径
        data (dict|list): 要保存的JSON数据

    异常处理:
        - 目录创建失败时抛出OSError
        - 文件写入失败时抛出IOError
    """
	try:
		os.makedirs(os.path.dirname(output_path), exist_ok=True)
		with open(output_path, 'w', encoding='utf-8') as f:
			json.dump(data, f, ensure_ascii=False, indent=2)
	except Exception as e:
		print(f"保存JSON文件失败: {str(e)}")
		raise


def read_json_file(file_path: str, encoding: str = 'utf-8') -> dict | list:
	"""
    读取JSON文件并返回解析后的内容（字典或列表）

    参数:
        file_path (str): JSON文件的完整路径（例如: "data/product.json"）
        encoding (str): 文件编码（默认: utf-8，可指定如 'gbk' 等）

    返回:
        dict | list: 解析后的JSON数据（字典或列表）

    异常处理:
        - 文件不存在时抛出FileNotFoundError
        - JSON格式错误时抛出json.JSONDecodeError
        - 其他IO错误时抛出异常
    """
	try:
		# 检查文件是否存在
		if not os.path.exists(file_path):
			raise FileNotFoundError(f"文件不存在: {file_path}")

		# 读取文件内容
		with open(file_path, 'r', encoding=encoding) as f:
			data = json.load(f)  # 解析JSON数据

		return data  # 返回解析后的字典或列表

	except FileNotFoundError as e:
		print(f"错误: {e}")
		raise  # 重新抛出异常（可选，可根据需求决定是否捕获）
	except json.JSONDecodeError as e:
		print(f"JSON格式错误: {e}，请检查文件内容是否符合JSON规范")
		raise
	except Exception as e:
		print(f"读取文件时发生未知错误: {e}")
		raise


def recursive_print_json(data, indent=0):
	"""
    递归遍历JSON数据并格式化输出，每层数据换行显示

    参数:
        data (dict/list): JSON数据（字典或列表）
        indent (int): 缩进层级（用于控制空格数，默认0）

    输出示例:
        {
          "key": "value",
          "list": [
            "item1",
            "item2"
          ]
        }
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


def extract_and_parse_json(text: str) -> dict | list:
	"""
    从文本中提取JSON字符串并解析

    参数:
        text (str): 包含JSON内容的文本段落

    返回:
        dict/list: 解析后的JSON数据

    异常处理:
        - 未找到有效JSON结构时抛出ValueError
        - JSON解析失败时抛出ValueError

    匹配模式:
        - 支持嵌套的对象结构（大括号{}）
        - 支持嵌套的数组结构（中括号[]）
        - 支持多行JSON文本
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
def dict_to_string(data: dict) -> str:
	"""
    将字典转换为字符串，以便于输出

    参数:
        data (dict): 字典数据

    返回:
        str: 字典数据转换后的字符串

    异常处理:
        - 无
	"""
	return json.dumps(data, ensure_ascii=False, indent=2)