# -*- coding: utf-8 -*-

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import time
from enum import Enum
from typing import Optional

import requests

logger = logging.getLogger(__name__)


"""
Ollama 本地模型客户端。

提供 Ollama 服务管理、模型发现、模型选择以及文本生成能力。

典型用法：

    model = init_ollama("qwen3:8b")
    if model:
        answer = chat_ollama(
            model,
            "请介绍一下中国股票市场。"
        )

本模块负责本地 Ollama 的基础设施管理，不包含任何业务逻辑。
业务层无需关心 Ollama 是否已经启动，只需要处理最终的模型结果即可。
"""

# =============================================================================
# Configuration
# =============================================================================

BASE_URL = "http://127.0.0.1:11434"
OLLAMA_EXECUTABLE = "ollama"

DEFAULT_MODEL: Optional[str] = None

HEALTHCHECK_TIMEOUT = 1.0
MODEL_LIST_TIMEOUT = 3.0
GENERATE_TIMEOUT = 120.0

STARTUP_TIMEOUT = 15.0
STARTUP_INTERVAL = 0.5

GENERATE_RETRIES = 2


# =============================================================================
# Types
# =============================================================================


class OllamaStatus(Enum):
    """Ollama 服务初始化结果。"""

    SUCCESS = "success"
    NOT_INSTALLED = "not_installed"
    NO_MODELS = "no_models"
    START_FAILED = "start_failed"


# =============================================================================
# Ollama Client
# =============================================================================


