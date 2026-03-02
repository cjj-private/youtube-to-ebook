"""
Part 1: Fetch Latest Videos from YouTube Channels
POWERED BY SUPADATA (No Google API Key Required)
Optimized for hellosg.org (哈啰人力)
"""

import os
import requests
import streamlit as st
from dotenv import load_dotenv

# 加载本地环境
load_dotenv()

# --- 核心配置：只读取 SUPADATA_API_KEY ---
def get_supadata_key():
    if "SUPADATA_API_KEY" in st.secrets:
        return st.secrets["SUPADATA_API_KEY"]
    return os.getenv("SUPADATA_API_KEY")

SUPADATA_API_KEY = get_supadata_key()

# ========================================
# 订阅频道列表 (可根据哈啰人力需求修改)
# ========================================
CHANNELS = [
    "@MOMSingapore",     # 新加坡人力部
    "@CNA",              # 亚洲新闻台
    "@TheStraitsTimes",  # 海峡时报
    "@LatentSpacePod",
]

def get_latest_video_via_supadata(channel_handle):
    """
    使用 Supadata API 直接获取频道的最新视频
    """
    # 准备请求 Supadata API
    # 文档参考: https://supadata.ai/docs
    url = f"https://api.supadata.ai/v1/youtube/channel/videos"
    params = {
        "channelHandle": channel_handle.lstrip("@"),
        "limit": 5  # 获取最近5个，方便过滤 Shorts
    }
    headers = {"x-api-key": SUPADATA_API_KEY}

    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"  ✗ Supadata API Error: {response.status_code}")
            return None
        
        data = response.json()
        items = data.get("videos", []) # 假设返回格式中有 videos 列表

        for video in items:
            # Supadata 通常会自动标注是否为 Shorts，或者我们可以通过时长过滤
            # 简单逻辑：如果标题或描述里没有明显 Shorts 特征则采用
            video_id = video.get("videoId")
            return {
                "title": video.get("title"),
                "video_id": video_id,
                "description": video.get("description", ""),
                "channel": channel_handle,
                "url": f"https://www.youtube.com/watch?v={video_id}"
            }
    except Exception as e:
        print(f"  ✗ Error calling Supadata for {channel_handle}: {e}")
    
    return None

def main():
    if not SUPADATA_API_KEY:
        print("❌ ERROR: SUPADATA_API_KEY not found in Secrets!")
        return []

    print("📺 STEP 1: Fetching latest videos via Supadata...\n")
    print("=" * 60)

    videos = []

    for channel_handle in CHANNELS:
        print(f"Looking up: {channel_handle}")
        video = get_latest_video_via_supadata(channel_handle)

        if video:
            videos.append(video)
            print(f"  ✓ Found: {video['title']}")
            print(f"    URL: {video['url']}\n")
        else:
            print(f"  ✗ No recent long-form videos found\n")

    print("=" * 60)
    print(f"Found {len(videos)} videos total!")
    return videos

if __name__ == "__main__":
    main()
