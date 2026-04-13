
import json
from .log import loginfo

def load_jsonl_to_dict_list(file_path: str) -> list:
	"""
	读取 JSONL 文件，转换为 字典列表（list[dict]）
	:param file_path: JSONL 文件路径（输入位置）
	:return: 字典列表，读取失败返回空列表
	"""
	data_list = []
	
	try:
		loginfo(f"开始加载 JSONL 文件：{file_path}", "start")
		
		# 逐行读取（支持超大文件，不占内存）
		with open(file_path, "r", encoding="utf-8") as f:
			for line_num, line in enumerate(f, 1):
				line = line.strip()
				if not line:
					continue  # 跳过空行
				
				try:
					item = json.loads(line)
					data_list.append(item)
				except json.JSONDecodeError:
					loginfo(f"第 {line_num} 行格式错误，已跳过", "error")
		
		loginfo(f"加载完成！共读取 {len(data_list)} 条数据", "success")
		return data_list
	
	except FileNotFoundError:
		loginfo(f"文件不存在：{file_path}", "error")
		return data_list
	except Exception as e:
		loginfo(f"加载失败：{str(e)}", "error")
		return data_list