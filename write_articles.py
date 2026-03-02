import requests
import streamlit as st
import json

def write_articles_for_videos(videos_with_transcripts):
    api_key = st.secrets.get("GROQ_API_KEY")
    if not api_key:
        st.error("❌ 未在 Secrets 中发现 GROQ_API_KEY")
        return []

    articles = []
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    for video in videos_with_transcripts:
        print(f"🚀 正在通过 Groq 为 {video['title']} 润色文章...")
        
        prompt = f"""
        你是一位【哈啰人力】的资深主编。请根据以下字幕写一篇深度政策分析文章。
        标题: {video['title']}
        字幕内容: {video['transcript']}
        
        要求：
        1. 文风参考《三联生活周刊》，优雅且专业。
        2. 深度分析新加坡人力政策对外国劳工的具体影响。
        3. 结尾带上【哈啰人力 (hellosg.org)】的独家观察。
        """

        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "你是一位专业的政策分析主编。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }

        try:
            response = requests.post(url, headers=headers, data=json.dumps(data))
            result = response.json()

            if "choices" in result:
                content_text = result['choices'][0]['message']['content']
                
                # 关键修复：这里的 Key 必须叫 'article' 以匹配你的 send_email.py
                articles.append({
                    "title": video['title'],
                    "article": content_text,  # 统一改为 article
                    "content": content_text,  # 保留一份 content 备用
                    "url": video['url']
                })
                print(f" ✅ Groq 写作成功！")
            else:
                print(f" ❌ Groq 报错: {result.get('error', {}).get('message')}")
        except Exception as e:
            print(f" ❌ 请求异常: {e}")

    return articles
