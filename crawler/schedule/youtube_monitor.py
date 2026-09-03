import time
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# ==================== 配置区域 ====================
# 1. 填入您免费申请的 Google API Key
API_KEY = "YOUR_YOUTUBE_API_KEY"

# 2. 填入你想监控的名人频道 ID（支持同时监控多个）
# 频道 ID 获取方法：打开名人 YouTube 主页，URL 后面或者简介里通常有一串以 UC 开头的 24 位代码
MONITOR_CHANNELS = {
    "SpaceX官方": "UC_Mhev9499pIdV_Y99S8fVA",
    "Google开发者": "UC_x5XG1OV2P6uZZ5FSM9Ttw"
}

# 3. 轮询检测间隔（单位：秒）。建议 300 秒（5分钟）或 600 秒（10分钟）
# 这样每天消耗的配额极低，完全在免费额度（10,000点）以内
CHECK_INTERVAL = 300 
# ==================================================

def init_youtube_client(api_key):
    """初始化 Google 官方客户端"""
    return build('youtube', 'v3', developerKey=api_key)

def get_latest_video(youtube, channel_id):
    """获取指定频道最新发布的一条视频"""
    try:
        # 每次调用只消耗 1 个配额点数
        request = youtube.activities().list(
            part="snippet,contentDetails",
            channelId=channel_id,
            maxResults=1
        )
        response = request.execute()
        
        if response.get("items"):
            item = response["items"][0]
            # 确保活动类型是“上传视频”
            if item["snippet"]["type"] == "upload":
                video_id = item["contentDetails"]["upload"]["videoId"]
                title = item["snippet"]["title"]
                return {"id": video_id, "title": title}
    except HttpError as e:
        print(f"❌ 谷歌 API 请求失败: {e}")
    except Exception as e:
        print(f"❌ 发生未知错误: {e}")
    return None

def start_monitor():
    youtube = init_youtube_client(API_KEY)
    print("🚀 YouTube 名人动态监控系统已启动...")
    print(f"当前正在监控 {len(MONITOR_CHANNELS)} 个频道，每 {CHECK_INTERVAL} 秒检测一次...\n" + "="*50)
    
    # 用于记录每个频道已知的最新视频 ID，防止首次启动或重复时误报
    history_latest_videos = {}
    
    # 首次启动：先初始化记录当前的最新视频状态
    for name, channel_id in MONITOR_CHANNELS.items():
        video = get_latest_video(youtube, channel_id)
        if video:
            history_latest_videos[channel_id] = video["id"]
            print(f"【初始化成功】[{name}] 当前最新视频: {video['title']}")
    
    print("\n" + "="*50 + "\n进入实时监控状态，等待新视频发布...")
    
    # 开始死循环定时监控
    while True:
        time.sleep(CHECK_INTERVAL)
        
        for name, channel_id in MONITOR_CHANNELS.items():
            current_video = get_latest_video(youtube, channel_id)
            
            if not current_video:
                continue
                
            last_known_id = history_latest_videos.get(channel_id)
            
            # 如果检测到的视频 ID 和历史记录不一致，说明发布了新视频！
            if current_video["id"] != last_known_id:
                print(f"\n🔥 【新动态提醒】名人 [{name}] 刚刚发布了新视频！")
                print(f"📺 视频标题: {current_video['title']}")
                print(f"🔗 视频链接: https://youtube.com{current_video['id']}")
                print("-" * 50)
                
                # 更新历史记录，防止重复报警
                history_latest_videos[channel_id] = current_video["id"]

if __name__ == "__main__":
    start_monitor()
