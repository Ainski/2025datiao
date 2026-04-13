from transformers import (AutoTokenizer,
                          AutoModelForCausalLM,
                          BitsAndBytesConfig,
                          TrainingArguments,
                          Trainer)

from .config import configure,lora_config,training_args

from .utils.log import loginfo
from .utils.dataloader import load_jsonl_to_dict_list
from datasets import load_dataset
from peft import LoraConfig,get_peft_model,TaskType,PeftModel

import os

# 数据整理函数
def process_function(examples, tokenizer):
	"""将数据集转换为模型可接受的格式"""
	max_length = 256  # 可根据需要调整

	# 拼接prompt和completion
	inputs = [f"{p}\n{c}" for p, c in zip(examples["prompt"], examples["completion"])]

	# 分词（添加padding确保批次内长度一致）
	tokenized = tokenizer(
		inputs,
		truncation=True,
		max_length=max_length,
		padding="max_length",
		return_tensors=None
	)

	# labels与input_ids相同（用于因果语言建模）
	tokenized["labels"] = tokenized["input_ids"].copy()

	return tokenized

def train():

	#  加载模型和分词器
	os.environ["TENSORBOARD_LOGGING_DIR"] = configure["log_dir"]
	tokenizer = AutoTokenizer.from_pretrained(configure["model_name"])
	loginfo("Tokenizer loaded successfully")

	#  加载数据

	dataset = load_dataset("json",
	                       data_files={
		                       "train": configure["train_data"]
	                       },
	                       split="train"
	                       )
	train_test_split = dataset.train_test_split(test_size=configure["train_test_split"])
	train_dataset = train_test_split["train"]
	eval_dataset = train_test_split["test"]
	loginfo("Dataset loaded successfully")

	# 处理数据集
	loginfo("Processing datasets...")
	train_dataset = train_dataset.map(
		lambda examples: process_function(examples, tokenizer),
		batched=True,
		remove_columns=dataset.column_names
	)
	eval_dataset = eval_dataset.map(
		lambda examples: process_function(examples, tokenizer),
		batched=True,
		remove_columns=dataset.column_names
	)
	loginfo("Datasets processed successfully")


	# 加载量化模型
	quantization_config = BitsAndBytesConfig(
		load_in_4bit=True,
		bnb_4bit_compute_dtype="float16",
		bnb_4bit_quant_type="nf4",
		llm_int8_enable_fp32_cpu_offload=True
	)
	
	# 使用自定义device_map以支持CPU offload
	device_map = {
		"transformer.word_embeddings": 0,
		"transformer.rotary_emb": 0,
	}
	
	model = AutoModelForCausalLM.from_pretrained(
		configure["model_name"],
		quantization_config=quantization_config,
		device_map="auto"
	)
	loginfo("Model quantized successfully")
	
	# 加载lora微调模型
	model = get_peft_model(model, lora_config)
	model.print_trainable_parameters()
	loginfo("Model PEFTed successfully")
	
	trainer = Trainer(
		model=model,
		args=training_args,
		train_dataset=train_dataset,
		eval_dataset=eval_dataset,
	)
	loginfo("Trainer created successfully")
	trainer.train()
	loginfo("Model trained successfully")
	
	model.save_pretrained(configure["save_path"])
	tokenizer.save_pretrained(configure["save_path"])
	
	loginfo("Model saved to"+configure["save_path"])
	
	base_model = AutoModelForCausalLM.from_pretrained(configure["model_name"],device_map="auto")
	model = PeftModel.from_pretrained(configure["save_path"],base_model=base_model)
	model = model.merge_and_unload()
	model.save_pretrained(configure["final_save_path"])
	
	tokenizer.save_pretrained(configure["final_save_path"])
	
	loginfo("Final model saved to"+configure["final_save_path"],"end")
	
	
	