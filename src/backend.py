from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline, BitsAndBytesConfig
import torch
import traceback
from train.config import configure
app = Flask(__name__)

# 启用 CORS，允许所有来源访问（开发环境）
CORS(app, resources={r"/*": {"origins": "*"}})

# 设置模型路径
MODEL_PATH = configure["final_save_path"]
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
			
			# 检查 GPU 是否可用
			if torch.cuda.is_available():
				gpu_name = torch.cuda.get_device_name(0)
				gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
				print(f"检测到 GPU: {gpu_name}, 显存: {gpu_memory:.2f} GB")
				
				# 使用 4bit 量化减少显存占用
				quantization_config = BitsAndBytesConfig(
					load_in_4bit=True,
					bnb_4bit_compute_dtype=torch.float16,
					bnb_4bit_use_double_quant=True,
					bnb_4bit_quant_type="nf4"
				)
				
				print("使用 4bit 量化加载模型...")
				device_map = "cuda"
				
			else:
				print("未检测到 GPU，使用 CPU 加载模型（可能需要较长时间）")
				device_map = "cpu"
				quantization_config = None

			model = AutoModelForCausalLM.from_pretrained(
				MODEL_PATH,
				device_map=device_map,
				quantization_config=quantization_config,
				torch_dtype=torch.float16,
				low_cpu_mem_usage=True
			)
			
			tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
			
			# 如果模型没有 pad_token，设置一个
			if tokenizer.pad_token is None:
				tokenizer.pad_token = tokenizer.eos_token
				model.config.pad_token_id = model.config.eos_token_id

			# 创建文本生成管道（指定设备）
			device = 0 if torch.cuda.is_available() else -1
			generation_pipe = pipeline(
				"text-generation",
				model=model,
				tokenizer=tokenizer,
				device=device,
				torch_dtype=torch.float16
			)
			
			# 打印显存使用情况
			if torch.cuda.is_available():
				used_memory = torch.cuda.memory_allocated(0) / 1024**3
				print(f"GPU 显存已使用: {used_memory:.2f} GB")
			
			print("模型和管道加载成功")

		except RuntimeError as e:
			if "CUDA out of memory" in str(e):
				print(f"GPU 显存不足: {e}")
				print("尝试使用 CPU 加载...")
				# 清除 GPU 缓存
				torch.cuda.empty_cache()
				# 重置变量
				model = None
				tokenizer = None
				generation_pipe = None
				# 使用 CPU 加载
				return load_model_cpu()
			else:
				print(f"模型加载失败: {e}")
				traceback.print_exc()
		except ImportError as e:
			print(f"缺少 bitsandbytes 库，尝试普通加载...")
			print(f"安装命令: pip install bitsandbytes")
			traceback.print_exc()
			# 回退到普通加载
			return load_model_fallback()
		except Exception as e:
			print(f"模型加载失败: {e}")
			traceback.print_exc()
			model = None
			tokenizer = None
			generation_pipe = None


def load_model_fallback():
	"""普通加载方法（无量化）"""
	global model, tokenizer, generation_pipe
	try:
		print("使用普通模式加载模型...")
		
		if torch.cuda.is_available():
			device_map = "cuda"
			torch_dtype = torch.float16
		else:
			device_map = "cpu"
			torch_dtype = torch.float32
		
		model = AutoModelForCausalLM.from_pretrained(
			MODEL_PATH,
			device_map=device_map,
			torch_dtype=torch_dtype,
			low_cpu_mem_usage=True
		)
		tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
		
		device = 0 if torch.cuda.is_available() else -1
		generation_pipe = pipeline(
			"text-generation",
			model=model,
			tokenizer=tokenizer,
			device=device
		)
		print("模型加载成功")
	except Exception as e:
		print(f"模型加载失败: {e}")
		traceback.print_exc()


def load_model_cpu():
	"""备用 CPU 加载方法"""
	global model, tokenizer, generation_pipe
	try:
		print("使用 CPU 加载模型...")
		model = AutoModelForCausalLM.from_pretrained(
			MODEL_PATH,
			device_map="cpu",
			torch_dtype=torch.float32
		)
		tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
		
		generation_pipe = pipeline(
			"text-generation",
			model=model,
			tokenizer=tokenizer,
			device=-1
		)
		print("CPU 模型加载成功（注意：推理速度可能较慢）")
	except Exception as e:
		print(f"CPU 模型加载失败: {e}")
		traceback.print_exc()


# 在应用启动时加载模型
load_model()


