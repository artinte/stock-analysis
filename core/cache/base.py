from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar

T = TypeVar("T")


class Cache(ABC, Generic[T]):
    """
    公共缓存接口。

    不关心具体数据类型，也不关心数据来源。
    """

    @abstractmethod
    def get(
        self,
        key: str,
    ) -> Optional[T]:
        """
        获取缓存。

        缓存不存在或已过期时返回 None。
        """
        raise NotImplementedError

    @abstractmethod
    def set(
        self,
        key: str,
        value: T,
    ) -> None:
        """
        写入缓存。
        """
        raise NotImplementedError

    @abstractmethod
    def delete(
        self,
        key: str,
    ) -> None:
        """
        删除指定缓存。
        """
        raise NotImplementedError

    @abstractmethod
    def clear(self) -> None:
        """
        清空缓存。
        """
        raise NotImplementedError
