import requests
import streamlit as st
import json

def write_articles_for_videos(videos_with_transcripts):
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        st.error("❌ 未发现 GEMINI_API_KEY")
        return []

    articles = []
    # 强制改为 v1 正式版接口，这是最稳的路径
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}

    for video in videos_with_transcripts:
        prompt = f"你是一位新加坡政策评论员，请根据字幕写一篇深度报道：\n标题：{video['title']}\n字幕：{video['transcript']}"
        data = {"contents": [{"parts": [{"text": prompt}]}]}

        try:
            print(f"🚀 正在通过 v1 接口请求 Gemini: {video['title']}...")
            response = requests.post(url, headers=headers, data=json.dumps(data))
            result = response.json()

            if "candidates" in result:
                content_text = result['candidates'][0]['content']['parts'][0]['text']
                articles.append({
                    "title": video['title'],
                    "content": content_text,
                    "html": f"<h2>{video['title']}</h2><p>{content_text.replace('\n', '<br>')}</p>",
                    "url": video['url']
                })
                print(f" ✅ 终于写成了！")
            else:
                # 打印出具体的错误原因，比如权限、配额或地区
                print(f" ❌ API 拒绝原因: {result.get('error', {}).get('message', '未知错误')}")
        except Exception as e:
            print(f" ❌ 请求异常: {e}")

    return articles
