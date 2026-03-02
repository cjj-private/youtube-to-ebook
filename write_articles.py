import requests
import streamlit as st
import json

def write_articles_for_videos(videos_with_transcripts):
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        st.error("❌ 未在 Secrets 中发现 GEMINI_API_KEY")
        return []

    # 🔑 这是最关键的部分：所有的模型“备用钥匙”
    # 如果你在新加坡，gemini-1.5-flash 绝对存在，只是路径需要试出来
    possible_models = [
        "gemini-1.5-flash",
        "models/gemini-1.5-flash",
        "gemini-1.5-flash-latest",
        "models/gemini-1.5-flash-latest",
        "gemini-pro"
    ]
    
    # 尝试两种 API 版本路径
    api_versions = ["v1beta", "v1"]
    
    articles = []
    headers = {'Content-Type': 'application/json'}

    for video in videos_with_transcripts:
        success = False
        prompt = f"你是一位新加坡政策评论员，请根据字幕写一篇深度报道：\n标题：{video['title']}\n字幕：{video['transcript']}"
        data = {"contents": [{"parts": [{"text": prompt}]}]}

        print(f"🚀 开始为视频进行多路径爆破: {video['title']}...")

        # 嵌套循环尝试所有组合
        for ver in api_versions:
            if success: break
            for model_name in possible_models:
                url = f"https://generativelanguage.googleapis.com/{ver}/{model_name}:generateContent?key={api_key}"
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
                        print(f" ✨ 爆破成功！路径: {ver}/{model_name}")
                        success = True
                        break
                    else:
                        print(f" ⏳ 尝试 {ver}/{model_name} 失败: {result.get('error', {}).get('message', '未知错误')}")
                except:
                    continue
        
        if not success:
            st.warning(f"❌ 视频 '{video['title']}' 尝试了所有路径均失败，请检查 API Key 是否真的有效。")

    return articles
