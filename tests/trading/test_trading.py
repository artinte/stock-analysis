import pandas as pd

# =====================================================================
# 1. 接口定义 (目前留空，待你后续实现内部功能)
# =====================================================================
class TradingEngine:
    def __init__(self, initial_capital: float):
        """初始化交易引擎"""
        pass

    def load_data(self, df: pd.DataFrame):
        """加载历史 K 线数据"""
        pass

    def place_order(self, direction: str, amount: int, price: float) -> bool:
        """
        下单接口
        direction: 'BUY' 或 'SELL'
        amount: 下单数量（股数/手）
        price: 下单价格
        返回值: 交易成功返回 True，资产不足或失败返回 False
        """
        return False

    def get_balance(self) -> dict:
        """
        获取当前账户状态
        返回值格式: {'cash': 现金, 'holdings': 持仓数量, 'total_value': 总资产}
        """
        return {'cash': 0.0, 'holdings': 0, 'total_value': 0.0}

    def get_logs(self) -> list:
        """获取交易历史日志，每条日志是一个字典"""
        return []


# =====================================================================
# 2. 自动化测试函数 (通过 assert 验证功能是否正确)
# =====================================================================

def run_all_tests():
    print("开始执行交易框架测试...")

    # 准备测试数据：3天的价格
    data = {
        'close': [100.0, 105.0, 95.0]
    }
    mock_df = pd.DataFrame(data, index=pd.date_range(start='2026-01-01', periods=3))

    # -----------------------------------------------------------------
    # 测试点 1：账户初始化
    # 验证目的：创建引擎后，现金和总资产必须等于初始资金，持仓为 0。
    # -----------------------------------------------------------------
    engine = TradingEngine(initial_capital=10000.0)
    balance = engine.get_balance()
    
    assert balance['cash'] == 10000.0, f"期望现金 10000.0，实际得到 {balance['cash']}"
    assert balance['holdings'] == 0, f"期望初始持仓为 0，实际得到 {balance['holdings']}"
    assert balance['total_value'] == 10000.0, "初始总资产计算错误"
    print("✅ 测试 1 通过：账户初始化正常。")

    # -----------------------------------------------------------------
    # 测试点 2：正常买入交易与资产更新
    # 验证目的：以 100 元买入 50 股，现金应减少 5000，持仓变 50，总资产仍为 10000。
    # -----------------------------------------------------------------
    engine.load_data(mock_df)
    success = engine.place_order(direction='BUY', amount=50, price=100.0)
    
    assert success is True, "正常的买入订单被拒绝了"
    balance = engine.get_balance()
    assert balance['cash'] == 5000.0, f"买入后现金扣除错误：{balance['cash']}"
    assert balance['holdings'] == 50, f"买入后持仓更新错误：{balance['holdings']}"
    assert balance['total_value'] == 10000.0, "买入瞬间的总资产不应该发生变化"
    print("✅ 测试 2 通过：正常买入及资产扣减逻辑正确。")

    # -----------------------------------------------------------------
    # 测试点 3：风控限制（本金不足拒绝下单）
    # 验证目的：当前只剩 5000 现金，如果尝试买 100 股（需要 10000），应该被拒绝，且资产不改变。
    # -----------------------------------------------------------------
    fail_success = engine.place_order(direction='BUY', amount=100, price=100.0)
    
    assert fail_success is False, "资金不足的订单应该被拒绝，但系统接受了"
    balance = engine.get_balance()
    assert balance['cash'] == 5000.0, "被拒绝的订单不应该扣除现金"
    print("✅ 测试 3 通过：风控拒单逻辑正常。")

    # -----------------------------------------------------------------
    # 测试点 4：交易日志记录
    # 验证目的：成功发生交易后，日志列表里必须有详细记录，方便后续对账。
    # -----------------------------------------------------------------
    logs = engine.get_logs()
    assert len(logs) == 1, f"应该只有1条成功交易记录，实际有 {len(logs)} 条"
    assert logs[0]['direction'] == 'BUY', "日志中的交易方向记录错误"
    assert logs[0]['price'] == 100.0, "日志中的交易价格记录错误"
    print("✅ 测试 4 通过：交易日志记录完整。")

    print("\n🎉 恭喜！所有核心测试全部通过！交易框架功能完全正常。")


# =====================================================================
# 3. 程序入口
# =====================================================================
if __name__ == "__main__":
    try:
        run_all_tests()
    except AssertionError as e:
        print(f"\n❌ 测试失败！拦截到未实现或错误的逻辑：")
        print(e)
