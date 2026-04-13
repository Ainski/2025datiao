import argparse
from train.utils.log import loginfo
from train.train import train
from train.validate import validate
from train.test import inference

def main():
	loginfo("智鉴引擎 启动", "start")

	parser = argparse.ArgumentParser(description="智鉴引擎——基于大语言模型的C端网购反刷单决策辅助系统")

	parser.add_argument("-v", "--version", action="version", version="%(prog)s 1.0")
	parser.add_argument(
		"--validate",
	    action="store_true",
		help="validate training pipeline with 2 samples"
	)
	parser.add_argument(
		"-t",
		"--train",
	    action="store_true",
		help="strat training model,if set, will train the model first"
	)
	parser.add_argument(
		"--eval-text",
		type=str,
		help="evaluate the text,if set, will evaluate the text"
		)

	args = parser.parse_args()

	loginfo(f"运行参数: validate={args.validate}, train={args.train}, eval_text={args.eval_text}")

	if args.validate:
		loginfo("开始验证训练流程...", "start")
		validate()
		loginfo("验证流程完成", "end")
	elif args.train:
		loginfo("开始训练模型...", "start")
		train()
		loginfo("模型训练完成", "end")
	else:
		loginfo("未设置训练参数，跳过训练阶段")

	if args.eval_text is not None:
		loginfo(f"开始评估文本: {args.eval_text}", "start")
		inference(args.eval_text)
		loginfo("文本评估完成", "end")
	else:
		loginfo("未提供评估文本，跳过评估阶段")
	
	loginfo("程序执行完毕", "end")
	
	
	
if __name__ == '__main__':
	main()