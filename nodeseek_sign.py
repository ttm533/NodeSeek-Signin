# -- coding: utf-8 --
import os
import sys
from datetime import datetime
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

# 获取当前时间
def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Telegram 推送函数
def telegram_Bot(token, chat_id, message):
    """Telegram 推送"""
    url = f'{telegram_api_url}/bot{token}/sendMessage'
    data = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown'  # 使用 Markdown 格式化
    }
    try:
        r = requests.post(url, json=data)
        response_data = r.json()
        print(f"Telegram推送结果：{response_data.get('ok', False)}\n")
    except Exception as e:
        print(f"Telegram推送失败：{e}")

# PushPlus 推送函数
def pushplus_ts(token, rw, msg):
    """PushPlus 推送"""
    url = 'https://www.pushplus.plus/send/'
    data = {
        "token": token,
        "title": rw,
        "content": msg,
        "template": "markdown"  # 使用 Markdown 格式化
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
        
        # 获取签到结果
        success = response_data.get('success', False)
        message = response_data.get('message', '无签到信息')
        gain = response_data.get('gain', 0)
        current = response_data.get('current', 0)

        # 处理签到状态和奖励
        status = "✅ 成功" if success else "❌ 失败"
        reward = f"{gain} 个鸡腿" if success else "无奖励"
        date = datetime.now().strftime("%Y-%m-%d") if success else "未知"

        # 格式化通知消息
        formatted_message = (
            f"--------------------------------------\n"
            f"*平台*: NodeSeek\n"
            f"*时间*: {get_current_time()}\n"
            f"*签到状态*: {status}\n"
            f"*签到日期*: {date}\n"
            f"*今日签到奖励*: {reward}\n"
            f"*累计鸡腿*: {current}\n"
            f"--------------------------------------"
        )

        # 本地打印消息
        print(formatted_message)

        # 检查推送渠道
        if not telegram_bot_token and not pushplus_token:
            print("无推送渠道，请检查通知变量是否正确")
        else:
            # 推送通知
            if telegram_bot_token and chat_id:
                telegram_Bot(telegram_bot_token, chat_id, formatted_message)

            if pushplus_token:
                pushplus_ts(pushplus_token, "NodeSeek签到", formatted_message)

    except Exception as e:
        print("发生异常:", e)
else:
    print("请先设置Cookie")
