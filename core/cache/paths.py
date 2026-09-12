from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

CACHE_ROOT = PROJECT_ROOT / "data" / "cache"


def get_cache_path(
    provider: str,
    name: str,
) -> Path:
    """
    获取指定数据源的缓存文件路径。

    例如：

        get_cache_path("yinhe", "stock_basic")

        → data/cache/yinhe/stock_basic.json
    """
    return CACHE_ROOT / provider / f"{name}.json"
