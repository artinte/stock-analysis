import asyncio
import aiosqlite
import logging
from config import DB_CONFIG, BROKER_CONFIG
from trading_pipeline import TradingPipeline
from pnl_calculator import PnlCalculator

# 调整日志级别以看得更清楚
logging.getLogger("crawler_storage").setLevel(logging.INFO)

async def init_trading_db():
    """初始化交易流水表（若使用 SQLite）"""
    async with aiosqlite.connect(DB_CONFIG["connection_string"]) as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                broker_order_id TEXT,
                symbol TEXT,
                action TEXT,
                quantity REAL,
                price REAL,
                fee REAL,
                status TEXT,
                timestamp TEXT
            )
        """)
        await conn.commit()

async def main():
    # 1. 初始化数据库表结构
    await init_trading_db()

    # 2. 启动交易管道中心
    pipeline = TradingPipeline(db_config=DB_CONFIG, broker_config=BROKER_CONFIG)
    await pipeline.start()

    print("\n" + "="*50 + "\n🔥 场景一：模拟高并发策略下单（多笔订单连续触发）\n" + "="*50)
    # 模拟买入 AAPL 10股 @ $150
    await pipeline.execute_and_record_order(symbol="AAPL", action="BUY", quantity=10, price=150.0)
    # 模拟买入 AAPL 20股 @ $155 (补仓，成本拉高)
    await pipeline.execute_and_record_order(symbol="AAPL", action="BUY", quantity=20, price=155.0)
    # 模拟卖出 AAPL 15股 @ $165 (部分平仓，锁定利润)
    await pipeline.execute_and_record_order(symbol="AAPL", action="SELL", quantity=15, price=165.0)

    # 等待异步队列把数据安全刷入数据库
    await asyncio.sleep(1.0)
    await pipeline.stop()

    print("\n" + "="*50 + "\n📊 场景二：拉取订单流水并滚动计算账户盈亏(PnL)\n" + "="*50)
    # 重新开启管道用于读取与计算
    await pipeline.start()
    
    # 1. 从高并发持久化层拉取 AAPL 的所有交易记录
    aapl_orders = await pipeline.get_symbol_orders("AAPL")
    print(f"[数据层] 成功查到 AAPL 历史订单共 {len(aapl_orders)} 笔。")

    # 2. 传入当前市场价（假设当前苹果股价回落到了 $160），卷算实时持仓和盈亏
    current_market_price = 160.0
    account_stats = PnlCalculator.calculate_position_and_pnl(aapl_orders, current_market_price)

    print(f"\n【AAPL 资产核算报告】")
    print(f" ➔ 当前持仓数量: {account_stats['current_position']} 股")
    print(f" ➔ 平均持仓成本: ${account_stats['average_cost']}")
    print(f" ➔ 已实现盈亏 (落袋为安): ${account_stats['realized_pnl']}")
    print(f" ➔ 浮动盈亏 (纸面财富): ${account_stats['unrealized_pnl']}")
    print(f" ➔ 账户总净盈亏 (含手续费): ${account_stats['total_pnl']}")
    print(f" ➔ 累计付出手续费: ${account_stats['total_fee']}")

    await pipeline.stop()

if __name__ == "__main__":
    asyncio.run(main())
