import requests
import streamlit as st
import json
import time  # 用于控制免费版 API 的请求频率

def write_articles_for_videos(videos_with_transcripts):
    """
    使用 Groq API (Llama 3.3 70B) 将视频字幕转化为深度长篇专题。
    修复了变量定义域错误及频率控制逻辑。
    """
    # 1. 获取 API Key
    api_key = st.secrets.get("GROQ_API_KEY")
    if not api_key:
        print("❌ 错误: 未在 Streamlit Secrets 中发现 GROQ_API_KEY")
        return []

    articles = []
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    for video in videos_with_transcripts:
        video_title = video.get('title', '未命名视频')
        print(f"\n🚀 正在为视频生成【长篇】深度报道: {video_title}...")
        
        # --- 2. 频率控制 (针对 Groq 免费额度) ---
        # 如果不是处理第一个视频，强制休息 30 秒以防止 Rate Limit 报错
        if len(articles) > 0:
            print("⏳ 正在等待额度刷新 (30秒)...")
            time.sleep(30)
        
        # --- 3. 获取字幕内容 ---
        # 确保从上级传来的字典中有 'transcript' 字段
        transcript_content = video.get('transcript', '')
        if not transcript_content:
            print(f" ⚠️ 视频 '{video_title}' 字幕内容为空，跳过 AI 生成。")
            continue

        # --- 4. 构造高保真 Prompt (纯净版，无品牌植入) ---
        prompt = f"""
你是一位极其严谨的内容架构师，擅长将复杂的长视频转化为逻辑清晰、富有洞见的长篇文章。
视频标题: {video_title}
字幕原文: {transcript_content}

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

篇幅要求：1000-1500 字左右。
"""

        # --- 5. 请求数据构造 ---
        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {
                    "role": "system", 
                    "content": "你是一位专业的科技与社会评论主编，擅长将复杂的视频内容转化为极具阅读价值的深度长篇文章。"
                },
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.5, # 较低的随机性有助于保持长文逻辑严密
            "max_tokens": 4096  # 确保有足够的长度生成 1500 字
        }

        # --- 6. 发起 API 请求 ---
        try:
            # 增加 timeout 到 180 秒，因为 Llama 3.3 70B 生成长文较慢
            response = requests.post(url, headers=headers, data=json.dumps(data), timeout=180)
            result = response.json()

            if "choices" in result:
                content_text = result['choices'][0]['message']['content']
                
                # 打包数据，确保与 send_email.py 或 Telegram 推送模块兼容
                articles.append({
                    "title": video_title,
                    "article": content_text,
                    "url": video.get('url', ''),
                    "channel": video.get('channel', 'YouTube Channel'),
                    "content": content_text
                })
                print(f" ✅ 长篇深度文章生成成功！({len(content_text)} 字)")
            else:
                error_msg = result.get('error', {}).get('message', '未知 API 错误')
                print(f" ❌ Groq 报错: {error_msg}")
                
        except Exception as e:
            print(f" ❌ 请求异常: {e}")

    return articles
