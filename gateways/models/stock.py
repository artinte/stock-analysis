from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class Stock:
    """
    股票基础信息。

    该模型用于描述证券本身的静态信息，
    不包含实时行情、估值和财务数据。

    所有数据源最终都应该将自己的原始数据
    转换成 Stock 对象。
    """

    symbol: str

    name: Optional[str] = None

    market: Optional[str] = None

    exchange: Optional[str] = None

    industry: Optional[str] = None

    sector: Optional[str] = None

    listing_date: Optional[str] = None

    ipo_price: Optional[float] = None

    total_shares: Optional[float] = None

    circulating_shares: Optional[float] = None

    chairman: Optional[str] = None

    legal_representative: Optional[str] = None

    company_name: Optional[str] = None

    website: Optional[str] = None

    description: Optional[str] = None