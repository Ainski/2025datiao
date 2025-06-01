import os
import pathlib
import re


def process_file(input_path, output_dir="clear_data"):
	"""读取文件，删除每行中反斜杠及其后的内容，并替换独立的none为\"none\""""
	# 创建输出目录（如果不存在）
	pathlib.Path(output_dir).mkdir(parents=True, exist_ok=True)

	# 构建输出文件路径
	filename = os.path.basename(input_path)
	output_path = os.path.join(output_dir, filename)

	with open(input_path, 'r', encoding='utf-8') as f_in:
		lines = f_in.readlines()

	processed_lines = []
	for line in lines:
		# 查找反斜杠的位置并删除其后的内容
		backslash_pos = line.find('//')
		if backslash_pos != -1:
			processed_line = line[:backslash_pos] + '\n'
		else:
			processed_line = line

		# 使用正则表达式替换独立的none（前后非引号字符）
		processed_line = re.sub(r'(?<![\"\'])(none)(?![\"\'])', r'"\1"', processed_line)

		processed_lines.append(processed_line)

	with open(output_path, 'w', encoding='utf-8') as f_out:
		f_out.writelines(processed_lines)

	print(f"处理完成，输出文件: {output_path}")
	return output_path


if __name__ == '__main__':
	count = 5
	input_path = r"datas/demo%d.json"
	output_dir = "clear_data"

	for i in range(count):
		the_input_path = input_path % (i + 1)

		# 检查文件是否存在
		if os.path.exists(the_input_path):
			print(f"正在处理文件: {the_input_path}")
			process_file(the_input_path, output_dir)
		else:
			print(f"文件不存在: {the_input_path}")