def clean_model_output(raw_text: str) -> str:
	"""清理模型输出，提取干净的结论"""
	import re
	
	# 移除 </think> 标签及其后的内容
	if '</think>' in raw_text:
		raw_text = raw_text.split('</think>')[0].strip()
	
	# 移除 prompt 模板中的占位符
	raw_text = re.sub(r'\[简要说明判断依据，?50字以内\]', '', raw_text)
	raw_text = re.sub(r'\[是刷单文本\] 或 \[不是刷单文本\]', '', raw_text)
	
	# 移除 "请开始分析：" 这样的前缀
	raw_text = re.sub(r'请开始分析[：:]\s*', '', raw_text)
	
	# 提取结论（找第一次出现的"是刷单文本"或"不是刷单文本"）
	is_spam = None
	if '不是刷单文本' in raw_text:
		is_spam = False
	elif '是刷单文本' in raw_text:
		is_spam = True
	
	# 提取理由（从"理由"、"原因"、"分析"等关键词后开始）
	reasons = []
	for keyword in ['理由', '原因', '分析', '依据']:
		# 使用更精确的正则，匹配到下一个空行或字符串结尾
		pattern = rf'{keyword}[：:]\s*([^\n\[].*?)(?=\n\n|\n判断：|\n请开始|$)'
		matches = re.findall(pattern, raw_text, re.DOTALL)
		if matches:
			reasons = [m.strip() for m in matches if m.strip() and len(m.strip()) > 5]
			if reasons:
				break
	
	# 如果没有找到明确的理由，提取结论后的所有非空行
	if not reasons:
		# 找到结论位置
		conclusion_pos = -1
		for kw in ['不是刷单文本', '是刷单文本']:
			pos = raw_text.find(kw)
			if pos != -1:
				conclusion_pos = pos + len(kw)
				break
		
		if conclusion_pos > 0:
			after_conclusion = raw_text[conclusion_pos:].strip()
			# 移除"理由："这样的前缀
			after_conclusion = re.sub(r'^理由[：:]\s*', '', after_conclusion)
			# 按行分割，过滤掉空行和无关内容
			lines = [line.strip() for line in after_conclusion.split('\n') 
			         if line.strip() 
			         and '请开始' not in line
			         and '判断：' not in line
			         and not line.startswith('[')]
			reasons = lines[:2]  # 最多取2行
	
	# 拼接结果
	conclusion = "是刷单文本" if is_spam else ("不是刷单文本" if is_spam is not None else "无法判断")
	reason_text = reasons[0] if reasons else "无明显特征"
	
	# 清理多余的空白和换行
	reason_text = re.sub(r'\s+', ' ', reason_text).strip()
	
	# 限制理由长度（截断过长的理由）
	if len(reason_text) > 100:
		reason_text = reason_text[:100] + "..."
	
	return f"{conclusion}\n理由：{reason_text}"


def ask_model(review: str) -> str:
	"""使用生成式模型判断评论是否为刷单文本"""
	global generation_pipe

	if not generation_pipe:
		load_model()  # 尝试重新加载
		if not generation_pipe:
			return "模型未成功加载，无法进行判断"

	try:
		print(f"开始处理评论: {review[:30]}...")

		# 优化后的提示模板 - 避免使用方括号
		prompt = (
				"你是一位专业的电商评论分析专家。请判断以下评论是否是刷单文本（虚假评论）。\n\n"
				"刷单文本的特征包括：\n"
				"- 过度赞美，使用重复或夸张的词汇\n"
				"- 内容空洞，缺乏具体使用体验\n"
				"- 强调物流速度等与产品本身无关的内容\n"
				"- 多个优点堆砌，缺乏缺点描述\n\n"
				"请直接输出判断结果和理由，格式如下：\n"
				"判断：是刷单文本 或 不是刷单文本\n"
				"理由：简要说明判断依据\n\n"
				f"待分析评论：\n{review}\n\n"
				"判断结果："
		)

		# 使用文本生成管道
		generated_results = generation_pipe(
			prompt,
			max_new_tokens=150,  # 限制生成的新token数量
			num_return_sequences=1,
			do_sample=True,  # 使用采样增加多样性
			temperature=0.7,  # 控制创造性
			top_p=0.9,
			eos_token_id=tokenizer.eos_token_id,
			pad_token_id=tokenizer.pad_token_id,
			truncation=True,  # 明确启用截断
			return_full_text=False  # 不返回原始 prompt
		)

		# 提取生成的文本
		generated_text = generated_results[0]['generated_text'].strip()
		print("模型原始输出：\n", generated_text)
		
		# 清理模型输出
		cleaned_text = clean_model_output(generated_text)
		print("清理后输出：\n", cleaned_text)
		
		return cleaned_text
	
	except Exception as e:
		print(f"处理评论时出错: {e}")
		traceback.print_exc()
		return f"处理评论时出错: {str(e)}"


@app.route('/api/input', methods=['POST', 'OPTIONS'])
def analyze_comments():
	"""API接口，接收评论列表并返回判断结果"""
	# 处理 OPTIONS 预检请求
	if request.method == 'OPTIONS':
		response = jsonify({})
		response.headers.add('Access-Control-Allow-Origin', '*')
		response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
		response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
		return response, 200
	
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
		response = jsonify(results)
		response.headers.add('Access-Control-Allow-Origin', '*')
		return response, 200

	except Exception as e:
		print(f"API处理出错: {e}")
		traceback.print_exc()
		response = jsonify({"error": f"服务器内部错误: {str(e)}"})
		response.headers.add('Access-Control-Allow-Origin', '*')
		return response, 500


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
	# 注意：debug=True 会导致模型在代码变化时重新加载，耗时较长
	# 生产环境建议使用 use_reloader=False
	app.run(host="127.0.0.1", port=8989, debug=True, use_reloader=False)