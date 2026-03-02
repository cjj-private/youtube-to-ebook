import google.generativeai as genai
import streamlit as st

def write_articles_for_videos(videos_with_transcripts):
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        st.error("❌ 未在 Secrets 中发现 GEMINI_API_KEY")
        return []

    # 核心配置：直接初始化
    genai.configure(api_key=api_key)
    
    # 尝试使用最新的稳定版模型全名
    model = genai.GenerativeModel('gemini-1.5-flash')

    articles = []
    print(f"✍️ 正在通过 Gemini 稳定版接口写稿...")

    for video in videos_with_transcripts:
        prompt = f"你是一位新加坡政策评论员。请根据以下字幕写一篇深度报道：\n\n标题：{video['title']}\n字幕：{video['transcript']}"

        try:
            # 这里的 generate_content 不加任何复杂参数
            response = model.generate_content(prompt)
            
            # 检查是否有内容返回
            if response.text:
                articles.append({
                    "title": video['title'],
                    "content": response.text,
                    "html": f"<h2>{video['title']}</h2><p>{response.text.replace('\n', '<br>')}</p>",
                    "url": video['url']
                })
                print(f" ✅ 已成功生成文章!")
        except Exception as e:
            # 如果 Flash 报错，最后一搏：尝试切换到 Pro 模型
            print(f" ⚠️ Flash 模型调用失败，正在尝试切换到 gemini-pro...")
            try:
                backup_model = genai.GenerativeModel('gemini-pro')
                response = backup_model.generate_content(prompt)
                articles.append({
                    "title": video['title'],
                    "content": response.text,
                    "html": f"<h2>{video['title']}</h2><p>{response.text.replace('\n', '<br>')}</p>",
                    "url": video['url']
                })
                print(f" ✅ 使用 gemini-pro 成功生成文章!")
            except Exception as e2:
                print(f" ❌ 所有模型均调用失败: {e2}")

    return articles
