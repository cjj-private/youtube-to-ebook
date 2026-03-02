"""
YouTube Newsletter Dashboard - Optimized for Streamlit Cloud
Project: hellosg.org (哈啰人力)
"""

import streamlit as st
import os
import sys
import json
import subprocess
import re
from datetime import datetime
from pathlib import Path

# --- 强制环境检查 (解决 ModuleNotFoundError) ---
try:
    import requests
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "requests"])

# Paths
PROJECT_DIR = Path(__file__).parent
CHANNELS_FILE = PROJECT_DIR / "get_videos.py"
PROMPT_FILE = PROJECT_DIR / "write_articles.py"
TRACKER_FILE = PROJECT_DIR / "processed_videos.json"
NEWSLETTERS_DIR = PROJECT_DIR / "newsletters"

# Ensure directory exists
NEWSLETTERS_DIR.mkdir(exist_ok=True)

st.set_page_config(
    page_title="The Digest | hellosg",
    page_icon="📰",
    layout="wide"
)

# --- 中文版杂志主笔 Prompt 模板 ---
CHINESE_PROMPT = """你是一位顶尖的杂志主笔。请将下方的 YouTube 视频字幕转换成一篇文笔优美、引人入胜的深度报道。

视频标题: {video['title']}
频道名称: {video['channel']}
视频链接: {video['url']}

视频描述:
{video['description']}

视频字幕:
{video['transcript']}

---

请根据以上素材重新创作一篇杂志长文。要求如下：
1. **修正错误**：利用视频描述修正人名、政策术语（如 MOM, EP, COMPASS）的错误。
2. **抓人标题**：拟定一个富有吸引力的中文标题（非原视频标题）。
3. **文采与可读性**：文笔参考《三联生活周刊》，通俗易懂地解释专业移民政策。
4. **独立成篇**：严禁出现“在本视频中”等字眼，文章应作为独立的深度阅读。
5. **语言要求**：全文使用简体中文。

请使用 Markdown 格式输出。"""

# ============================================
# CUSTOM CSS (保留你喜欢的黑金杂志风格)
# ============================================
st.markdown("""
<style>
    :root {
        --accent-gold: #d4a855;
        --bg-primary: #0d0d0d;
    }
    .stApp { background: var(--bg-primary); color: #e8e4dd; }
    h1 { font-family: 'serif'; color: var(--accent-gold) !important; text-align: center; }
    .stButton>button { border-radius: 8px; border: 1px solid var(--accent-gold); }
</style>
""", unsafe_allow_html=True)

# ============================================
# HELPER FUNCTIONS
# ============================================

def get_channels():
    if not CHANNELS_FILE.exists(): return []
    with open(CHANNELS_FILE) as f:
        content = f.read()
    match = re.search(r'CHANNELS\s*=\s*\[(.*?)\]', content, re.DOTALL)
    return re.findall(r'["\'](@[\w]+)["\']', match.group(1)) if match else []

def save_channels(channels):
    with open(CHANNELS_FILE) as f:
        content = f.read()
    channels_str = "CHANNELS = [\n" + ",\n".join([f'    "{ch}"' for ch in channels]) + "\n]"
    new_content = re.sub(r'CHANNELS\s*=\s*\[.*?\]', channels_str, content, flags=re.DOTALL)
    with open(CHANNELS_FILE, "w") as f: f.write(new_content)

# ============================================
# MAIN UI
# ============================================

st.sidebar.title("THE DIGEST")
page = st.sidebar.radio("导航", ["生成简报", "频道管理", "写作风格", "档案库"])

if page == "生成简报":
    st.markdown("<h1>THE DIGEST</h1>", unsafe_allow_html=True)
    st.caption("为哈啰人力定制：将 YouTube 视频转化为深度政策简报")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 开始抓取并生成文章", type="primary", use_container_width=True):
            with st.spinner("正在解析视频并调用 AI 写作..."):
                try:
                    # 【关键修复】：使用 sys.executable 确保环境一致
                    result = subprocess.run(
                        [sys.executable, str(PROJECT_DIR / "main.py")],
                        capture_output=True, text=True, cwd=str(PROJECT_DIR), timeout=600
                    )
                    if result.returncode == 0:
                        st.success("生成成功！请查看 Archive 页面下载 EPUB。")
                    else:
                        st.error("执行出错")
                    with st.expander("查看运行日志"):
                        st.code(result.stdout + result.stderr)
                except Exception as e:
                    st.error(f"运行失败: {e}")

elif page == "频道管理":
    st.header("订阅频道")
    current_channels = get_channels()
    new_ch = st.text_input("添加 YouTube 频道 (如 @MOMSingapore)")
    if st.button("添加"):
        if new_ch and new_ch not in current_channels:
            current_channels.append(new_ch if new_ch.startswith("@") else "@"+new_ch)
            save_channels(current_channels)
            st.rerun()
    st.write("当前订阅：", current_channels)

elif page == "写作风格":
    st.header("AI 写作指令")
    st.info("当前已配置为：中文杂志主笔风格")
    st.text_area("Prompt 内容", value=CHINESE_PROMPT, height=400)
    if st.button("应用中文模板"):
        # 这里逻辑可以根据需要写入 write_articles.py
        st.success("配置已更新（预览）")

elif page == "档案库":
    st.header("已生成的简报")
    if TRACKER_FILE.exists():
        with open(TRACKER_FILE) as f:
            data = json.load(f)
        st.write(f"共处理视频：{len(data.get('videos', {}))} 个")
        for vid, info in data.get('videos', {}).items():
            st.text(f"✅ {info.get('title')}")
    else:
        st.info("尚无处理记录。")
