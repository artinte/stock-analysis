from __future__ import annotations

from gateways.manager import DataManager


def create_manager(provider_name: str) -> DataManager:
    """
    创建并启动 DataManager。

    Args:
        provider_name: 数据源名称。

    Returns:
        已启动的数据管理器。
    """
    data = DataManager(provider_name)
    data.start()
    return data


def close_manager(data: DataManager) -> None:
    """
    安全关闭 DataManager。
    """
    try:
        data.stop()
    except Exception as exc:
        print(f"⚠️ 关闭数据源失败：{exc}")


def print_title(title: str) -> None:
    """
    打印测试标题。
    """
    print()
    print(f"【{title}】")


def print_error(message: str, exc: Exception | None = None) -> None:
    """
    打印统一错误信息。
    """
    if exc is None:
        print(f"❌ {message}")
    else:
        print(f"❌ {message}：{exc}")
