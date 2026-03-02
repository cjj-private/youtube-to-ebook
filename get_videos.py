import os
import streamlit as st
from googleapiclient.discovery import build

# --- 核心安全修改：从云端保险箱读取 Key ---
def get_youtube_key():
    if "YOUTUBE_API_KEY" in st.secrets:
        return st.secrets["YOUTUBE_API_KEY"]
    return os.getenv("YOUTUBE_API_KEY")

YOUTUBE_API_KEY = get_youtube_key()

# 哈啰人力关注的频道 (你可以根据需要增加)
CHANNELS = ["@MOMSingapore", "@CNA", "@TheStraitsTimes"]

def get_channel_uploads_id(youtube, handle):
    handle = handle.lstrip("@")
    try:
        # 强制使用 API Key 模式，避免 TransportError
        request = youtube.channels().list(part="contentDetails", forHandle=handle)
        response = request.execute()
        if "items" in response:
            return response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    except Exception as e:
        st.error(f"无法获取频道 {handle} 信息: {e}")
    return None

def get_latest_video(youtube, playlist_id, channel_name):
    try:
        request = youtube.playlistItems().list(part="snippet", playlistId=playlist_id, maxResults=3)
        response = request.execute()
        for item in response.get("items", []):
            vid = item["snippet"]["resourceId"]["videoId"]
            # 这里简单返回第一个视频，你可以后续加入 Shorts 过滤逻辑
            return {
                "title": item["snippet"]["title"],
                "video_id": vid,
                "description": item["snippet"]["description"],
                "channel": channel_name,
                "url": f"https://www.youtube.com/watch?v={vid}"
            }
    except Exception as e:
        print(f"获取视频列表失败: {e}")
    return None

def main():
    if not YOUTUBE_API_KEY:
        st.warning("⚠️ 没找到 YOUTUBE_API_KEY，请检查 Secrets 设置")
        return []

    # 初始化 YouTube 客户端 (static_discovery=False 提高在 Streamlit 的兼容性)
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY, static_discovery=False)
    
    videos = []
    print("📺 正在抓取新加坡相关政策视频...")
    
    for handle in CHANNELS:
        uploads_id = get_channel_uploads_id(youtube, handle)
        if uploads_id:
            video = get_latest_video(youtube, uploads_id, handle)
            if video:
                videos.append(video)
                print(f" ✅ 找到: {video['title']}")
    
    return videos

if __name__ == "__main__":
    main()
