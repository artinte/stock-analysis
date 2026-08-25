from gateways.services.adapters.industry_adapter import IndustryAdapter
from core.models.industry import Industry
from core.models.industry_profile import IndustryProfile
from utils.stock_industry_category import StockQueryResult, get_stock_industry_category


class IndustryService:
    """
    行业数据服务。

    负责：

        股票代码
            ↓
        行业分类

        行业分类
            ↓
        行业画像
    """

    def __init__(
        self,
        provider=None,
    ):
        self.provider = provider

    def get_industry(
        self,
        symbol: str,
    ) -> Industry:
        stock_query_result: StockQueryResult = get_stock_industry_category(symbol)
        industry = IndustryAdapter.from_stock_query(stock_query_result)
        return industry

    def get_industry_profile(
        self,
        industry: Industry,
    ) -> IndustryProfile:
        pass
