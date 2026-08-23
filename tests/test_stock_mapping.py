from utils.stock_mapping import StockCodeConverter, get_stock_info


def main():
    print("=" * 70)
    print(" 雪球 URL 拼装与生成测试 ")
    print("=" * 70)

    # 1. 直接拼装雪球链接
    url_1 = StockCodeConverter.get_xueqiu_url("600433")
    url_2 = StockCodeConverter.get_xueqiu_url("600433.SH")
    url_3 = StockCodeConverter.get_xueqiu_url("冠豪高新")
    url_4 = StockCodeConverter.get_xueqiu_url("301391")
    print(f"输入 '600433'    -> 雪球链接: {url_1}")
    print(f"输入 '600433.SH' -> 雪球链接: {url_2}")
    print(f"输入 '冠豪高新'  -> 雪球链接: {url_3}")
    print(f"输入 '301391'    -> 雪球链接: {url_4}")

    print("\n【全维度元数据展示】")
    info = get_stock_info("600433")
    print("600433 元数据:", info)


if __name__ == "__main__":
    main()
