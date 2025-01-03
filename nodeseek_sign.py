# -- coding: utf-8 --
import os
import sys
from curl_cffi import requests
from datetime import datetime

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

# 格式化时间
def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 格式化通知内容
def format_message(platform, status, reward, date):
    return (
        f"--------------------------------------\n"
        f"*平台*: {platform}\n"
        f"*时间*: {get_current_time()}\n"
        f"*签到状态*: {status}\n"
        f"*签到日期*: {date}\n"
        f"*今日签到奖励*: {reward}\n"
        f"--------------------------------------"
    )

# Telegram 推送函数
def telegram_Bot(token, chat_id, message):
    """Telegram 推送"""
    url = f'{telegram_api_url}/bot{token}/sendMessage'
    data = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown'  # 使用Markdown格式
    }
    try:
        r = requests.post(url, json=data)
        response_data = r.json()
        msg = response_data['ok']
        print(f"Telegram推送结果：{msg}\n")
    except Exception as e:
        print(f"Telegram推送失败：{e}")

# PushPlus 推送函数
def pushplus_ts(token, title, msg):
    """PushPlus 推送"""
    url = 'https://www.pushplus.plus/send/'
    data = {
        "token": token,
        "title": title,
        "content": msg,
        "template": "markdown"  # 使用Markdown格式
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
        reward = response_data.get('reward', '无奖励')
        date = response_data.get('date', '未知')

        # 格式化消息
        formatted_message = format_message(
            platform="NodeSeek",
            status="成功" if success == "true" else "失败",
            reward=reward,
            date=date
        )

        # 本地打印消息
        print(formatted_message)

        # 发送通知
        send("NodeSeek签到", message)

        if telegram_bot_token and chat_id:
            telegram_Bot(telegram_bot_token, chat_id, formatted_message)

        if pushplus_token:
            pushplus_ts(pushplus_token, "NodeSeek签到", formatted_message)

    except Exception as e:
        print("发生异常:", e)
else:
    print("请先设置Cookie")
