import requests
import pandas as pd

# ---------------------- 核心配置 ----------------------
# 热歌榜接口（可替换其他榜单，id对应关系见下文）
API_URL = "https://music.163.com/api/playlist/detail?id=3778678"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Referer": "https://music.163.com/"
}

# ---------------------- 直接请求接口获取数据 ----------------------
def get_music_data():
    try:
        # 发送请求到接口（返回纯JSON，无需正则）
        response = requests.get(API_URL, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        # 直接提取歌曲列表（接口返回的路径更简单）
        song_list = data["result"]["tracks"]
        music_result = []
        
        # 解析歌曲名+歌手
        for song in song_list:
            song_name = song["name"].strip()
            # 拼接多个歌手
            artists = [art["name"] for art in song["artists"]]
            artist_str = " / ".join(artists)
            # 按你的格式拼接
            music_info = f"{song_name}|{artist_str}"
            music_result.append(music_info)
        
        return music_result
    
    except Exception as e:
        print(f"❌ 获取数据失败：{e}")
        return []

# ---------------------- 保存数据 ----------------------
def save_data(music_list):
    if not music_list:
        print("❌ 无数据可保存")
        return
    
    # 保存为TXT（song_name|artist格式，;分隔）
    with open("网易云热歌榜_接口版.txt", "w", encoding="utf-8") as f:
        f.write(";".join(music_list))
    
    # 保存为Excel（可选，方便查看）
    df = pd.DataFrame({"歌曲信息": music_list})
    df.to_excel("网易云热歌榜_接口版.xlsx", index=False)
    
    print(f"✅ 成功爬取 {len(music_list)} 首歌曲！")
    print("✅ TXT文件：网易云热歌榜_接口版.txt")
    print("✅ Excel文件：网易云热歌榜_接口版.xlsx")
    print("📌 前5首示例：", ";".join(music_list[:5]))

# ---------------------- 主函数 ----------------------
if __name__ == "__main__":
    print("🔍 开始爬取网易云音乐热歌榜（接口版）...")
    music_data = get_music_data()
    save_data(music_data)