class OllamaClient:
    """
    Ollama 本地客户端。

    一个 Client 对象负责：
        - 检查 Ollama 服务
        - 启动 Ollama 服务
        - 获取本地模型
        - 选择模型
        - 调用模型生成文本

    Client 本身不保存模型上下文，也不承担业务状态。
    """

    def __init__(
        self,
        base_url: str = BASE_URL,
        executable: str = OLLAMA_EXECUTABLE,
        *,
        healthcheck_timeout: float = HEALTHCHECK_TIMEOUT,
        model_list_timeout: float = MODEL_LIST_TIMEOUT,
        generate_timeout: float = GENERATE_TIMEOUT,
        startup_timeout: float = STARTUP_TIMEOUT,
        startup_interval: float = STARTUP_INTERVAL,
        generate_retries: int = GENERATE_RETRIES,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.executable = executable

        self.healthcheck_timeout = healthcheck_timeout
        self.model_list_timeout = model_list_timeout
        self.generate_timeout = generate_timeout

        self.startup_timeout = startup_timeout
        self.startup_interval = startup_interval

        self.generate_retries = max(0, generate_retries)

        self._process: Optional[subprocess.Popen] = None

    # -------------------------------------------------------------------------
    # URLs
    # -------------------------------------------------------------------------

    @property
    def tags_url(self) -> str:
        """模型列表接口。"""

        return f"{self.base_url}/api/tags"

    @property
    def generate_url(self) -> str:
        """文本生成接口。"""

        return f"{self.base_url}/api/generate"

    # -------------------------------------------------------------------------
    # Service
    # -------------------------------------------------------------------------

    def is_running(self) -> bool:
        """
        判断 Ollama API 是否已经可以访问。

        这里直接检查 /api/tags，而不是检查系统进程。
        对客户端而言，真正重要的是 API 是否可用。
        """

        try:
            response = requests.get(
                self.tags_url,
                timeout=self.healthcheck_timeout,
            )
            return response.ok

        except requests.RequestException:
            return False

    def _find_executable(self) -> Optional[str]:
        """
        查找 Ollama 可执行文件。

        优先使用 PATH 中的 ollama。
        """

        path = shutil.which(self.executable)

        if path:
            return path

        return None

    def _start_process(self) -> bool:
        """
        启动 ollama serve。

        返回 True 表示进程成功创建。
        进程创建成功并不意味着 API 已经可用，
        后续仍需要 wait_until_ready()。
        """

        executable = self._find_executable()

        if executable is None:
            logger.error(
                "Ollama executable not found: %s",
                self.executable,
            )
            return False

        creationflags = 0

        if os.name == "nt":
            creationflags = getattr(
                subprocess,
                "CREATE_NO_WINDOW",
                0,
            )

        try:
            self._process = subprocess.Popen(
                [executable, "serve"],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=creationflags,
            )

        except OSError as exc:
            logger.error(
                "Failed to start Ollama: %s",
                exc,
            )
            return False

        logger.info("Ollama service is starting...")

        return True

    def _process_exited(self) -> bool:
        """
        判断由当前 Client 启动的 Ollama 进程是否已经退出。
        """

        if self._process is None:
            return False

        return self._process.poll() is not None

    def _wait_until_ready(self) -> bool:
        """
        等待 Ollama API 真正进入可用状态。

        不使用固定 sleep，而是在整个超时时间内持续轮询。
        """

        deadline = time.monotonic() + self.startup_timeout

        while time.monotonic() < deadline:

            if self.is_running():
                logger.info("Ollama service is ready.")
                return True

            if self._process_exited():
                logger.error("Ollama process exited before the API became ready.")
                return False

            time.sleep(self.startup_interval)

        logger.error(
            "Ollama startup timeout after %.1f seconds.",
            self.startup_timeout,
        )

        return False

    def ensure_running(self) -> bool:
        """
        确保 Ollama API 可用。

        如果已经运行，直接复用；
        如果没有运行，则启动 ollama serve 并等待 API 就绪。
        """

        if self.is_running():
            return True

        logger.info("Ollama is not running. Starting service...")

        if not self._start_process():
            return False

        return self._wait_until_ready()

    # -------------------------------------------------------------------------
    # Models
    # -------------------------------------------------------------------------

    def list_models(self) -> list[str]:
        """
        获取当前本地已经安装的模型。

        返回示例：

            [
                "qwen3:8b",
                "deepseek-r1:8b"
            ]
        """

        try:
            response = requests.get(
                self.tags_url,
                timeout=self.model_list_timeout,
            )
            response.raise_for_status()

            payload = response.json()
            models = payload.get("models", [])

            if not isinstance(models, list):
                logger.error("Invalid model list returned by Ollama.")
                return []

            result: list[str] = []

            for item in models:
                if not isinstance(item, dict):
                    continue

                name = item.get("name")

                if isinstance(name, str) and name.strip():
                    result.append(name.strip())

            return result

        except requests.RequestException as exc:
            logger.error(
                "Failed to query Ollama models: %s",
                exc,
            )

        except (ValueError, TypeError):
            logger.error("Invalid JSON returned by Ollama.")

        return []

    @staticmethod
    def choose_model(
        models: list[str],
        preferred: Optional[str] = None,
        *,
        fallback: bool = False,
    ) -> Optional[str]:
        """
        从本地模型中选择一个模型。

        preferred 存在时优先使用 preferred。

        默认不自动降级到其它模型。
        这是有意为之：对于模型驱动的业务，
        静默切换模型通常比直接失败更危险。

        如确实需要自动降级：

            choose_model(
                models,
                "qwen3:8b",
                fallback=True,
            )
        """

        if not models:
            return None

        if preferred is None:
            return models[0]

        if preferred in models:
            return preferred

        if fallback:
            logger.warning(
                "Preferred model '%s' is unavailable; " "falling back to '%s'.",
                preferred,
                models[0],
            )
            return models[0]

        logger.error(
            "Preferred model '%s' is not installed. " "Available models: %s",
            preferred,
            ", ".join(models),
        )

        return None

    # -------------------------------------------------------------------------
    # Initialization
    # -------------------------------------------------------------------------

    def initialize(
        self,
        preferred_model: Optional[str] = None,
        *,
        fallback: bool = False,
    ) -> tuple[OllamaStatus, Optional[str]]:
        """
        初始化 Ollama，并返回最终使用的模型。

        返回：

            (OllamaStatus.SUCCESS, "qwen3:8b")

        或：

            (OllamaStatus.START_FAILED, None)
        """

        executable_available = self._find_executable() is not None

        if not self.ensure_running():

            if not executable_available:
                return (
                    OllamaStatus.NOT_INSTALLED,
                    None,
                )

            return (
                OllamaStatus.START_FAILED,
                None,
            )

        models = self.list_models()

        if not models:
            return (
                OllamaStatus.NO_MODELS,
                None,
            )

        model = self.choose_model(
            models,
            preferred_model,
            fallback=fallback,
        )

        if model is None:
            return (
                OllamaStatus.NO_MODELS,
                None,
            )

        return (
            OllamaStatus.SUCCESS,
            model,
        )

    # -------------------------------------------------------------------------
    # Generation
    # -------------------------------------------------------------------------

    def generate(
        self,
        model: str,
        prompt: str,
        *,
        timeout: Optional[float] = None,
        retries: Optional[int] = None,
    ) -> Optional[str]:
        """
        调用 Ollama 生成文本。

        参数：
            model:
                模型名称，例如 qwen3:8b。

            prompt:
                用户提示词。

            timeout:
                单次请求超时时间。

            retries:
                请求失败后的重试次数。
        """

        if not model:
            logger.error("Model name cannot be empty.")
            return None

        if not prompt or not prompt.strip():
            logger.error("Prompt cannot be empty.")
            return None

        timeout = self.generate_timeout if timeout is None else timeout

        retries = self.generate_retries if retries is None else max(0, retries)

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
        }

        attempts = retries + 1

        for attempt in range(1, attempts + 1):

            try:
                logger.debug(
                    "Calling Ollama model=%s " "(attempt %d/%d)",
                    model,
                    attempt,
                    attempts,
                )

                response = requests.post(
                    self.generate_url,
                    json=payload,
                    timeout=timeout,
                )

                response.raise_for_status()

                data = response.json()

                result = data.get("response")

                if not isinstance(result, str):
                    logger.error(
                        "Ollama response does not contain " "a valid 'response' field."
                    )
                    return None

                result = result.strip()

                if not result:
                    logger.warning("Ollama returned an empty response.")
                    return None

                return result

            except requests.Timeout:
                logger.warning(
                    "Ollama request timed out after %.1fs " "(attempt %d/%d).",
                    timeout,
                    attempt,
                    attempts,
                )

            except requests.ConnectionError:
                logger.warning(
                    "Connection to Ollama failed " "(attempt %d/%d).",
                    attempt,
                    attempts,
                )

            except requests.HTTPError as exc:
                logger.error(
                    "Ollama HTTP error: %s",
                    exc,
                )

                # HTTP 错误一般代表模型不存在、请求参数错误等，
                # 重试不会改变结果，因此不再重复请求。
                return None

            except requests.RequestException as exc:
                logger.error(
                    "Ollama request failed: %s",
                    exc,
                )

            except (ValueError, TypeError):
                logger.error("Invalid JSON response from Ollama.")
                return None

            if attempt < attempts:
                time.sleep(0.8)

        logger.error(
            "Ollama generation failed after %d attempts.",
            attempts,
        )

        return None


