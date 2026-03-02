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
        
            # 构造完全忠于原片、无额外植入的 Prompt
            prompt = f"""
            你是一位极其严谨的内容架构师，擅长将复杂的长视频转化为逻辑清晰、富有洞见的长篇文章。
            视频标题: {video_info['title']}
            字幕原文: {transcript}
            
            ### 核心任务：
            请将上述字幕内容整理成一篇深度拆解文章。你的唯一目标是：**在不改变作者原意的前提下，将其碎片化的表达系统化。**
            
            ### 结构要求：
            1. 【核心问题 (The Problem)】：精准还原作者在视频开头提出的核心痛点或认知偏差。
            2. 【底层逻辑 (The Framework)】：这是文章的主体。请分章节还原作者的推导过程。
               - 必须保留作者原创的概念、术语和比喻。
               - 尽可能引用原话作为金句或段落支撑。
               - 逻辑必须环环相扣，体现作者的思想深度。
            3. 【行动指南 (The System)】：将视频中提到的解决方法或实操建议，整理成具备逻辑关联的行动步骤。
            
            ### 文风约束：
            - **禁止脑补**：严禁引入字幕中未提及的行业趋势、背景信息或 AI 术语。
            - **去 AI 腔调**：禁止使用“总而言之”、“在这个时代”、“首先/其次/最后”等机械的连接词。
            - **保持质感**：文风应简洁、有力、专业。每一段的开头必须是一个有力的观点点睛，且该观点必须直接源自视频内容。
            
            篇幅：1000-1500 字左右（通过深度还原案例和推导逻辑来保证篇幅，而非填充废话）。
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
