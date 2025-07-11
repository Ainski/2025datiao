from flask import Flask, request, jsonify
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch
import traceback

app = Flask(__name__)

# 设置模型路径
MODEL_PATH = "E:/github/2025datiao/back/deepseek-R1-qwen-1.5B/models--deepseek-ai--DeepSeek-R1-Distill-Qwen-1.5B"

# 初始化全局变量
model = None
tokenizer = None
generation_pipe = None


# 加载模型函数
def load_model():
	global model, tokenizer, generation_pipe
	
	if model is None:
		try:
			print("正在加载模型...")
			model = AutoModelForCausalLM.from_pretrained(
				MODEL_PATH,
				device_map="auto",
				torch_dtype=torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
			)
			tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
			
			# 创建文本生成管道（不指定设备）
			generation_pipe = pipeline(
				"text-generation",
				model=model,
				tokenizer=tokenizer
			)
			print("模型和管道加载成功")
		
		except Exception as e:
			print(f"模型加载失败: {e}")
			traceback.print_exc()
			model = None
			tokenizer = None
			generation_pipe = None


# 在应用启动时加载模型
load_model()


def ask_model(review: str) -> str:
	"""使用生成式模型判断评论是否为刷单文本"""
	global generation_pipe
	
	if not generation_pipe:
		load_model()  # 尝试重新加载
		if not generation_pipe:
			return "模型未成功加载，无法进行判断"
	
	try:
		print(f"开始处理评论: {review[:30]}...")
		
		# 优化后的提示模板
		prompt = (
				"### 任务：判断以下评论是否是刷单文本，并给出判断依据\n"
				"### 输出要求：\n"
				"1. 第一行必须明确回答：是刷单文本 或 不是刷单文本\n"
				"2. 第二行开始说明判断理由\n"
				"### 示例：\n"
				"是刷单文本\n"
				"理由：评论包含多个产品优点描述，使用重复赞美词汇，且提到物流速度等与产品无关的内容，符合刷单特征。\n"
				"### 待判断评论：\n" + review + "\n"
				                               "### 判断结果："
		)
		
		# 使用文本生成管道
		generated_results = generation_pipe(
			prompt,
			max_new_tokens=150,  # 限制生成的新token数量
			num_return_sequences=1,
			do_sample=False,  # 使用贪婪解码保证确定性输出
			eos_token_id=tokenizer.eos_token_id,
			pad_token_id=tokenizer.pad_token_id,
			truncation=True,  # 明确启用截断
			return_full_text=False  # 不返回原始提示
		)
		
		# 提取生成的文本
		generated_text = generated_results[0]['generated_text'].strip()
		print("模型生成结果：\n", generated_text)
		
		# 解析结果
		if "是刷单文本" in generated_text:
			return "是刷单文本 - " + generated_text
		elif "不是刷单文本" in generated_text:
			return "不是刷单文本 - " + generated_text
		else:
			return "不确定 - " + generated_text
	
	except Exception as e:
		print(f"处理评论时出错: {e}")
		traceback.print_exc()
		return f"处理评论时出错: {str(e)}"


@app.route('/api/input', methods=['POST'])
def analyze_comments():
	"""API接口，接收评论列表并返回判断结果"""
	try:
		# 检查模型是否已加载
		if not generation_pipe:
			load_model()  # 尝试重新加载
			if not generation_pipe:
				return jsonify({"error": "模型未成功加载，无法进行判断"}), 500
		
		# 获取请求数据
		data = request.get_json()
		if not data or 'comments' not in data:
			return jsonify({"error": "缺少必要的参数: comments"}), 400
		
		comments = data['comments']
		if not isinstance(comments, list) or len(comments) == 0:
			return jsonify({"error": "comments参数必须是一个非空列表"}), 400
		
		# 处理评论
		results = []
		for comment in comments:
			# 确保评论是字符串类型
			comment_text = str(comment) if not isinstance(comment, str) else comment
			eval_result = ask_model(comment_text)
			
			# 构建结果对象
			results.append({
				"comment": comment_text,
				"eval_result": eval_result
			})
		
		print(f"成功处理 {len(results)} 条评论")
		return jsonify(results), 200
	
	except Exception as e:
		print(f"API处理出错: {e}")
		traceback.print_exc()
		return jsonify({"error": f"服务器内部错误: {str(e)}"}), 500


@app.route('/health', methods=['GET'])
def health_check():
	"""健康检查端点"""
	if generation_pipe:
		return jsonify({"status": "healthy", "model_loaded": True}), 200
	else:
		return jsonify({"status": "unhealthy", "model_loaded": False}), 500


if __name__ == '__main__':
	# 测试模型功能
	# test_review = "味道很好闻 。保湿也挺好。也很好吸收，不黏腻。很好用。快递也很快。前一天下单，第二天就到了。还给送货到家。就京东这么好了吧。"
	# result = ask_model(test_review)
	# print("\n测试结果:")
	# print(result)
	
	# 启动Flask应用
	app.run(host="127.0.0.1", port=8989, debug=True)