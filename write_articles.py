import requests
import streamlit as st
import json
import time

def write_articles_for_videos(videos_with_transcripts):
    """
    高保真版：使用 Groq API (Llama 3.3 70B) 深度还原视频逻辑与语感。
    """
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
        print(f"\n🚀 正在为视频生成【高保真】深度拆解: {video_title}...")
        
        if len(articles) > 0:
            print("⏳ 正在等待额度刷新 (30秒)...")
            time.sleep(30)
        
        transcript_content = video.get('transcript', '')
        if not transcript_content:
            continue

        # --- 【高保真版 Prompt 修改点】 ---
        prompt = f"""
你是一位顶尖的思想拆解专家，擅长以原作者的口吻还原其最深层的思维模型。
视频标题: {video_title}
字幕原文: {transcript_content}

### 核心任务：
请将字幕内容整理成一篇深度系统化长文。
**注意：这不是总结，这是还原。** 我需要你像原作者在写书一样，把他的逻辑链条严丝合缝地接起来。

### 结构与文风硬性要求：
1. **【第一人称叙述】**：禁止使用“作者说”、“视频提到”。直接用“你”、“我们”、“我”来叙述，保持导师授课般的现场感。
2. **【底层逻辑还原】**：
   - 必须保留并深入解释视频中的核心“黑话”（如：1D-5D Thinking, NPC scripts, Synthesis, Meta-narrative等）。
   - 不要跳过推导过程。如果作者从一个痛苦点推导到哲学高度，请写出那个转变的瞬间。
3. **【金句嵌入】**：在每个章节中，必须至少引用 2 句字幕中的高能量原句，并用引号标注。
4. **【行动指南】**：拒绝“保持心态”之类的废话。必须还原视频中具体的、甚至是奇怪的实操建议（例如：通过某种特定的写作方式或日常习惯）。

### 负面约束 (禁止事项)：
- 绝对禁止使用：首先、其次、最后、综上所述、综上所述、在当今社会、哈啰人力。
- 严禁脑补：如果视频里没提到的逻辑，禁止为了文章通顺而自己发明。

篇幅：1300-1500 字。
"""

        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {
                    "role": "system", 
                    "content": "你是一位专注于个人发展哲学与系统思维的内容主编。你的文字风格犀利、深邃、富有启发性，拒绝任何平庸的AI总结感。"
                },
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,  # 提高到 0.7 增加文字的感染力和灵活性
            "top_p": 0.9,       # 让选词更有深度
            "max_tokens": 4096
        }

        try:
            response = requests.post(url, headers=headers, data=json.dumps(data), timeout=180)
            result = response.json()

            if "choices" in result:
                content_text = result['choices'][0]['message']['content']
                articles.append({
                    "title": video_title,
                    "article": content_text,
                    "url": video.get('url', ''),
                    "channel": video.get('channel', 'YouTube Channel'),
                    "content": content_text
                })
                print(f" ✅ 高保真长文生成成功！({len(content_text)} 字)")
            else:
                print(f" ❌ Groq 报错: {result.get('error', {}).get('message', '未知错误')}")
                
        except Exception as e:
            print(f" ❌ 请求异常: {e}")

    return articles
