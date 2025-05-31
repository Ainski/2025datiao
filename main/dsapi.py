import os
import argparse
import json
from utils import read_input_data, save_json_output
from config import DEEPSEEK_API_KEY
from openai import OpenAI

API_URL = 'https://api.deepseek.com/'

def call_deepseek_api(prompt):
	"""
	:param prompt: 用户的输入提示
	:return: 如果调用成功，返回API响应和reasoning内容；否则，返回错误信息。
	"""
	client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
	print(f"DeepSeek API调用中，请稍候...")

	try:
		response = client.chat.completions.create(
			model="deepseek-reasoner",
			messages=[
				{"role": "user", "content": prompt}
			],
			temperature=0.3,
			max_tokens=2000
		)
		# 获取完整API响应
		api_response = response.choices[0].message.content
		reasoning_content = response.choices[0].message.reasoning_content  # 获取reasoning内容
		return {api_response,reasoning_content}

	except Exception as e:
		print(f"API调用失败: {str(e)}")
		return {
			"raw_response": "",
			"description": "",
			"type": "API调用失败",
			"think": f"API调用失败: {str(e)}",
			"reasoning": ""
		}

