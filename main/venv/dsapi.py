import os
import argparse
import json
from utils import read_input_data, save_json_output
from config import DEEPSEEK_API_KEY
from openai import OpenAI

API_URL = 'https://api.deepseek.com/'

def call_deepseek_api(prompt):
	# ret ='''{\n    "comment": [\n        {\n            "content": "不愧是ally推荐的，很好用，会继续回购",\n            "risk_level": "中风险",\n            "reason": "评论内容较为通用，缺乏具体产品细节（如保湿或定妆效果），仅泛泛提及\'好用\'和\'回购\'，且强调影响者推荐（ally），可能为刷单常见的模板式评论；但评论与产品相关，并非完全无意义或无关，因此风险等级中等。"\n        }\n    ]\n}'''
	# return ret
	"""
	:param prompt: 用户的输入提示
	:return: 如果调用成功，返回API响应和reasoning内容；否则，返回错误信息。
	"""
	client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
	print(f"DeepSeek API调用中，请稍候...")

	try:
		response = client.chat.completions.create(
			model="deepseek-chat",
			messages=[
				{"role": "user", "content": prompt}
			],
			temperature=0.3,
			max_tokens=2000
		)
		# 获取完整API响应
		api_response = response.choices[0].message.content
		#reasoning_content = response.choices[0].message.reasoning_content  # 获取reasoning内容
		return api_response

	except Exception as e:
		print(f"API调用失败: {str(e)}")
		return {
			"raw_response": "",
			"description": "",
			"type": "API调用失败",
			"think": f"API调用失败: {str(e)}",
			"reasoning": ""
		}

