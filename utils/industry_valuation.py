# -*- coding: utf-8 -*-
from functools import lru_cache
from typing import Dict, Optional, Union
import pandas as pd
from download_pe_ratio import get_csindex_pe_data

"""
==========================================================================================
脚本名称: industry_valuation.py
所属项目: stock-analysis (量化选股数据矩阵框架)
脚本功能: 提供行业与个股估值指标 (PE, TTM PE, PB, 股息率) 的缓存读取与快捷查询 API。
==========================================================================================
"""

ZH_NUM_MAP = {1: "一", 2: "二", 3: "三", 4: "四"}


@lru_cache(maxsize=2)
def _get_cached_valuation_data(category: str = "csindex") -> Dict[str, pd.DataFrame]:
    """读取数据并自动清洗映射为统一表头 (带多表头兼容机制)"""
    raw_dict = get_csindex_pe_data(category=category)
    cleaned_dict: Dict[str, pd.DataFrame] = {}
    category_prefix = "中上协" if category == "csrc" else "中证"

    for sheet_name, raw_df in raw_dict.items():
        if raw_df is None or raw_df.empty:
            continue

        df = raw_df.copy()

        # 1. 清洗【个股数据】
        if "个股" in sheet_name or "股票" in sheet_name:
            code_col = next(
                (
                    c
                    for c in ["股票代码", "证券代码", "成分券代码", "代码"]
                    if c in df.columns
                ),
                df.columns[0],
            )
            name_col = next(
                (
                    c
                    for c in ["股票简称", "证券简称", "成分券名称", "名称"]
                    if c in df.columns
                ),
                df.columns[1],
            )

            # 模糊兼容多种中英文列名
            rename_dict = {
                code_col: "code",
                name_col: "name",
            }

            for col in df.columns:
                col_str = str(col)
                if "静态" in col_str or "静态市盈率" in col_str:
                    rename_dict[col] = "static_pe"
                elif "滚动" in col_str or "TTM" in col_str or "滚动市盈率" in col_str:
                    rename_dict[col] = "ttm_pe"
                elif "市净率" in col_str or "PB" in col_str:
                    rename_dict[col] = "pb"
                elif "股息率" in col_str:
                    rename_dict[col] = "dv_ratio"
                elif "行业名称" in col_str or "所属行业" in col_str:
                    rename_dict[col] = "industry"
                elif "行业代码" in col_str:
                    rename_dict[col] = "industry_code"

            # 兼容可能存在的级次行业（如果有）
            for lvl_num, lvl_zh in ZH_NUM_MAP.items():
                for c in df.columns:
                    if f"{category_prefix}{lvl_zh}级" in str(
                        c
                    ) or f"{lvl_zh}级行业" in str(c):
                        if "代码" in str(c):
                            rename_dict[c] = f"l{lvl_num}_code"
                        else:
                            rename_dict[c] = f"l{lvl_num}"

            df = df.rename(columns=rename_dict)
            df["code"] = (
                df["code"].astype(str).str.split(".").str[0].str.strip().str.zfill(6)
            )
            df["name"] = df["name"].astype(str).str.strip()
            cleaned_dict["stock"] = df

        # 2. 清洗【行业估值】(静态/滚动/PB/股息率)
        else:
            ind_code_col = next(
                (c for c in ["行业代码", "代码"] if c in df.columns), df.columns[0]
            )
            ind_name_col = next(
                (c for c in ["行业名称", "名称"] if c in df.columns), df.columns[1]
            )

            rename_dict = {
                ind_code_col: "ind_code",
                ind_name_col: "ind_name",
                "行业层级": "level",
            }

            for col in df.columns:
                col_str = str(col)
                if "静态" in col_str:
                    rename_dict[col] = "static_pe"
                elif "滚动" in col_str or "TTM" in col_str:
                    rename_dict[col] = "ttm_pe"
                elif "市净率" in col_str or "PB" in col_str:
                    rename_dict[col] = "pb"
                elif "股息率" in col_str:
                    rename_dict[col] = "dv_ratio"

            df = df.rename(columns=rename_dict)

            if "ind_code" in df.columns:
                df["ind_code"] = (
                    df["ind_code"]
                    .astype(str)
                    .str.split(".")
                    .str[0]
                    .str.strip()
                    .str.zfill(6)
                )
            if "ind_name" in df.columns:
                df["ind_name"] = df["ind_name"].astype(str).str.strip()

            if "静态" in sheet_name:
                cleaned_dict["static_pe"] = df
            elif "滚动" in sheet_name or "TTM" in sheet_name:
                cleaned_dict["ttm_pe"] = df
            elif "市净率" in sheet_name or "PB" in sheet_name:
                cleaned_dict["pb"] = df
            elif "股息率" in sheet_name:
                cleaned_dict["dv_ratio"] = df

    return cleaned_dict


