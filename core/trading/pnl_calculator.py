from typing import Dict, Any, List

class PnlCalculator:
    """
    商业化标准的持仓与盈亏计算器（采用移动平均成本法卷算）。
    支持计算：当前持仓量、平均开仓成本、已实现盈亏、浮动盈亏。
    """
    @staticmethod
    def calculate_position_and_pnl(orders: List[Dict[str, Any]], current_market_price: float = None) -> Dict[str, Any]:
        position = 0.0          # 当前持仓数量
        avg_cost = 0.0          # 平均开仓成本 (Avg Cost)
        realized_pnl = 0.0      # 已实现盈亏 (Realized PnL - 已经落袋为安的钱)
        total_fee = 0.0         # 累计交易手续费

        # 按时间正序遍历所有订单，滚动卷算仓位
        for order in sorted(orders, key=lambda x: x.get("timestamp", "")):
            if order["status"] != "FILLED":
                continue
            
            qty = float(order["quantity"])
            price = float(order["price"])
            fee = float(order["fee"])
            total_fee += fee

            if order["action"].upper() == "BUY":
                # 买入：加仓，更新平均成本
                new_position = position + qty
                if new_position > 0:
                    avg_cost = ((position * avg_cost) + (qty * price) + fee) / new_position
                position = new_position
            
            elif order["action"].upper() == "SELL":
                # 卖出：减仓，计算已实现盈亏
                if position > 0:
                    # 盈亏 = (卖出价 - 买入均本) * 卖出数量 - 卖出手续费
                    trade_pnl = (price - avg_cost) * min(qty, position) - fee
                    realized_pnl += trade_pnl
                position = max(0.0, position - qty)
                if position == 0:
                    avg_cost = 0.0  # 清仓后成本归零

        # 计算浮动盈亏 (Unrealized PnL)
        unrealized_pnl = 0.0
        if position > 0 and current_market_price is not None:
            unrealized_pnl = (current_market_price - avg_cost) * position

        return {
            "current_position": position,
            "average_cost": round(avg_cost, 4),
            "realized_pnl": round(realized_pnl, 4),
            "unrealized_pnl": round(unrealized_pnl, 4),
            "total_pnl": round(realized_pnl + unrealized_pnl, 4),
            "total_fee": round(total_fee, 4)
        }
