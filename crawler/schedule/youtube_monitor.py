import os
import requests

from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("youtube_api_key")
PROXY = "http://127.0.0.1:7890"

url = "https://www.googleapis.com/youtube/v3/channels"

params = {
    "part": "snippet",
    "id": "UCK8sQmJBp8GCxrOtXWBpyEA",
    "key": API_KEY,
}

proxies = {
    "http": PROXY,
    "https": PROXY,
}

try:
    response = requests.get(
        url,
        params=params,
        proxies=proxies,
        timeout=15,
    )

    print("状态码:", response.status_code)
    print("返回内容:", response.text)

except Exception as e:
    print("❌ 请求失败:", e)