from transformers import AutoTokenizer, AutoModelForCausalLM
#加载已经微调的模型
#final_path = "./saved_full_model"
final_path = "E:/github/2025datiao/back/deepseek-R1-qwen-1.5B/models--deepseek-ai--DeepSeek-R1-Distill-Qwen-1.5B"
model = AutoModelForCausalLM.from_pretrained(final_path,device_map="auto")
tokenizer = AutoTokenizer.from_pretrained(final_path)
#构建推理pipeline
from transformers import pipeline
pipe = pipeline("text-generation",model=model,tokenizer=tokenizer,max_length=100)
#输入评论信息
review = input("请输入评论信息：\n")
prompt = ("判断以下是否是刷单文本，并给出判断依据：\n输出内容形式如下：这个评论（是\不是）刷单文本，因为...\n" + review + "\n")
generated_text = pipe(prompt,max_length=100,num_return_sequences=1,do_sample=False)
print("任务开始：\n",generated_text[0]["generated_text"])
print("\n任务结束")