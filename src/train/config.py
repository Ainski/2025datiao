from peft import LoraConfig,TaskType
from transformers import TrainingArguments,Trainer

#  所有路径应该以src 文件夹为根目录
configure={
	"model_name":"./train/model/qwen_7b",
	"output_model_dir" : "./train/models/finetuned_models_7b",
	"save_path" : "./train/models/saved_lora_model_7b",
	"final_save_path":"./train/models/saved_full_model_7b",
	"train_data" : "./train/data/train.jsonl",
	"train_test_split":0.15,
	"log_dir":"./train/logs"
}

lora_config = LoraConfig(
	r=8,
	lora_alpha=16,
	lora_dropout=0.05,
	task_type=TaskType.CAUSAL_LM
)

training_args = TrainingArguments(
    output_dir="./finetuned_models_7b",
    num_train_epochs=20,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=16,
    gradient_checkpointing=True,
    fp16=True,
    logging_steps=10,
    save_steps=100,
    eval_strategy="steps",
    eval_steps=50,
    learning_rate=2e-4,
    remove_unused_columns=False,
    #run_name="qwen1.5b_finetune"
    run_name="qwen7b_finetune"
)