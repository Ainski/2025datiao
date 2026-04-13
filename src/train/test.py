from transformers import AutoTokenizer, AutoModelForCausalLM
from transformers import pipeline

from .config import configure
from .utils.log import loginfo
def inference(text :str) -> str:
	
	model =  AutoModelForCausalLM.from_pretrained(configure["final_save_path"],device_map="auto")
	
	tokenizer = AutoTokenizer.from_pretrained(configure["final_save_path"])
	
	pipe = pipeline('text-generation', model=model,tokenizer=tokenizer, max_lenth = 100 )
	
	prompt = (
			"判断以下是否是刷单文本，并给出判断依据：\n"
			"输出内容形式如下：这个评论（是\不是）刷单文本，因为...\n"
			+ text
			+ "\n")
	generated_text = pipe(prompt, max_length=100, num_return_sequences=1, do_sample=False)
	loginfo("任务开始：\n", generated_text[0]["generated_text"])
	loginfo("\n任务结束")
	
	return generated_text[0]["generated_text"]