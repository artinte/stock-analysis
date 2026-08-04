from functools import lru_cache
from typing import List, Union
import pandas as pd

# 引入你的数据获取模块
from download_industry_data import get_csindex_industry_data

LEVEL_MAP = {
    1: "一",
    "1": "一",
    "一级": "一",
    2: "二",
    "2": "二",
    "二级": "二",
    3: "三",
    "3": "三",
    "三级": "三",
    4: "四",
    "4": "四",
    "四级": "四",
}


class StockItem:
    """单只股票数据对象，支持属性访问 (stock.code, stock.name, stock.l3 等)"""

    def __init__(self, row_dict: dict):
        self.code = str(row_dict.get("code", "")).zfill(6)
        self.name = row_dict.get("name", "")
        self.l1 = row_dict.get("l1", "")
        self.l2 = row_dict.get("l2", "")
        self.l3 = row_dict.get("l3", "")
        self.l4 = row_dict.get("l4", "")

    def __repr__(self):
        return f"<Stock {self.code} {self.name} | {self.l1}->{self.l2}->{self.l3}->{self.l4}>"

    def to_dict(self):
        return {
            "code": self.code,
            "name": self.name,
            "l1": self.l1,
            "l2": self.l2,
            "l3": self.l3,
            "l4": self.l4,
        }


class StockQueryResult:
    """股票查询结果容器，封装 DataFrame，解决访问繁琐问题"""

    def __init__(self, df: pd.DataFrame):
        self._df = df.reset_index(drop=True)

    def top(self, n: int = 5):
        """替代 .head(n)"""
        return StockQueryResult(self._df.head(n))

    def summary(self, level: int = 3) -> pd.DataFrame:
        """只提取核心摘要列 (代码、名称、指定行业层级)，免去手写繁琐长列名"""
        target_lvl = f"l{level}"
        cols = ["code", "name", target_lvl]
        return self._df[[c for c in cols if c in self._df.columns]]

    def to_list(self) -> List[StockItem]:
        """转为 Python 对象列表，外部用 stock.code / stock.name / stock.l3 访问"""
        return [StockItem(row) for row in self._df.to_dict(orient="records")]

    def to_df(self) -> pd.DataFrame:
        """需要使用原生 Pandas 高级操作时提取底层 DataFrame"""
        return self._df

    def __len__(self):
        return len(self._df)

    def __repr__(self):
        # 默认只展示精简的核心列，直接 print 不会刷屏折行
        show_cols = [c for c in ["code", "name", "l2", "l3"] if c in self._df.columns]
        return self._df[show_cols].to_string(index=False)


class CategoryQueryResult:
    """行业分类列表容器"""

    def __init__(self, data: Union[List[str], pd.DataFrame]):
        self._data = data

    def top(self, n: int = 5):
        """替代 .head(n)，查看前 N 个分类"""
        if isinstance(self._data, pd.DataFrame):
            return CategoryQueryResult(self._data.head(n))
        return CategoryQueryResult(self._data[:n])

    def to_list(self) -> List[str]:
        """直接获取纯字符串名称列表"""
        if isinstance(self._data, pd.DataFrame):
            return self._data.iloc[:, -1].dropna().tolist()
        return self._data

    def to_df(self) -> pd.DataFrame:
        """获取包含分类代码和分类名称的 DataFrame"""
        if isinstance(self._data, pd.DataFrame):
            return self._data
        return pd.DataFrame(self._data, columns=["category_name"])

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        if isinstance(self._data, pd.DataFrame):
            return self._data.to_string(index=False)
        return (
            f"全量行业分类 ({len(self._data)}个):\n"
            + ", ".join(map(str, self._data[:10]))
            + ("..." if len(self._data) > 10 else "")
        )


@lru_cache(maxsize=1)
def _get_cached_data() -> pd.DataFrame:
    """读取数据并自动清洗映射为统一表头 (code, name, l1, l2, l3, l4)"""
    df = get_csindex_industry_data().copy()
    code_col = next(
        (c for c in ["证券代码", "成分券代码", "代码"] if c in df.columns),
        df.columns[0],
    )

    rename_dict = {code_col: "code", "证券简称": "name"}
    for lvl_num, lvl_zh in LEVEL_MAP.items():
        if isinstance(lvl_num, int):
            rename_dict[f"中证{lvl_zh}级行业分类简称"] = f"l{lvl_num}"
            rename_dict[f"中证{lvl_zh}级行业分类代码"] = f"l{lvl_num}_code"

    df = df.rename(columns=rename_dict)
    df["code"] = df["code"].astype(str).str.zfill(6)
    return df


# ==========================================================================================
# 核心查询 API 封装
# ==========================================================================================


def get_stock_industry_category(
    stock_codes: Union[str, int, List], top: int = None
) -> StockQueryResult:
    """
    1. 查询指定股票的行业分类 (如贵州茅台)
    """
    df = _get_cached_data()
    codes = [
        str(c).zfill(6)
        for c in ([stock_codes] if isinstance(stock_codes, (str, int)) else stock_codes)
    ]
    res = df[df["code"].isin(codes)]
    if top:
        res = res.head(top)
    return StockQueryResult(res)


