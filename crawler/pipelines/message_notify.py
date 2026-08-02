import os
import requests
from dotenv import load_dotenv
from datetime import datetime

# 加载 .env 环境变量文件
load_dotenv()


class WechatWebhookNotifier:
    """企业微信群机器人消息推送封装类"""

    BASE_URL = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send"

    def __init__(self, key: str = None):
        # 优先使用传入的 key，未传入则从环境变量中读取 WECHAT_WEBHOOK_KEY
        self.key = key or os.getenv("WECHAT_WEBHOOK_KEY")
        if not self.key:
            raise ValueError(
                "未找到企业微信 Webhook Key！请在 .env 中设置 WECHAT_WEBHOOK_KEY 或初始化时传入。"
            )

        self.url = f"{self.BASE_URL}?key={self.key}"

    def send_text(self, content: str) -> dict:
        """发送普通文本消息"""
        payload = {"msgtype": "text", "text": {"content": content}}
        return self._send(payload)

    def send_markdown(self, markdown_content: str) -> dict:
        """发送 Markdown 富文本消息（爬虫推送推荐，排版更美观）"""
        payload = {"msgtype": "markdown", "markdown": {"content": markdown_content}}
        return self._send(payload)

    def _send(self, payload: dict) -> dict:
        """内部方法：统一处理 POST 请求与异常捕获"""
        headers = {"Content-Type": "application/json"}
        try:
            # 设置 5 秒超时，防止网络卡顿影响爬虫主流程
            response = requests.post(self.url, json=payload, headers=headers, timeout=5)
            response.raise_for_status()
            res_json = response.json()

            if res_json.get("errcode") == 0:
                print("✅ [企微推送] 消息发送成功")
            else:
                print(f"❌ [企微推送] 发送失败，错误信息: {res_json}")

            return res_json
        except requests.exceptions.RequestException as e:
            print(f"⚠️ [企微推送] 网络请求异常: {e}")
            return {"errcode": -1, "errmsg": str(e)}


# -------------------------------------------------------------
# 爬虫 Pipeline 结合集成（以 Scrapy 或自定义管道为例）
# -------------------------------------------------------------
class WechatNotificationPipeline:
    """爬虫 Pipeline 管道类，可在数据处理完成或满足条件时触发推送"""

    def __init__(self):
        self.notifier = WechatWebhookNotifier()

    def process_item(self, item, spider=None):
        """
        处理爬虫抓取的每一个 Item（根据需要触发推送）
        """
        # 示例：假设只推送抓取的标题和价格
        title = item.get("title", "未命名")
        price = item.get("price", "未知")

        # 组合成美观的 Markdown 消息
        message = (
            f"### 🕷️ 爬虫监控提醒\n"
            f"> **标题**: {title}\n"
            f'> **价格**: <font color="warning">{price}</font>\n'
        )

        # 触发推送
        self.notifier.send_markdown(message)

        return item


# -------------------------------------------------------------
# 测试运行
# -------------------------------------------------------------
if __name__ == "__main__":
    # 示例 1: 直接使用推送类
    bot = WechatWebhookNotifier()
    # 获取当前时间并格式化（例如：2026-08-02 20:15:30）
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 将时间拼接到测试消息中
    bot.send_text(f"这是一条来自 Python 爬虫类的测试消息 🚀 \n[{now_str}]")

    # 示例 2: 模拟爬虫管道调用
    pipeline = WechatNotificationPipeline()
    fake_item = {"title": "某商品促销售价", "price": "￥199.00"}
    pipeline.process_item(fake_item)
