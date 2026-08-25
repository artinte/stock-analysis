from core.models.industry import Industry
from common.constants import IndustryStandard


class IndustryAdapter:
    """
    行业数据转换器。

    负责：

        DataFrame 查询结果
              ↓
        Industry 模型
    """

    @staticmethod
    def from_stock_query(
        result,
    ) -> Industry:

        df = result.to_df()

        if df.empty:
            raise ValueError("行业查询结果为空")

        row = df.iloc[0]

        return Industry(
            code=str(row.get("code", "")),
            name=row.get("l3") or row.get("l2") or row.get("l1"),
            level_1=row.get("l1"),
            level_2=row.get("l2"),
            level_3=row.get("l3"),
            level_4=row.get("l4"),
            standard=IndustryStandard.SW,
            source="stock_query",
        )
