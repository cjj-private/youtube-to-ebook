import requests
import streamlit as st
import json

def write_articles_for_videos(videos_with_transcripts):
    api_key = st.secrets.get("GROQ_API_KEY")
    if not api_key:
        st.error("❌ 未发现 GROQ_API_KEY")
        return []

    articles = []
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    for video in videos_with_transcripts:
        print(f"🚀 正在为视频生成【长篇】深度报道: {video['title']}...")
        
        # 💡 修改了 Prompt，要求 1500 字左右，并增加章节感
        prompt = f"""
        你是一位深度内容拆解专家。请根据以下视频字幕写一篇深度分析长文。
        标题: {video['title']}
        字幕内容: {video['transcript']}
        
        要求：
        1. 篇幅要求：请写出一篇 1000-1500 字左右的深度报道。
        2. 结构要求：
           - 【引言】：结合当下 AI 趋势引入主题。
           - 【核心拆解】：分 3-4 个章节详细论述视频中的技术细节和逻辑。
           - 【行业影响】：分析该技术/观点对整个行业意味着什么。
           - 【深度总结】：给读者的实操建议或启发。
        3. 文风：专业、优雅、充满洞察力，类似《连线》(Wired) 或《三联生活周刊》的封面文章。
        """

        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "你是一位专业的科技专栏主编，擅长撰写长篇深度报道。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.6 # 稍微降低随机性，让逻辑更严密
        }

        try:
            response = requests.post(url, headers=headers, data=json.dumps(data))
            result = response.json()

            if "choices" in result:
                content_text = result['choices'][0]['message']['content']
                articles.append({
                    "title": video['title'],
                    "article": content_text,
                    "url": video['url'],
                    "channel": video.get('channel', 'YouTube Channel'),
                    "content": content_text
                })
                print(f" ✅ 长篇深度文章生成成功！")
            else:
                print(f" ❌ Groq 报错: {result.get('error', {}).get('message')}")
        except Exception as e:
            print(f" ❌ 请求异常: {e}")

    return articles
