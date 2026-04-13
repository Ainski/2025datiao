from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, TaskType
from .config import configure, lora_config, training_args
from .utils.log import loginfo
from datasets import load_dataset
import os
import torch

def validate():
	"""验证整个训练流程是否正常运行"""
	
	print("="*60)
	print("开始验证训练流程...")
	print("="*60)
	
	# 1. 验证GPU可用性
	print("\n[1/6] 检查GPU可用性...")
	if not torch.cuda.is_available():
		raise RuntimeError("CUDA 不可用！")
	print(f"✓ GPU 可用: {torch.cuda.get_device_name(0)}")
	print(f"✓ GPU 显存: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
	
	# 2. 加载tokenizer
	print("\n[2/6] 加载Tokenizer...")
	tokenizer = AutoTokenizer.from_pretrained(configure["model_name"])
	print("✓ Tokenizer 加载成功")
	
	# 3. 加载数据集（只取少量样本）
	print("\n[3/6] 加载并处理数据集（验证模式，仅2个样本）...")
	dataset = load_dataset("json",
	                       data_files={"train": configure["train_data"]},
	                       split="train[:2]")  # 只取前2个样本
	
	# 处理数据集
	from .train import process_function
	dataset = dataset.map(
		lambda examples: process_function(examples, tokenizer),
		batched=True,
		remove_columns=dataset.column_names
	)
	print(f"✓ 数据集加载成功，共 {len(dataset)} 个样本")
	
	# 4. 加载量化模型
	print("\n[4/6] 加载量化模型...")
	quantization_config = BitsAndBytesConfig(
		load_in_4bit=True,
		bnb_4bit_compute_dtype="float16",
		bnb_4bit_quant_type="nf4",
		llm_int8_enable_fp32_cpu_offload=True
	)
	
	model = AutoModelForCausalLM.from_pretrained(
		configure["model_name"],
		quantization_config=quantization_config,
		device_map="auto"
	)
	print("✓ 模型量化成功")
	
	# 5. 加载LoRA配置
	print("\n[5/6] 应用LoRA配置...")
	model = get_peft_model(model, lora_config)
	model.print_trainable_parameters()
	print("✓ LoRA 配置应用成功")
	
	# 6. 测试前向传播和反向传播
	print("\n[6/6] 测试前向传播和反向传播...")
	model.train()
	
	# 取一个样本进行测试
	sample = dataset[0]
	input_ids = torch.tensor([sample["input_ids"]]).cuda()
	labels = torch.tensor([sample["labels"]]).cuda()
	
	# 前向传播
	with torch.amp.autocast('cuda'):
		outputs = model(input_ids=input_ids, labels=labels)
		loss = outputs.loss
	
	print(f"✓ 前向传播成功，Loss: {loss.item():.4f}")
	
	# 反向传播
	loss.backward()
	print("✓ 反向传播成功！")
	
	# 清理显存
	del model, tokenizer, input_ids, labels, outputs, loss
	torch.cuda.empty_cache()
	
	print("\n" + "="*60)
	print("🎉 所有验证步骤通过！训练流程正常！")
	print("="*60)
	print("\n现在可以安全地运行正式训练了。")
