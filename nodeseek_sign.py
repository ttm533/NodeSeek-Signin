# -- coding: utf-8 --
import os
import sys
from curl_cffi import requests

# 环境变量配置
NS_RANDOM = os.environ.get("NS_RANDOM", "true")
NS_COOKIE = os.environ.get("NS_COOKIE", "")
COOKIE = os.environ.get("COOKIE", "")
COOKIE_ENV = NS_COOKIE or COOKIE

# 推送通知的配置
pushplus_token = os.environ.get("PUSHPLUS_TOKEN")
telegram_bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
chat_id = os.environ.get("CHAT_ID", "")
telegram_api_url = os.environ.get("TELEGRAM_API_URL", "https://api.telegram.org")  # Telegram 代理API

# Telegram 推送函数
def telegram_Bot(token, chat_id, message):
    """Telegram 推送"""
    # 在消息中添加 NodeSeek 标识
    message = f"NodeSeek: {message}"
    
    url = f'{telegram_api_url}/bot{token}/sendMessage'
    data = {
        'chat_id': chat_id,
        'text': message
    }
    
    try:
        r = requests.post(url, json=data)
        response_data = r.json()
        msg = response_data['ok']
        print(f"Telegram推送结果：{msg}\n")
    except Exception as e:
        print(f"Telegram推送失败：{e}")

# PushPlus 推送函数
def pushplus_ts(token, rw, msg):
    """PushPlus 推送"""
    # 在消息中添加 NodeSeek 标识
    msg = f"NodeSeek: {msg}"
    
    url = 'https://www.pushplus.plus/send/'
    data = {
        "token": token,
        "title": rw,
        "content": msg
    }
    
    try:
        r = requests.post(url, json=data)
        msg = r.json().get('msg', None)
        print(f'PushPlus推送结果：{msg}\n')
    except Exception as e:
        print(f"PushPlus推送失败：{e}")

# 加载通知服务（可选）
def load_send():
    global send
    global hadsend
    cur_path = os.path.abspath(os.path.dirname(__file__))
    sys.path.append(cur_path)
    if os.path.exists(cur_path + "/notify.py"):
        try:
            from notify import send
            hadsend = True
        except:
            print("加载notify.py的通知服务失败，请检查~")
            hadsend = False
    else:
        print("加载通知服务失败, 缺少notify.py文件")
        hadsend = False
load_send()

# 判断是否有有效的 COOKIE
if COOKIE_ENV:
    url = f"https://www.nodeseek.com/api/attendance?random={NS_RANDOM}"
    
    # 请求头
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0",
        'sec-ch-ua': "\"Not A(Brand\";v=\"99\", \"Microsoft Edge\";v=\"121\", \"Chromium\";v=\"121\"",
        'sec-ch-ua-mobile': "?0",
        'sec-ch-ua-platform': "\"Windows\"",
        'origin': "https://www.nodeseek.com",
        'sec-fetch-site': "same-origin",
        'sec-fetch-mode': "cors",
        'sec-fetch-dest': "empty",
        'referer': "https://www.nodeseek.com/board",
        'accept-language': "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        'Cookie': COOKIE_ENV
    }

    try:
        # 发送签到请求
        response = requests.post(url, headers=headers, impersonate="chrome110")
        response_data = response.json()
        print(response_data)
        print(COOKIE_ENV)
        
        # 获取响应信息
        message = response_data.get('message')
        success = response_data.get('success')
        
        # 发送通知
        send("nodeseek签到", message)
        
        if success == "true":
            print(message)
            # 如果 Telegram 配置有效，发送 Telegram 通知
            if telegram_bot_token and chat_id:
                telegram_Bot(telegram_bot_token, chat_id, message)
        else:
            print(message)
            # 如果 Telegram 配置有效，发送 Telegram 通知
            if telegram_bot_token and chat_id:
                telegram_Bot(telegram_bot_token, chat_id, message)
            # 如果 PushPlus 配置有效，发送 PushPlus 通知
            if pushplus_token:
                pushplus_ts(pushplus_token, "nodeseek签到", message)
    except Exception as e:
        print("发生异常:", e)
        print("实际响应内容:", response.text)
else:
    print("请先设置Cookie")
