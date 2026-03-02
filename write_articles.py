import requests
import streamlit as st
import json

def write_articles_for_videos(videos_with_transcripts):
    # 1. 从 Secrets 读取你刚才申请的那个新 Key
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        st.error("❌ 未在 Secrets 中发现 GEMINI_API_KEY")
        return []

    articles = []
    # 使用 v1beta 接口配合最新申请的 Key 是最稳的
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}

    for video in videos_with_transcripts:
        print(f"🚀 正在尝试为视频生成深度报道: {video['title']}...")
        
        # 针对 hellosg.org 优化 Prompt
        prompt = f"""
        你是一位【哈啰人力】的资深主编。请根据以下字幕写一篇深度政策分析文章。
        标题: {video['title']}
        字幕内容: {video['transcript']}
        
        要求：
        1. 使用《三联生活周刊》风格，文章要优雅、专业。
        2. 深度分析新加坡人力政策对外国劳工的具体影响。
        3. 结尾带上【哈啰人力】的独家观察。
        """

        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }

        try:
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
                print(f" ✅ 终于成功了！哈啰人力文章已生成。")
            else:
                # 打印出具体的错误信息，比如是不是地区不支持或权限问题
                error_msg = result.get('error', {}).get('message', '未知错误')
                print(f" ❌ API 拒绝请求: {error_msg}")
        except Exception as e:
            print(f" ❌ 请求异常: {e}")

    return articles
