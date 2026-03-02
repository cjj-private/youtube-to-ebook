import requests
import streamlit as st
import json

def write_articles_for_videos(videos_with_transcripts):
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        st.error("❌ 未在 Secrets 中发现 GEMINI_API_KEY")
        return []

    articles = []
    # 使用 v1beta 是因为它的兼容性最广，适合新项目
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}

    for video in videos_with_transcripts:
        print(f"🚀 正在通过新项目 Key 尝试写作: {video['title']}...")
        
        prompt = f"你是一位新加坡政策评论员。请根据以下字幕写一篇深度报道：\n标题：{video['title']}\n字幕：{video['transcript']}"
        data = {"contents": [{"parts": [{"text": prompt}]}]}

        try:
            response = requests.post(url, headers=headers, data=json.dumps(data))
            result = response.json()

            if "candidates" in result:
                content_text = result['candidates'][0]['content']['parts'][0]['text']
                articles.append({
                    "title": video['title'],
                    "content": content_text,
                    "html": f"<h2>{video['title']}</h2><p>{content_text.replace('\n', '<br>')}</p>",
                    "url": video['url']
                })
                print(f" ✅ 【大功告成】哈啰人力文章生成成功！")
            else:
                # 这里的报错信息至关重要
                error_msg = result.get('error', {}).get('message', '未知错误')
                print(f" ❌ API 拒绝详情: {error_msg}")
                st.error(f"Gemini 报错: {error_msg}")
        except Exception as e:
            print(f" ❌ 请求异常: {e}")

    return articles
