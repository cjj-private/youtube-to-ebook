import requests
import streamlit as st
import json

def write_articles_for_videos(videos_with_transcripts):
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        st.error("❌ 未在 Secrets 中发现 GEMINI_API_KEY")
        return []

    articles = []
    # 强制指定 v1 版本的正式地址，绕过 v1beta
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}

    print(f"✍️ 正在通过原生 HTTP 接口为 {len(videos_with_transcripts)} 个视频写稿...")

    for video in videos_with_transcripts:
        prompt = f"""
        你是一位【哈啰人力 (hellosg.org)】的资深主编，擅长以《三联生活周刊》的深度视角解读政策。
        请根据以下视频字幕，写一篇高质量的新加坡政策深度报道。

        标题: {video['title']}
        字幕: {video['transcript']}
        
        要求：
        1. 标题要引人入胜。
        2. 文风优美，专业拆解政策对外国劳工的影响。
        3. 结尾带上【哈啰人力】的独家观察。
        """

        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }

        try:
            # 直接发起 HTTP 请求
            response = requests.post(url, headers=headers, data=json.dumps(data))
            result = response.json()

            # 解析返回的 JSON
            if "candidates" in result:
                content_text = result['candidates'][0]['content']['parts'][0]['text']
                articles.append({
                    "title": video['title'],
                    "content": content_text,
                    "html": f"<h2>{video['title']}</h2><p>{content_text.replace('\n', '<br>')}</p>",
                    "url": video['url']
                })
                print(f" ✅ Gemini 终于写成了: {video['title']}")
            else:
                print(f" ❌ API 返回错误: {result}")
        except Exception as e:
            print(f" ❌ 请求发生异常: {e}")

    return articles
