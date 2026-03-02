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
    print(f"🚀 正在向 Telegram 推送长篇文章...")

    for article in articles:
        # --- 重点修改：不再只截取 300 字 ---
        full_content = article['article']
        
        # 1. 构造消息头部
        header = f"📢 *【哈啰人力】深度专题报道*\n\n📌 *{article['title']}*\n\n"
        footer = f"\n\n🔗 [查看视频原文]({article['url']})"
        
        # 2. 检查长度 (Telegram 单条消息上限约 4000 字符)
        # 如果文章超长，我们分段发，或者直接尝试全发
        if len(full_content) > 3800:
            # 如果真的太长，先发第一部分，剩下的作为补充
            main_text = header + full_content[:3500] + " (未完待续...)" + footer
        else:
            main_text = header + full_content + footer

        # 3. 发送主消息
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": main_text,
            "parse_mode": "Markdown"
        }
        
        try:
            res = requests.post(url, data=payload)
            if res.status_code == 200:
                print(f" ✅ 完整文章已推送到 Telegram: {article['title']}")
                
                # 如果有剩余内容，补发一条（可选）
                if len(full_content) > 3500:
                    extra_text = "续前文：\n\n" + full_content[3500:]
                    requests.post(url, data={"chat_id": chat_id, "text": extra_text})
            else:
                # 如果 Markdown 解析失败（文章里有特殊字符），尝试用纯文本重发
                print(f" ⚠️ Markdown 发送失败，尝试纯文本模式...")
                payload["parse_mode"] = ""
                requests.post(url, data=payload)
                
        except Exception as e:
            print(f" ❌ TG 请求异常: {e}")
            success = False

    return success
