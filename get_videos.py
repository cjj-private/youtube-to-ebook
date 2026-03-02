import os
import requests
from googleapiclient.discovery import build
import streamlit as st

# 从 Streamlit Secrets 获取 API Key
YOUTUBE_API_KEY = st.secrets.get("YOUTUBE_API_KEY")

# ========================================
# 恢复项目原本的频道列表 (硅谷 AI/Tech 频道)
# ========================================
CHANNELS = [
    # "@LatentSpacePod",
    "@ycombinator",
    "@DanKoeTalks",
    #"@a16z",
    #"@RedpointAI",
    #"@EveryInc",
    #"@DataDrivenNYC",
    #"@NoPriorsPodcast",
    #"@DwarkeshPatel",
]

def get_channel_info(youtube, channel_handle):
    """
    通过 handle 寻找频道信息。
    为了避免 404，我们改用 list(forHandle=...)。
    """
    handle = channel_handle.lstrip("@")
    try:
        request = youtube.channels().list(
            part="snippet,contentDetails",
            forHandle=handle
        )
        response = request.execute()

        if response.get("items"):
            channel = response["items"][0]
            return {
                "channel_id": channel["id"],
                "channel_name": channel["snippet"]["title"],
                "uploads_playlist_id": channel["contentDetails"]["relatedPlaylists"]["uploads"]
            }
    except Exception as e:
        print(f"  ✗ 获取频道 {channel_handle} 失败: {e}")
    return None

def is_youtube_short(video_id):
    """
    检测是否为 Shorts 短视频。
    """
    shorts_url = f"https://www.youtube.com/shorts/{video_id}"
    try:
        response = requests.head(shorts_url, allow_redirects=True, timeout=5)
        return "/shorts/" in response.url
    except:
        return False

def get_latest_video(youtube, uploads_playlist_id, channel_name):
    """
    从上传列表中获取最新的长视频。
    """
    request = youtube.playlistItems().list(
        part="snippet",
        playlistId=uploads_playlist_id,
        maxResults=5 # 缩小范围，提高速度
    )
    response = request.execute()

    for item in response.get("items", []):
        video_id = item["snippet"]["resourceId"]["videoId"]
        if is_youtube_short(video_id):
            continue

        return {
            "title": item["snippet"]["title"],
            "video_id": video_id,
            "description": item["snippet"]["description"],
            "channel": channel_name,
            "url": f"https://www.youtube.com/watch?v={video_id}"
        }
    return None

def main():
    if not YOUTUBE_API_KEY:
        print("❌ 错误: 未找到 YOUTUBE_API_KEY")
        return []

    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    print(f"正在抓取原本的 {len(CHANNELS)} 个技术频道...\n")
    
    videos = []
    for channel_handle in CHANNELS:
        info = get_channel_info(youtube, channel_handle)
        if info:
            video = get_latest_video(youtube, info["uploads_playlist_id"], info["channel_name"])
            if video:
                videos.append(video)
                print(f"  ✅ 找到: {video['title']}")
        else:
            print(f"  ⚠️ 找不到频道: {channel_handle}")

    return videos

if __name__ == "__main__":
    main()
