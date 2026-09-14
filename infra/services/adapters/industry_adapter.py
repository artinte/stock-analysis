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
    ) -> Industry | None:

        try:

            # 防止传入错误类型
            if not hasattr(result, "to_df"):
                return None

            df = result.to_df()

            if df is None or df.empty:
                return None

            row = df.iloc[0]

            return Industry(
                symbol=str(row.get("code", "")),
                name=row.get("l3") or row.get("l2") or row.get("l1") or "-",
                level_1=row.get("l1") or "-",
                level_2=row.get("l2") or "-",
                level_3=row.get("l3") or "-",
                level_4=row.get("l4") or "-",
                standard=IndustryStandard.SW,
                source="stock_query",
            )

        except Exception as e:

            print(f"行业数据转换失败: {e}")

            return None
