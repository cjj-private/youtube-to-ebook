import requests
import streamlit as st
import json

def write_articles_for_videos(videos_with_transcripts):
    api_key = st.secrets.get("GROQ_API_KEY")
    if not api_key:
        st.error("❌ 未在 Secrets 中发现 GROQ_API_KEY")
        return []

    articles = []
    # Groq 的标准 API 地址
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    for video in videos_with_transcripts:
        print(f"🚀 正在通过 Groq (Llama 3) 快速生成报道: {video['title']}...")
        
        prompt = f"""
        你是一位【哈啰人力】的资深主编。请根据以下字幕写一篇深度政策分析文章。
        标题: {video['title']}
        字幕内容: {video['transcript']}
        
        要求：
        1. 文风参考《三联生活周刊》，优雅且专业。
        2. 深度分析新加坡人力政策对外国劳工的具体影响。
        3. 结尾带上【哈啰人力】的独家观察。
        """

        data = {
            "model": "llama-3.3-70b-versatile", # 使用最强的 70B 模型
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
                articles.append({
                    "title": video['title'],
                    "content": content_text,
                    "html": f"<h2>{video['title']}</h2><p>{content_text.replace('\n', '<br>')}</p>",
                    "url": video['url']
                })
                print(f" ✅ 【重大突破】Groq 成功写好了文章！")
            else:
                error_info = result.get('error', {}).get('message', '未知错误')
                print(f" ❌ Groq 报错: {error_info}")
        except Exception as e:
            print(f" ❌ 请求异常: {e}")

    return articles