# =============================================================================
# Default Client
# =============================================================================

_default_client = OllamaClient()


# =============================================================================
# Public API
# =============================================================================


def get_installed_models(
    base_url: str = BASE_URL,
) -> list[str]:
    """
    获取本地 Ollama 模型。

    保留函数式接口，方便旧代码继续使用。
    """

    client = OllamaClient(base_url=base_url)
    return client.list_models()


def select_model(
    models: list[str],
    preferred_model: Optional[str] = None,
    *,
    allow_fallback: bool = False,
) -> Optional[str]:
    """
    选择模型。

    保留旧版本 API。
    """

    return OllamaClient.choose_model(
        models,
        preferred_model,
        fallback=allow_fallback,
    )


def start_ollama(
    timeout: float = STARTUP_TIMEOUT,
    base_url: str = BASE_URL,
) -> tuple[OllamaStatus, list[str]]:
    """
    启动并检查 Ollama。

    保留旧版本 API。
    """

    client = OllamaClient(
        base_url=base_url,
        startup_timeout=timeout,
    )

    executable_available = client._find_executable() is not None

    if not client.ensure_running():

        if not executable_available:
            return (
                OllamaStatus.NOT_INSTALLED,
                [],
            )

        return (
            OllamaStatus.START_FAILED,
            [],
        )

    models = client.list_models()

    if not models:
        return (
            OllamaStatus.NO_MODELS,
            [],
        )

    return (
        OllamaStatus.SUCCESS,
        models,
    )


def init_ollama(
    preferred_model: Optional[str] = DEFAULT_MODEL,
    *,
    allow_fallback: bool = False,
) -> Optional[str]:
    """
    初始化 Ollama 并返回最终模型。

    示例：

        model = init_ollama("qwen3:8b")

        if model:
            print(model)

    默认情况下，如果 qwen3:8b 不存在，
    不会偷偷切换到其它模型。
    """

    status, model = _default_client.initialize(
        preferred_model,
        fallback=allow_fallback,
    )

    if status is OllamaStatus.SUCCESS:

        print(f"✅ Ollama 就绪，模型: {model}")

        return model

    if status is OllamaStatus.NOT_INSTALLED:

        print("❌ 未找到 Ollama，请先安装 Ollama。")

    elif status is OllamaStatus.NO_MODELS:

        if preferred_model:
            print(f"❌ 未找到可用模型: {preferred_model}")
        else:
            print("❌ Ollama 已运行，但没有安装模型。")

    elif status is OllamaStatus.START_FAILED:

        print("❌ Ollama 启动失败或超时。")

    return None


def chat_ollama(
    model: str,
    prompt: str,
    *,
    base_url: str = BASE_URL,
    timeout: float = GENERATE_TIMEOUT,
    retries: int = GENERATE_RETRIES,
) -> Optional[str]:
    """
    调用 Ollama 模型。

    保留原来的函数式接口。

    示例：

        response = chat_ollama(
            "qwen3:8b",
            "分析一下中国股票市场。"
        )
    """

    client = (
        _default_client
        if base_url.rstrip("/") == BASE_URL.rstrip("/")
        else OllamaClient(base_url=base_url)
    )

    return client.generate(
        model,
        prompt,
        timeout=timeout,
        retries=retries,
    )


if __name__ == "__main__":
    """
    Ollama 完整自检。

    用于：

        python ollama_client.py

    验证：
        1. Ollama 是否存在
        2. Ollama 是否运行
        3. 模型是否安装
        4. qwen3:8b 是否可用
        5. 模型是否能够正常生成
    """

    logging.basicConfig(
        level=logging.INFO,
        format=("%(asctime)s " "[%(levelname)s] " "%(message)s"),
        datefmt="%H:%M:%S",
    )

    model = init_ollama(
        "qwen3:8b",
        allow_fallback=False,
    )

    if not model:
        exit()

    prompt = "请简单介绍一下中国股票市场。\n要求使用中文回答，控制在 200 字以内。"

    print()
    print("🤖 正在调用 Ollama...")
    print()

    response = chat_ollama(
        model,
        prompt,
    )

    if not response:
        print()
        print("❌ 模型调用失败。")
        exit()

    print("========== 用户问题 ==========")
    print()
    print(prompt)
    print()
    print("========== AI 回复 ==========")
    print()
    print(response)
    print()
    print("==============================")
