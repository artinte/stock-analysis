from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Callable, Generic, Optional, TypeVar

from core.cache.base import Cache

T = TypeVar("T")


class FileCache(Cache[T], Generic[T]):
    """
    基于 JSON 文件的通用缓存。

    特点：
        - 支持过期时间
        - 支持自定义序列化 / 反序列化
        - 自动创建缓存目录
        - 原子写入
        - 适合股票基础信息、ETF 信息等低频变化数据

    注意：
        该类不负责并发锁。
        如果后续需要多进程同时写入，再增加文件锁。
    """

    def __init__(
        self,
        path: str | Path,
        *,
        ttl_days: Optional[int] = None,
        serializer: Optional[Callable[[T], object]] = None,
        deserializer: Optional[Callable[[object], T]] = None,
    ):
        """
        path:
            缓存文件路径。

        ttl_days:
            缓存有效期，单位为天。
            None 表示永不过期。

        serializer:
            将 Python 对象转换为 JSON 可序列化对象。

        deserializer:
            将 JSON 对象恢复为 Python 对象。
        """
        self.path = Path(path)
        self.ttl_days = ttl_days

        self.serializer = serializer
        self.deserializer = deserializer

    def get(
        self,
        key: str,
    ) -> Optional[T]:
        """
        获取指定 key 的缓存。
        """
        data = self._load()

        item = data.get(key)

        if not isinstance(item, dict):
            return None

        cached_at = self._parse_datetime(item.get("cached_at"))

        if cached_at is None:
            return None

        if self._is_expired(cached_at):
            return None

        value = item.get("value")

        if self.deserializer is not None:
            return self.deserializer(value)

        return value

    def set(
        self,
        key: str,
        value: T,
    ) -> None:
        """
        写入指定 key 的缓存。
        """
        data = self._load()

        if self.serializer is not None:
            value = self.serializer(value)

        data[key] = {
            "cached_at": datetime.now().isoformat(timespec="seconds"),
            "value": value,
        }

        self._save(data)

    def delete(
        self,
        key: str,
    ) -> None:
        """
        删除指定 key 的缓存。
        """
        data = self._load()

        if key not in data:
            return

        del data[key]

        self._save(data)

    def clear(self) -> None:
        """
        清空整个缓存文件。
        """
        if self.path.exists():
            self.path.unlink()

    def _load(self) -> dict:
        """
        加载 JSON 文件。
        """
        if not self.path.exists():
            return {}

        try:
            with self.path.open(
                "r",
                encoding="utf-8",
            ) as f:
                data = json.load(f)

            return data if isinstance(data, dict) else {}

        except (OSError, json.JSONDecodeError):
            return {}

    def _save(
        self,
        data: dict,
    ) -> None:
        """
        原子写入 JSON 文件。
        """
        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        temp_path = self.path.with_suffix(self.path.suffix + ".tmp")

        with temp_path.open(
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=2,
            )

        temp_path.replace(self.path)

    def _is_expired(
        self,
        cached_at: datetime,
    ) -> bool:
        """
        判断缓存是否过期。
        """
        if self.ttl_days is None:
            return False

        return datetime.now() - cached_at > timedelta(days=self.ttl_days)

    @staticmethod
    def _parse_datetime(
        value,
    ) -> Optional[datetime]:
        """
        解析缓存时间。
        """
        if not value:
            return None

        try:
            return datetime.fromisoformat(str(value))
        except (TypeError, ValueError):
            return None
