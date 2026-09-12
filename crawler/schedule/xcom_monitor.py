from __future__ import annotations

import os

import requests
from dotenv import load_dotenv

load_dotenv()


BEARER_TOKEN = os.getenv("x_bearer_token")

if not BEARER_TOKEN:
    raise RuntimeError("❌ 未找到 X_BEARER_TOKEN")


url = "https://api.x.com/2/tweets/search/recent"

headers = {
    "Authorization": f"Bearer {BEARER_TOKEN}",
}

params = {
    "query": "NVDA lang:en -is:retweet",
    "max_results": 10,
    "tweet.fields": "created_at,public_metrics,lang,author_id",
}


print()
print("=" * 60)
print("X API 测试")
print("=" * 60)
print("正在请求 X API...")
print()


response = requests.get(
    url,
    headers=headers,
    params=params,
    timeout=30,
)


print("HTTP 状态码:", response.status_code)


if response.status_code != 200:
    print("❌ API 请求失败")
    print(response.text)
    raise SystemExit(1)


data = response.json()

tweets = data.get("data", [])

print(f"✅ 获取到 {len(tweets)} 条帖子")
print()


for i, tweet in enumerate(tweets, 1):
    print(f"--- 第 {i} 条 ---")
    print("ID:", tweet.get("id"))
    print("时间:", tweet.get("created_at"))
    print("作者:", tweet.get("author_id"))
    print("内容:", tweet.get("text"))
    print("指标:", tweet.get("public_metrics"))
    print()