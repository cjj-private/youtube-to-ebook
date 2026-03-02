"""
YouTube Newsletter Generator - Main Script
Ties together all the pieces: fetch videos → get transcripts → write articles → send Telegram
Tracks processed videos to avoid sending duplicates.
"""

from get_videos import main as fetch_videos
from get_transcripts import get_transcripts_for_videos
from write_articles import write_articles_for_videos
from send_email import send_newsletter  # 这里虽然叫 send_newsletter，但内部逻辑已改为 TG
from video_tracker import filter_new_videos, mark_videos_processed, get_processed_count

def run():
    """
    运行完整的自动化工作流。
    """
    print("=" * 60)
    print("  HELLOSG.ORG - 自动简报生成器 (Telegram 版)")
    print("=" * 60)
    print(f"  📊 历史已处理视频数量: {get_processed_count()}")

    # --- STEP 1: 抓取视频 ---
    print("\n📺 STEP 1: 正在从 YouTube 抓取最新视频...")
    videos = fetch_videos()

    if not videos:
        print("❌ 未找到视频，请检查频道列表。")
        return

    # --- STEP 1b: 过滤重复 ---
    print("\n🔍 正在检查是否有新内容...")
    new_videos = filter_new_videos(videos)

    if not new_videos:
        print("✅ 暂时没有新视频。所有内容已在之前的推送中处理。")
        print("=" * 60)
        return

    print(f"\n  → 发现 {len(new_videos)} 个新视频需要处理\n")

    # --- STEP 2: 提取字幕 ---
    print("\n📝 STEP 2: 正在提取视频字幕 (Supadata)...")
    videos_with_transcripts = get_transcripts_for_videos(new_videos)

    if not videos_with_transcripts:
        print("❌ 无法获取字幕，流程停止。")
        return

    # --- STEP 3: AI 写稿 ---
    print("\n✍️ STEP 3: 正在使用 Groq (Llama 3) 编写深度分析文章...")
    articles = write_articles_for_videos(videos_with_transcripts)

    if not articles:
        print("❌ 文章生成失败。")
        return

    # --- STEP 4: 推送到 Telegram ---
    print("\n📱 STEP 4: 正在向 Telegram 推送简报...")
    success = send_newsletter(articles)

    # --- STEP 5: 标记已处理 ---
    if success:
        mark_videos_processed(videos_with_transcripts)
        print(f"\n  ✓ 成功！已标记 {len(videos_with_transcripts)} 个视频为“已发送”。")
    else:
        print("\n  ⚠️ 推送部分失败，请检查 Telegram 配置。")

    print("\n" + "=" * 60)
    print("  任务全部完成！")
    print("=" * 60)

    return articles

if __name__ == "__main__":
    run()
