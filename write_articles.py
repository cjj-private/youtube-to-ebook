import requests
import streamlit as st
import json

def write_articles_for_videos(videos_with_transcripts):
    api_key = st.secrets.get("GROQ_API_KEY")
    if not api_key:
        st.error("❌ 未发现 GROQ_API_KEY")
        return []

    articles = []
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    for video in videos_with_transcripts:
        print(f"🚀 正在为视频生成深度报道: {video['title']}...")
        
        # 注意：这里的 prompt 变量必须和上方的 for 循环保持对齐（通常是 8 个空格或 2 个 Tab）
        prompt = f"""
        你是一位深度内容拆解专家。请根据以下视频字幕写一篇深度分析文章。
        标题: {video['title']}
        字幕内容: {video['transcript']}
        
        要求：
        1. 风格优雅、有洞察力，类似《三联生活周刊》的深度感。
        2. 提炼出视频中的 3 个核心观点或金句。
        3. 结尾总结该内容对读者的实际启发。
        """

        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "你是一位专业的深度内容分析主编。"},
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
                    "article": content_text,
                    "url": video['url'],
                    "channel": video.get('channel', 'YouTube Channel'),
                    "content": content_text
                })
                print(f" ✅ 文章生成成功！")
            else:
                print(f" ❌ Groq 报错: {result.get('error', {}).get('message')}")
        except Exception as e:
            print(f" ❌ 请求异常: {e}")

    return articles
