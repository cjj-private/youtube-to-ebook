import google.generativeai as genai
import streamlit as st

def write_articles_for_videos(videos_with_transcripts):
    # 1. 从 Secrets 读取 Gemini Key
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        st.error("❌ 错误: 未在 Secrets 中发现 GEMINI_API_KEY")
        return []

    # 2. 配置 Gemini 并强制指定使用 v1 正式版接口
    try:
        genai.configure(api_key=api_key, transport='rest') # 使用 REST 模式更稳定
        # 强制指定模型名称，避开 v1beta 的坑
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
        )
    except Exception as e:
        st.error(f"配置 Gemini 失败: {e}")
        return []

    articles = []
    print(f"✍️ 正在通过 Gemini v1 接口为 {len(videos_with_transcripts)} 个视频写稿...")

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
            # 这里的 request_options 是最后的绝招，强制 API 路径
            response = model.generate_content(
                prompt
            )
            
            articles.append({
                "title": video['title'],
                "content": response.text,
                "html": f"<h2>{video['title']}</h2><p>{response.text.replace('\n', '<br>')}</p><hr><a href='{video['url']}'>查看原视频</a>",
                "url": video['url']
            })
            print(f" ✅ 已生成文章: {video['title']}")
        except Exception as e:
            # 如果还是报错，打印出更详细的信息帮助调试
            print(f" ❌ Gemini 写作失败 ({video['title']}): {str(e)}")

    return articles
