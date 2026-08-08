import requests
import subprocess
import time
from enum import Enum
from typing import List, Tuple

BASE_URL = "http://127.0.0.1:11434"


class OllamaStatus(Enum):
    SUCCESS = "SUCCESS"  # 正常启动且有模型
    NOT_INSTALLED = "NOT_INSTALLED"  # 未安装 Ollama
    NO_MODELS = "NO_MODELS"  # 正常启动但无可用模型
    START_FAILED = "START_FAILED"  # 启动超时或失败


def get_installed_models(base_url=BASE_URL) -> List[str]:
    """获取本地已安装的模型列表"""
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=2)
        if response.status_code == 200:
            models = response.json().get("models", [])
            return [model["name"] for model in models]
    except Exception:
        pass
    return []


def start_ollama(timeout=3) -> Tuple[OllamaStatus, List[str]]:
    """启动 Ollama 并返回运行状态码及模型列表

    Returns:
        Tuple[OllamaStatus, List[str]]: (状态码, 模型列表)
    """
    url = f"{BASE_URL}/api/tags"

    # 1. 检查是否已经启动
    try:
        # 请求模型是否成功
        requests.get(url, timeout=1)
        # 请求成功，获取已安装模型
        models = get_installed_models()
        if not models:
            return OllamaStatus.NO_MODELS, []
        return OllamaStatus.SUCCESS, models
    except requests.RequestException:
        pass

    # 2. 尝试后台启动 Ollama
    print("🚀 正在启动 Ollama...")
    try:
        subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        return OllamaStatus.NOT_INSTALLED, []
    except Exception:
        return OllamaStatus.START_FAILED, []

    # 3. 轮询等待服务就绪
    for _ in range(timeout):
        try:
            requests.get(url, timeout=1)
            models = get_installed_models()
            if not models:
                return OllamaStatus.NO_MODELS, []
            return OllamaStatus.SUCCESS, models
        except requests.RequestException:
            time.sleep(1)

    return OllamaStatus.START_FAILED, []
