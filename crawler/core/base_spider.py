import requests
import random
import time


class BaseSpider:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Sentinel/2026",
            "Accept-Language": "zh-CN,zh;q=0.9",
        }

    def fetch(self, url, method="GET", data=None):
        """带有自动重试机制的请求封装"""
        for _ in range(3):
            try:
                response = requests.request(
                    method, url, headers=self.headers, data=data, timeout=15
                )
                if response.status_code == 200:
                    return response
                time.sleep(random.uniform(1, 3))
            except Exception as e:
                print(f"⚠️ 网络异常: {e}")
        return None
