import asyncio
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List
import feedparser
from yt_dlp import YoutubeDL


class YouTubeRecentFetcher:
    """按时间窗口单次抓取 YouTube 最近视频的工具类"""

    def __init__(self, target_channels: Dict[str, str], days_back: int = 7):
        """
        :param target_channels: 目标频道字典 {频道名称: Channel_ID}
        :param days_back: 抓取过去多少天内发布的视频 (默认 7 天)
        """
        self.target_channels = target_channels
        self.days_back = days_back
        self.rss_base_url = "https://www.youtube.com/feeds/videos.xml?channel_id="

    async def fetch_channel_recent_videos(self, channel_name: str, channel_id: str) -> List[Dict[str, Any]]:
        """拉取单频道过去 N 天的视频列表"""
        rss_url = f"{self.rss_base_url}{channel_id}"
        loop = asyncio.get_running_loop()
        feed = await loop.run_in_executor(None, feedparser.parse, rss_url)

        cutoff_time = datetime.now(timezone.utc) - timedelta(days=self.days_back)
        recent_videos = []

        for entry in feed.entries:
            # 解析 RSS 中的时间
            published_parsed = entry.get("published_parsed")
            if published_parsed:
                pub_dt = datetime(*published_parsed[:6], tzinfo=timezone.utc)
            else:
                pub_dt = datetime.now(timezone.utc)

            # 时间过滤：只留过去 N 天以内的视频
            if pub_dt >= cutoff_time:
                recent_videos.append({
                    "channel_name": channel_name,
                    "video_id": entry.yt_videoid,
                    "title": entry.title,
                    "link": entry.link,
                    "published": entry.published,
                    "published_dt": pub_dt,
                })

        return recent_videos

    async def extract_video_details(self, video_url: str) -> Dict[str, Any]:
        """使用 yt-dlp 提取详细元数据（如时长、简介等）"""
        ydl_opts = {
            "skip_download": True,
            "quiet": True,
            "no_warnings": True,
        }

        def _extract():
            with YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(video_url, download=False)

        loop = asyncio.get_running_loop()
        try:
            info = await loop.run_in_executor(None, _extract)
            return {
                "description": info.get("description", "").strip(),
                "duration_min": round(info.get("duration", 0) / 60, 2),
                "view_count": info.get("view_count", 0),
            }
        except Exception as e:
            print(f"[!] 提取元数据失败 ({video_url}): {e}")
            return {}

    async def run(self) -> List[Dict[str, Any]]:
        """执行单次任务，收集并返回全部视频数据"""
        print(f"[*] 开始抓取过去 {self.days_back} 天内的视频...")
        all_results = []

        for name, cid in self.target_channels.items():
            print(f"[*] 正在检索频道: [{name}]...")
            videos = await self.fetch_channel_recent_videos(name, cid)

            if not videos:
                print(f"    - 过去 {self.days_back} 天无新发布视频。")
                continue

            for item in videos:
                print(f"    [🚀 抓取到] {item['title']} (发布于: {item['published']})")
                
                # 提取补充元数据
                details = await self.extract_video_details(item["link"])
                full_item = {**item, **details}
                all_results.append(full_item)

        print(f"\n[+] 抓取完成！共获得 {len(all_results)} 条符合条件的视频数据。")
        return all_results

if __name__ == "__main__":
    # 监控频道配置 (名称: Channel ID)
    TARGET_CHANNELS = {
        "NVIDIA": "UC_x5XG1OV2P6uZZ5FSM9Ttw",
        "Google": "UCK8sQmJBp8GCxrOtXWBpyEA",
        "Google Cloud Tech": "UCJS9pqu9BzkAMNTmA_kEog",
        "OpenAI": "UCXZCJLdBC09xxGZ6gcdrc6A",
        "Lex Fridman": "UCSHZKyawb77ixDdsGog4iWA",
    }

    # 实例化抓取器：获取过去 3 天内发布的所有视频
    fetcher = YouTubeRecentFetcher(target_channels=TARGET_CHANNELS, days_back=3)

    # 运行抓取，运行完后即刻退出
    results = asyncio.run(fetcher.run())

    # =========================================================
    # 拿到 results 后的处理逻辑 (比如存 JSON、传给 LLM 摘要等)
    # =========================================================
    for video in results:
        print(f"\n- [{video['channel_name']}] {video['title']}")
        print(f"  时长: {video.get('duration_min')} 分钟")
        print(f"  链接: {video['link']}")