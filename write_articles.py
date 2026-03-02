import google.generativeai as genai
import streamlit as st

# 从 Secrets 读取 Gemini Key (去 AI Studio 免费拿)
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY")

def write_articles_for_videos(videos_with_transcripts):
    if not GEMINI_API_KEY:
        st.error("❌ 请在 Secrets 中添加 GEMINI_API_KEY (免费版)")
        return []

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash') # 使用免费且快速的模型

    articles = []
    for video in videos_with_transcripts:
        prompt = f"""
        你是一位【哈啰人力】的资深政策评论员。请根据以下视频字幕写一篇深度报道。
        
        视频标题: {video['title']}
        字幕内容: {video['transcript']}
        
        要求：
        1. 使用《三联生活周刊》文风，针对新加坡外劳政策进行解读。
        2. 语言为简体中文。
        3. 标题要吸引人。
        """
        
        try:
            response = model.generate_content(prompt)
            articles.append({
                "title": video['title'],
                "content": response.text,
                "url": video['url']
            })
            print(f" ✅ Gemini 已免费生成文章: {video['title']}")
        except Exception as e:
            print(f" ❌ Gemini 生成失败: {e}")
            
    return articles
