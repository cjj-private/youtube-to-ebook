import requests
import streamlit as st
import json
import time  # 导入时间模块用于控制请求频率

def write_articles_for_videos(videos_with_transcripts):
    """
    使用 Groq API 将视频字幕转化为深度长篇报道。
    加入了 time.sleep 以避免免费额度的 Rate Limit 报错。
    """
    api_key = st.secrets.get("GROQ_API_KEY")
    if not api_key:
        st.error("❌ 未在 Streamlit Secrets 中发现 GROQ_API_KEY")
        return []

    articles = []
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    for video in videos_with_transcripts:
        print(f"🚀 正在为视频生成【长篇】深度报道: {video['title']}...")
        
        # --- 关键修复：请求频率控制 ---
        # 免费版 Groq 对每分钟的 Token 数量有限制，在此强制休息 10 秒
        if len(articles) > 0:
            print("⏳ 正在等待额度刷新 (10秒)...")
            time.sleep(30)
        
        # 构造高质量深度长文的 Prompt
        prompt = f"""
        你是一位深度内容拆解专家。请根据以下视频字幕写一篇深度分析长文。
        标题: {video['title']}
        字幕内容: {video['transcript']}
        
        要求：
        1. 篇幅要求：请写出一篇 1000-1500 字左右的深度报道。
        2. 结构要求：
           - 【引言】：结合行业背景或当下 AI 趋势引入主题，吸引读者。
           - 【核心内容拆解】：分 3-4 个章节详细论述视频中的关键技术细节、逻辑或故事。
           - 【行业/社会影响】：分析这些观点对相关行业或普通人意味着什么。
           - 【主编点评】：以“哈啰人力 (hellosg.org)”的视角提供实操建议或深度启发。
        3. 文风：专业、优雅、有洞察力，类似《连线》(Wired) 或《三联生活周刊》的封面文章风格。
        """

        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {
                    "role": "system", 
                    "content": "你是一位专业的科技与社会评论主编，擅长将复杂的视频内容转化为极具阅读价值的深度长篇文章。"
                },
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.6  # 稍微调低随机性，保证长文的逻辑连贯
        }

        try:
            response = requests.post(url, headers=headers, data=json.dumps(data), timeout=120)
            result = response.json()

            if "choices" in result:
                content_text = result['choices'][0]['message']['content']
                
                # 打包所有必要字段返回给 send_email.py (Telegram)
                articles.append({
                    "title": video['title'],
                    "article": content_text,
                    "url": video['url'],
                    "channel": video.get('channel', 'YouTube Channel'),
                    "content": content_text  # 冗余字段确保兼容性
                })
                print(f" ✅ 长篇深度文章生成成功！({len(content_text)} 字)")
            else:
                error_msg = result.get('error', {}).get('message', '未知 API 错误')
                print(f" ❌ Groq 报错: {error_msg}")
                st.warning(f"由于 API 限制，视频 '{video['title']}' 生成失败。")
                
        except Exception as e:
            print(f" ❌ 请求异常: {e}")

    return articles
