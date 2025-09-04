"""
投资组合管理模块简化测试
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd

# 添加src到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mytrade.backtest import PortfolioManager


def test_portfolio_simple():
    """投资组合管理模块简化测试"""
    print("="*60)
    print("           投资组合管理模块简化测试")
    print("="*60)
    
    try:
        # 1. 创建投资组合管理器
        print("\n1. 创建投资组合管理器...")
        initial_cash = 100000.0
        portfolio = PortfolioManager(initial_cash=initial_cash)
        print(f"[OK] 投资组合管理器初始化成功")
        print(f"   初始资金: {initial_cash:,.2f}")
        
        # 2. 测试账户摘要
        print("\n2. 测试账户摘要...")
        summary = portfolio.get_portfolio_summary()
        print("[OK] 账户摘要:")
        print(f"   当前现金: {summary.get('current_cash', 0):,.2f}")
        print(f"   市场价值: {summary.get('market_value', 0):,.2f}")
        print(f"   总资产: {summary.get('total_value', 0):,.2f}")
        print(f"   持仓数量: {summary.get('num_positions', 0)}")
        
        # 3. 测试买入交易
        print("\n3. 测试买入交易...")
        buy_result = portfolio.execute_trade(
            symbol="000001",
            action="BUY",
            shares=1000,
            price=12.50,
            reason="测试买入"
        )
        print(f"[OK] 买入交易结果: {'成功' if buy_result else '失败'}")
        
        # 再次检查账户摘要
        summary = portfolio.get_portfolio_summary()
        print("   更新后账户摘要:")
        print(f"   当前现金: {summary.get('current_cash', 0):,.2f}")
        print(f"   市场价值: {summary.get('market_value', 0):,.2f}")
        print(f"   总资产: {summary.get('total_value', 0):,.2f}")
        print(f"   持仓数量: {summary.get('num_positions', 0)}")
        
        # 4. 测试持仓查看
        print("\n4. 测试持仓查看...")
        positions = portfolio.get_positions()
        print(f"[OK] 当前持仓: {len(positions)} 个")
        for symbol, position in positions.items():
            print(f"   {symbol}: {position.get('shares', 0)} 股, 成本价: {position.get('avg_cost', 0):.2f}")
        
        # 5. 测试卖出交易
        print("\n5. 测试卖出交易...")
        sell_result = portfolio.execute_trade(
            symbol="000001",
            action="SELL",
            shares=500,
            price=13.00,
            reason="测试卖出"
        )
        print(f"[OK] 卖出交易结果: {'成功' if sell_result else '失败'}")
        
        # 最终账户摘要
        summary = portfolio.get_portfolio_summary()
        print("\n6. 最终账户摘要:")
        print(f"   当前现金: {summary.get('current_cash', 0):,.2f}")
        print(f"   市场价值: {summary.get('market_value', 0):,.2f}")
        print(f"   总资产: {summary.get('total_value', 0):,.2f}")
        print(f"   持仓数量: {summary.get('num_positions', 0)}")
        
        # 7. 测试交易历史
        print("\n7. 测试交易历史...")
        trades = portfolio.get_trade_history()
        print(f"[OK] 交易历史记录: {len(trades)} 笔")
        for i, trade in enumerate(trades[-3:], 1):  # 显示最后3笔
            print(f"   交易{i}: {trade.get('symbol', 'N/A')} {trade.get('action', 'N/A')} "
                  f"{trade.get('shares', 0)} 股 @ {trade.get('price', 0):.2f}")
        
        print("\n" + "="*60)
        print("投资组合管理模块测试完成")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"[ERROR] 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_portfolio_simple()
    exit(0 if success else 1)