# ==========================================================================================
# 外部快捷调用 API
# ==========================================================================================


def get_industry_valuation(
    industry: str, pe_type: str = "ttm", category: str = "csindex"
) -> Optional[pd.DataFrame]:
    """快捷获取指定行业的估值指标"""
    type_map = {
        "ttm": "ttm_pe",
        "static": "static_pe",
        "pb": "pb",
        "dv": "dv_ratio",
    }
    key = type_map.get(pe_type.lower(), "ttm_pe")
    data_dict = _get_cached_valuation_data(category=category)

    df = data_dict.get(key)
    if df is None or df.empty:
        return None

    target = str(industry).strip()
    mask = (df["ind_name"].str.contains(target, na=False)) | (
        df["ind_code"] == target.zfill(6)
    )
    return df[mask].reset_index(drop=True)


def get_industry_pe(
    industry: str, pe_type: str = "ttm", category: str = "csindex"
) -> Optional[float]:
    """直接返回某行业的指定 PE/PB 数值"""
    df = get_industry_valuation(industry, pe_type=pe_type, category=category)
    if df is not None and not df.empty:
        val_col = (
            "ttm_pe"
            if pe_type == "ttm"
            else ("static_pe" if pe_type == "static" else pe_type)
        )
        if val_col in df.columns:
            try:
                return float(df.iloc[0][val_col])
            except (ValueError, TypeError):
                return None
    return None


def get_stock_valuation(
    stock: str, category: str = "csindex"
) -> Optional[pd.DataFrame]:
    """快捷获取某只股票的个股估值及所属行业分类"""
    data_dict = _get_cached_valuation_data(category=category)
    df = data_dict.get("stock")
    if df is None or df.empty:
        return None

    target = str(stock).strip()
    clean_code = target.split(".")[0].zfill(6)

    mask = (df["code"] == clean_code) | (df["name"].str.contains(target, na=False))
    return df[mask].reset_index(drop=True)


# ==========================================================================================
# 使用示例
# ==========================================================================================
if __name__ == "__main__":
    # 1. 快速查单个行业的滚动 PE
    bank_pe = get_industry_pe("银行", pe_type="ttm")
    print(f"📌 银行行业滚动市盈率 (TTM PE): {bank_pe}")

    # 2. 获取半导体行业的完整估值行
    semi_df = get_industry_valuation("半导体", pe_type="static")
    print("\n📌 半导体行业静态 PE 查询结果:")
    print(semi_df)

    # 3. 查某只股票的估值与所属行业 (加安全列切片，避免 KeyError)
    maotai_df = get_stock_valuation("贵州茅台")
    print("\n📌 贵州茅台估值数据原始表头:", list(maotai_df.columns))
    print("\n📌 贵州茅台查询结果:")

    # 动态匹配现有的列进行打印
    want_cols = [
        "code",
        "name",
        "static_pe",
        "ttm_pe",
        "pb",
        "dv_ratio",
        "industry",
        "l1",
        "l2",
        "l3",
    ]
    existing_cols = [c for c in want_cols if c in maotai_df.columns]
    print(maotai_df[existing_cols])
