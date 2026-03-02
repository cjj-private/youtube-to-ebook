"""
Part 1: Fetch Latest Videos from YouTube Channels
POWERED BY SUPADATA (Fixed 400 Error)
Optimized for hellosg.org (哈啰人力)
"""

import os
import requests
import streamlit as st
from dotenv import load_dotenv

# 加载本地环境
load_dotenv()

def get_supadata_key():
    if "SUPADATA_API_KEY" in st.secrets:
        return st.secrets["SUPADATA_API_KEY"]
    return os.getenv("SUPADATA_API_KEY")

SUPADATA_API_KEY = get_supadata_key()

# ========================================
# 订阅频道列表
# ========================================
CHANNELS = [
    "@MOMSingapore",     # 新加坡人力部
    "@CNA",              # 亚洲新闻台
    "@TheStraitsTimes",  # 海峡时报
    "@LatentSpacePod",
]

def get_latest_video_via_supadata(channel_handle):
    """
    通过 Supadata API 获取频道视频。
    修复 400 错误：先搜索频道获取正确的 ID 或数据。
    """
    clean_handle = channel_handle.lstrip("@")
    headers = {"x-api-key": SUPADATA_API_KEY}
    
    # 策略：使用 Supadata 的 YouTube 视频抓取接口
    # 尝试直接使用正确的参数名：channelHandle (注意大小写和API文档一致性)
    url = "https://api.supadata.ai/v1/youtube/channel/videos"
    params = {"channelHandle": clean_handle}

    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)
        
        # 如果还是 400，尝试使用通用搜索接口
        if response.status_code != 200:
            search_url = "https://api.supadata.ai/v1/youtube/search"
            search_params = {"query": channel_handle, "limit": 2, "type": "video"}
            response = requests.get(search_url, params=search_params, headers=headers, timeout=15)

        if response.status_code == 200:
            data = response.json()
            # 兼容不同返回格式
            videos = data.get("videos", data if isinstance(data, list) else [])
            
            if videos:
                # 寻找第一个非 Shorts 的视频 (Supadata 返回通常按时间排序)
                for v in videos:
                    v_id = v.get("videoId")
                    if not v_id: continue
                    
                    return {
                        "title": v.get("title"),
                        "video_id": v_id,
                        "description": v.get("description", ""),
                        "channel": channel_handle,
                        "url": f"https://www.youtube.com/watch?v={v_id}"
                    }
        else:
            print(f"  ✗ API Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    return None

def main():
    if not SUPADATA_API_KEY:
        print("❌ ERROR: SUPADATA_API_KEY missing!")
        return []

    print("📺 STEP 1: Fetching videos for hellosg.org...\n")
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
            print(f"  ✗ Could not find videos for {channel_handle}\n")

    print("=" * 60)
    print(f"Found {len(videos)} videos total!")
    return videos

if __name__ == "__main__":
    main()
