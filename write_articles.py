import requests
import streamlit as st
import json

def write_articles_for_videos(videos_with_transcripts):
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        st.error("❌ 未在 Secrets 中发现 GEMINI_API_KEY")
        return []

    articles = []
    # 尝试两个可能的模型路径
    model_options = ["gemini-1.5-flash", "gemini-1.5-flash-latest", "gemini-pro"]
    
    headers = {'Content-Type': 'application/json'}

    for video in videos_with_transcripts:
        success = False
        prompt = f"你是一位新加坡政策评论员。请根据以下内容写深度报道：\n标题：{video['title']}\n字幕：{video['transcript']}"
        data = {"contents": [{"parts": [{"text": prompt}]}]}

        # 循环尝试不同的模型名称，直到有一个成功
        for model_name in model_options:
            url = f"https://generativelanguage.googleapis.com/v1/models/{model_name}:generateContent?key={api_key}"
            
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
                    print(f" ✅ 使用 {model_name} 成功生成文章!")
                    success = True
                    break # 成功了就跳出模型尝试循环
                else:
                    print(f" ⚠️ 模型 {model_name} 尝试失败，继续尝试下一个...")
            except Exception as e:
                continue

        if not success:
            print(f" ❌ 所有模型路径均尝试失败。")

    return articles
