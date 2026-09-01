import pandas as pd
import time

# =====================================================================
# 1. 风控接口定义 (目前留空，待后续实现内部逻辑)
# =====================================================================
class RiskManager:
    def __init__(self, max_order_value: float, max_daily_loss: float, blacklist: list, max_tps: int):
        """
        初始化风控参数
        max_order_value: 单笔订单最大允许金额 (元)
        max_daily_loss:  当日最大允许亏损额 (元)
        blacklist:       股票/品种黑名单 (列表)
        max_tps:         每秒最大发单量 (Transactions Per Second)，防刷单
        """
        pass

    def check_order(self, symbol: str, direction: str, amount: int, price: float, current_daily_loss: float) -> tuple[bool, str]:
        """
        事前风控检查接口
        返回值: (是否允许下单: bool, 拒绝原因/通过信息: str)
        """
        # 默认全部放行（待实现）
        return True, "Passed"


# =====================================================================
# 2. 自动化风控测试用例
# =====================================================================

def run_risk_tests():
    print("🚀 开始执行量化系统风控模块（Risk Management）测试...")

    # 初始化一套风控规则
    risk_config = {
        'max_order_value': 50000.0,   # 单笔最多 5 万
        'max_daily_loss': 10000.0,    # 当天最多亏 1 万
        'blacklist': ['600000.SH', '000001.SZ'], # 黑名单股票
        'max_tps': 3                  # 每秒最多发 3 笔单
    }
    
    rm = RiskManager(**risk_config)

    # -----------------------------------------------------------------
    # 测试点 1：正常订单放行
    # 验证目的：合规、金额合规的订单必须正常通过。
    # -----------------------------------------------------------------
    # 买入 100 股 100 元的普通股票（总价 10000 < 50000）
    passed, reason = rm.check_order(symbol='600519.SH', direction='BUY', amount=100, price=100.0, current_daily_loss=0.0)
    assert passed is True, f"【失败】正常订单被误拦: {reason}"
    print("✅ 测试 1 通过：正常合规订单顺利放行。")

    # -----------------------------------------------------------------
    # 测试点 2：单笔超额拦截（Fat Finger / 胖手指测试）
    # 验证目的：防止交易员或算法写错数字，下单金额过大。
    # -----------------------------------------------------------------
    # 买入 1000 股 100 元的股票（总价 100000 > 50000 风控限额）
    passed, reason = rm.check_order(symbol='600519.SH', direction='BUY', amount=1000, price=100.0, current_daily_loss=0.0)
    assert passed is False, "【失败】单笔金额超限，风控竟然没有拦截！"
    assert "金额" in reason or "value" in reason.lower(), f"【失败】拦截原因不明确: {reason}"
    print("✅ 测试 2 通过：单笔超额拦截成功。")

    # -----------------------------------------------------------------
    # 测试点 3：当日最大亏损限额拦截（Daily Stop-Loss）
    # 验证目的：当策略今天已经亏损过大时，不能再开新仓，防止情绪化扩大亏损。
    # -----------------------------------------------------------------
    # 假设当前今天已经亏损了 12000 元（超过了 10000 的限制）
    passed, reason = rm.check_order(symbol='600519.SH', direction='BUY', amount=100, price=100.0, current_daily_loss=12000.0)
    assert passed is False, "【失败】今日亏损已超限，风控没有拦截新开仓订单！"
    assert "亏损" in reason or "loss" in reason.lower(), f"【失败】拦截原因不明确: {reason}"
    print("✅ 测试 3 通过：日内最大亏损保护拦截成功。")

    # -----------------------------------------------------------------
    # 测试点 4：股票黑名单拦截（Compliance / 合规检查）
    # 验证目的：限制交易特定股票（如内幕信息隔离期、高风险待退市ST股）。
    # -----------------------------------------------------------------
    # 尝试购买黑名单中的 600000.SH
    passed, reason = rm.check_order(symbol='600000.SH', direction='BUY', amount=100, price=10.0, current_daily_loss=0.0)
    assert passed is False, "【失败】黑名单股票未被拦截！"
    assert "黑名单" in reason or "blacklist" in reason.lower(), f"【失败】拦截原因不明确: {reason}"
    print("✅ 测试 4 通过：黑名单合规拦截成功。")

    # -----------------------------------------------------------------
    # 测试点 5：流控拦截（Rate Limiting / 频率检查）
    # 验证目的：防止策略代码写错陷入死循环（如无限重试），在一秒内向交易所狂发几百笔订单。
    # -----------------------------------------------------------------
    print("正在测试每秒发单流控（TPS）...")
    # 限制是每秒最多 3 笔。我们连续发 4 笔：
    success_count = 0
    for _ in range(4):
        passed, _ = rm.check_order(symbol='600519.SH', direction='BUY', amount=100, price=100.0, current_daily_loss=0.0)
        if passed:
            success_count += 1
            
    assert success_count <= 3, f"【失败】流控失效！1秒内允许了 {success_count} 笔订单（上限3笔）"
    print("✅ 测试 5 通过：高频发单流控（TPS）拦截成功。")

    print("\n🎉 恭喜！所有核心风控测试全部通过！风控模块安全可靠。")


# =====================================================================
# 3. 程序入口
# =====================================================================
if __name__ == "__main__":
    try:
        run_risk_tests()
    except AssertionError as e:
        print(f"\n❌ 风控测试未通过！缺陷详情：")
        print(e)
