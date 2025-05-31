from dsapi import call_deepseek_api
from utils import *
import os
def make_prompt(data):
    prompt = "现在给出关于网站上某个产品的以及其评论的相关信息：请你判断是否为一条刷单评论。刷单评论指的是评论内容大量重复、无意义、或与产品无关的评论。"
    prompt += data
    prompt += "请逐条评论分析风险等级[低风险、中风险、高风险]，并给出理由。请以json的格式提交，json的格式如下：\n"
    prompt += "{\n"
    prompt += "    \"comment\": [\n"
    prompt += "        {\n"
    prompt += "            \"content\": \"评论内容\",\n"
    prompt += "            \"risk_level\": \"低风险/中风险/高风险\",\n"
    prompt += "            \"reason\": \"理由\"\n"
    prompt += "        }\n"
    prompt += "    ]\n"
    prompt += "}"
    return prompt
def main():
    data=read_json_file("demo.json")
    demo_file=open("demo.json","r",encoding="utf-8")
    raw=demo_file.read()

if __name__ == '__main__':
    main()