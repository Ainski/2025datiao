from dsapi import call_deepseek_api
from utils import *
import os
import time
from DrissionPage import ChromiumPage
import requests
def make_prompt(data:dict):
    prompt = "现在给出关于网站上某个产品的以及其评论的相关信息：请你判断是否为一条刷单评论。刷单评论指的是评论内容大量重复、无意义、或与产品无关的评论。"
    prompt += f"{data}"
    prompt += "请逐条评论分析风险等级[低风险、中风险、高风险]，并给出理由。请以json的格式提交，json的格式如下：\n"
    prompt += "{\n"
    prompt += "    \"details\": [{\n"
    prompt += "        \"User\": \"用户昵称\",\n"
    prompt += "        \"comment_date\": \"评论日期\",\n"
    prompt += "        \"comment_score\": \"评论分数\",\n"
    prompt += "        \"praise_count\": \"点赞数\",\n"
    prompt += "        \"wareAttribute\": \"购买型号\"\n"
    prompt += "        \"content\": \"评论内容\",\n"
    prompt += "        \"risk_level\": \"低风险/中风险/高风险\",\n"
    prompt += "        \"reason\": \"理由\"\n"
    prompt += "    }],\n"
    prompt += "    \"overviews\"{\n"
    prompt += "        \"Product\": \"商品名称\",\n"
    prompt += "        \"Price\": \"商品价格\",\n"
    prompt += "        \"total_comments\": \"总评论数\",\n"
    prompt += "        \"low_risk_comments\": \"低风险评论数\",\n"
    prompt += "        \"mid_risk_comments\": \"中风险评论数\",\n"
    prompt += "        \"high_risk_comments\": \"高风险评论数\",\n"
    prompt += "        \"overview_risk_level\": \"风险等级\",\n"
    prompt += "        \"overview_reason\": \"理由\"\n"
    prompt += "    }\n"
    prompt += "}"
    return prompt
# def main():
#
#     read_path=r"clear_data/demo%d.json"
#     save_path=r"clear_data/result%d.json"
#     for i in range(1,6):
#         f = read_path%i
#         ifs = open(f, 'r', encoding='utf-8')
#
#         data = ifs.read() #读取所有文件内容
#         ifs.close()
#
#         prompt = make_prompt(data) #生成prompt
#
#         result = call_deepseek_api(prompt) #调用API
#         if type(result)!=str:
#             print(result)
#         clear_result=extract_and_parse_json(result) #清洗并解析json
#
#         sf = save_path%i #保存文件名
#         save_json_output(sf,clear_result) #保存json文件
#         print(f"第{i}个文件处理完成")
#         print(recursive_print_json(clear_result))
def monitor_jd_buttons():
    """监听所有标签页中的京东商品页面"""
    page = ChromiumPage()
    processed_urls = set()
    
    print("已打开浏览器，请随意浏览京东页面")
    page.get('https://www.jd.com')  # 初始页面
    count = 0
    try:
        while True:
            # 获取所有标签页（无需显式切换）
            for tab in page.get_tabs():
                current_url = tab.url
                
                if current_url.startswith('https://item.jd.com') and current_url not in processed_urls:
                    
                    print(f"发现新商品页: {current_url}")
                    processed_urls.add(current_url)
                    
                    # 直接操作标签页对象
                    tab.wait.doc_loaded()
                    # 保持原有的商品信息获取逻辑
                    raw_data = {}
                    title_elem = tab.ele('.sku-name', timeout=2)
                    price_elem = tab.ele('.price', timeout=2)
                    
                    if title_elem:
                        raw_data['title'] = title_elem.text
                        print(f"商品标题: {title_elem.text}")
                    if price_elem:
                        raw_data['price'] = price_elem.text
                        print(f"当前价格: {price_elem.text}")
                    
                    # 新增goods-base信息获取
                    goods_base = tab.ele('.goods-base', timeout=2)
                    if goods_base:
                        print("\n商品基础信息：")
                        raw_data['goods_base'] = goods_base.text
                        print(goods_base.text)
                    else:
                        print("未找到商品基础信息区块")
                    try:
                        # 新增按钮点击逻辑
                        arrow_btn = tab.ele('css:.all-btn .arrow', timeout=2)
                        if arrow_btn:
                            print("发现可点击按钮，正在模拟点击...")
                            tab.listen.start(targets=['api.m.jd.com'])  # 修改为复数形式targets
                            arrow_btn.click()
                            r = tab.listen.wait()
                            
                            if r and r.response:
                                # 合并重复的响应处理逻辑
                                
                                json_data = r.response.body
                                print("\n" + "=" * 50)
                                comments_data = json_data['result']['floors'][2]['data']
                                comments=[]
                                print(comments_data)
                                for comment in comments_data:
                                    print(comment)
                                    if 'commentInfo' not in comment:
                                        continue
                                    comment={
                                        'userNickName':comment['commentInfo']['userNickName'] if 'userNickName' in comment['commentInfo'] else '',
	                                    'wareAttribute':comment['commentInfo']['wareAttribute'] if 'wareAttribute' in comment['commentInfo'] else '',
	                                    'commentDate':comment['commentInfo']['commentDate'] if 'commentDate' in comment['commentInfo'] else '',
	                                    'commentScore':comment['commentInfo']['commentScore'] if 'commentScore' in comment['commentInfo'] else '',
	                                    'praiseCnt':comment['commentInfo']['praiseCnt'] if 'praiseCnt' in comment['commentInfo'] else '',
	                                    'commentData':comment['commentInfo']['commentData'] if 'commentData' in comment['commentInfo'] else '',
                                    }
                                    comments.append(comment)
                                print("评论数据：")
                                print(comments)
                                raw_data['comments'] = f"{comments}"
                                print("=" * 50 + "\n")
                                
                                """
                                    成功则保存数据，并调用API进行风险识别，并保存结果
                                """
                                save_path = r"clear_data/result%d.json"
                                prompt = make_prompt(raw_data)  # 生成prompt
                                result = call_deepseek_api(prompt)  # 调用API
                                clear_result = extract_and_parse_json(result)  # 清洗并解析json
                                sf = save_path % count  # 保存文件名
                                save_json_output(sf, clear_result)  # 保存json文件
                                print(recursive_print_json(clear_result))
                                count += 1
                                
                            tab.listen.stop()  # 停止监听
                        else:
                            print("未找到指定按钮元素")
                    except Exception as e:
                        print(f"操作异常: {str(e)}")

                    
            
            # 清理记录
            if len(processed_urls) > 50:
                processed_urls = set()
            
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("程序已停止")
    finally:
        page.quit()


if __name__ == "__main__":
    monitor_jd_buttons()