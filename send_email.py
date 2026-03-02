import requests
import streamlit as st
import os

def send_newsletter(articles):
    token = st.secrets.get("TELEGRAM_BOT_TOKEN")
    chat_id = st.secrets.get("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        st.error("❌ 未发现 Telegram 配置")
        return False

    success = True
    print(f"🚀 正在向 Telegram 发送文章推送...")

    for article in articles:
        # 1. 构造优美的 TG 消息正文
        text = f"📢 *【哈啰人力】新政策解读*\n\n"
        text += f"📌 *{article['title']}*\n\n"
        # 截取前 300 字作为预览，防止消息过长
        preview = article['article'][:300] + "..."
        text += f"{preview}\n\n"
        text += f"🔗 [查看原文]({article['url']})"

        # 2. 发送文字消息 (支持 Markdown)
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }
        
        try:
            res = requests.post(url, data=payload)
            if res.status_code == 200:
                print(f" ✅ 消息已推送到 Telegram: {article['title']}")
            else:
                print(f" ❌ TG 发送失败: {res.text}")
                success = False
        except Exception as e:
            print(f" ❌ TG 请求异常: {e}")
            success = False

    # 3. (可选) 如果你想发送 EPUB 电子书文件
    # 这里可以复用你之前的 create_epub 函数逻辑，然后用 sendDocument 发送
    
    return success
