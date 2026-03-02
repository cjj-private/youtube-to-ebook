import google.generativeai as genai
import streamlit as st

# 从 Secrets 读取 Gemini Key
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY")

def write_articles_for_videos(videos_with_transcripts):
    if not GEMINI_API_KEY:
        st.error("❌ 请在 Secrets 中添加 GEMINI_API_KEY")
        return []

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')

    articles = []
    for video in videos_with_transcripts:
        # 更加精准的哈啰人力 Prompt
        prompt = f"""
        你是一位【哈啰人力】资深主编。请根据视频字幕写一篇深度报道。
        
        视频标题: {video['title']}
        字幕内容: {video.get('transcript', '无字幕')}
        视频链接: {video['url']}
        
        要求：
        1. 标题：要有吸引力（例如：从XX看新加坡外劳政策的温情转弯）。
        2. 文风：参考《三联生活周刊》，客观、专业且有深度。
        3. 语言：简体中文。
        4. 结尾：加入【哈啰人力 (hellosg.org)】的专家点评。
        """
        
        try:
            response = model.generate_content(prompt)
            # 这里的 content 是纯文本，html 是给邮件和网页用的
            articles.append({
                "title": video['title'],
                "content": response.text,
                "html": f"<h2>{video['title']}</h2><p>{response.text.replace('\n', '<br>')}</p><hr><a href='{video['url']}'>查看原视频</a>",
                "url": video['url']
            })
            print(f" ✅ Gemini 已成功生成文章: {video['title']}")
        except Exception as e:
            print(f" ❌ Gemini 写作失败: {e}")
            
    return articles
