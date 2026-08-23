from utils.stock_industry_category import (
    get_stock_industry_category,
    get_category_stocks,
    get_all_category,
)


def main():
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


if __name__ == "__main__":
    main()