def get_category_stocks(
    category_name: str, level: int = None, top: int = None
) -> StockQueryResult:
    """
    获取某个行业下的所有股票 (支持模糊匹配和跨层级自动检索)

    :param category_name: 行业名称或行业代码 (如 "半导体"、"半导体与半导体生产设备"、"600519")
    :param level: 行业层级 (1/2/3/4 或 "一级"/"二级")。若传 None，则自动在所有层级中模糊检索
    :param top: 返回前 N 条结果
    """
    df = _get_cached_data()
    clean_cat = str(category_name).strip()

    # 1. 如果指定了 level，在指定层级查找
    if level is not None:
        lvl_num = {"一": 1, "二": 2, "三": 3, "四": 4}.get(
            LEVEL_MAP.get(level, level), level
        )
        target_col = f"l{lvl_num}_code" if clean_cat.isdigit() else f"l{lvl_num}"

        # 先试精准匹配
        res = df[df[target_col].astype(str).str.strip() == clean_cat]

        # 匹配不到则尝试模糊匹配 (包含关系)
        if res.empty and not clean_cat.isdigit():
            res = df[df[target_col].astype(str).str.contains(clean_cat, na=False)]

    # 2. 如果未指定 level，自动搜寻全量 1~4 级行业分类列
    else:
        if clean_cat.isdigit():
            # 按行业代码检索
            code_cols = [
                c for c in df.columns if c.startswith("l") and c.endswith("_code")
            ]
            mask = (
                df[code_cols]
                .astype(str)
                .apply(lambda col: col.str.strip() == clean_cat)
                .any(axis=1)
            )
            res = df[mask]
        else:
            # 按行业名称检索 (全层级包含模糊匹配)
            name_cols = [c for c in ["l1", "l2", "l3", "l4"] if c in df.columns]
            mask = (
                df[name_cols]
                .astype(str)
                .apply(lambda col: col.str.contains(clean_cat, na=False))
                .any(axis=1)
            )
            res = df[mask]

    if top:
        res = res.head(top)

    return StockQueryResult(res)


def get_all_category(
    level: int = 1, return_code: bool = False, top: int = None
) -> CategoryQueryResult:
    """
    3. 获取全量行业分类列表
    """
    df = _get_cached_data()
    lvl_num = {"一": 1, "二": 2, "三": 3, "四": 4}.get(
        LEVEL_MAP.get(level, level), level
    )

    name_col = f"l{lvl_num}"
    code_col = f"l{lvl_num}_code"

    if return_code and code_col in df.columns:
        res_df = (
            df[[code_col, name_col]].dropna().drop_duplicates().reset_index(drop=True)
        )
        res_df.columns = ["category_code", "category_name"]
        if top:
            res_df = res_df.head(top)
        return CategoryQueryResult(res_df)

    res_list = df[name_col].dropna().unique().tolist()
    if top:
        res_list = res_list[:top]
    return CategoryQueryResult(res_list)


# ==========================================================================================
# 完整测试示例 (覆盖所提的所有场景)
# ==========================================================================================
if __name__ == "__main__":

    print("==================================================================")
    print(" 示例 1: 查【个股】行业信息 (以贵州茅台为例)")
    print("==================================================================")
    maotai = get_stock_industry_category("600519")

    # (1) 直接打印容器对象（自动过滤冗余列，输出清爽）
    print("\n[1.1 直接 print 结果容器]:")
    print(maotai)

    # (2) 快速提取精简摘要 (避免手写复杂的列名过滤)
    print("\n[1.2 使用 .summary(level=3) 提取三级行业摘要]:")
    print(maotai.summary(level=3))

    # (3) 转换为对象列表，使用点语法优雅访问字段
    print("\n[1.3 转换为 StockItem 对象访问属性]:")
    item = maotai.to_list()[0]
    print(f"股票名称: {item.name}")
    print(f"股票代码: {item.code}")
    print(f"一级分类: {item.l1}")
    print(f"三级分类: {item.l3}")

    print("\n==================================================================")
    print(" 示例 2: 查【行业成份股】模糊匹配与检索")
    print("==================================================================")
    # (1) 不限制 level，全层级模糊匹配
    print("[2.1 全层级模糊匹配：输入 '半导体' (不限制 level)]:")
    semi_stocks = get_category_stocks("半导体", top=5)
    print(semi_stocks.summary(level=3))

    # (2) 限定 level=2 进行模糊匹配
    print("\n[2.2 指定层级模糊匹配：输入 '半导体' (指定 level=2)]:")
    l2_semi = get_category_stocks("半导体", level=2, top=5)
    print(l2_semi.summary(level=2))

    # (3) 对象属性遍历
    print("\n[2.3 遍历结果并访问属性]:")
    for stock in semi_stocks.to_list():
        print(
            f"代码: {stock.code} | 名称: {stock.name:<6} | 二级: {stock.l2} | 三级: {stock.l3}"
        )

    print("\n==================================================================")
    print(" 示例 3: 获取【全量行业分类列表】")
    print("==================================================================")
    # (1) 获取全量一级行业分类
    print("[3.1 获取所有一级行业名称]:")
    print(get_all_category(level=1))

    # (2) 获取二级行业并转为纯 Python List
    print("\n[3.2 获取前 5 个二级行业名称 (List[str])]:")
    l2_list = get_all_category(level=2, top=5).to_list()
    print(l2_list)

    # (3) 获取带行业代码映射表
    print("\n[3.3 获取三级行业及对应分类代码]:")
    l3_with_code = get_all_category(level=3, return_code=True, top=5)
    print(l3_with_code)
