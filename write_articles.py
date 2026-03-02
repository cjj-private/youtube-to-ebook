from google import genai
import streamlit as st

def write_articles_for_videos(videos_with_transcripts):
    # 1. 从 Secrets 读取 Gemini Key
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        st.error("❌ 错误: 未在 Secrets 中发现 GEMINI_API_KEY")
        return []

    # 2. 初始化最新版客户端
    client = genai.Client(api_key=api_key)

    articles = []
    print(f"✍️ 正在通过新版 Google GenAI 为 {len(videos_with_transcripts)} 个视频写稿...")

    for video in videos_with_transcripts:
        prompt = f"""
        你是一位【哈啰人力 (hellosg.org)】的资深主编，擅长以《三联生活周刊》的深度视角解读政策。
        请根据以下 YouTube 视频的字幕，写一篇高质量的中文深度报道。

        【视频标题】: {video['title']}
        【原始字幕】: {video['transcript']}
        
        要求：
        1. 标题：要有杂志感，引人入胜。
        2. 风格：文笔优美，专业拆解新加坡人力政策。
        3. 结尾：带上【哈啰人力】的独家观察。
        """

        try:
            # 使用最新版 API 调用方式
            response = client.models.generate_content(
                model="gemini-1.5-flash", 
                contents=prompt
            )
            
            articles.append({
                "title": video['title'],
                "content": response.text,
                "html": f"<h2>{video['title']}</h2><p>{response.text.replace('\n', '<br>')}</p><hr><a href='{video['url']}'>查看原视频</a>",
                "url": video['url']
            })
            print(f" ✅ 已生成文章: {video['title']}")
        except Exception as e:
            print(f" ❌ Gemini 写作失败 ({video['title']}): {e}")

    return articles
