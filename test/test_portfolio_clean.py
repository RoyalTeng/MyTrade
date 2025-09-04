"""
投资组合管理模块清洁测试

测试投资组合管理、交易执行、风险控制和绩效分析。
"""

import sys
from pathlib import Path

# 添加src到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mytrade.backtest import PortfolioManager


def test_portfolio_manager():
    """投资组合管理模块集成测试"""
    print("="*60)
    print("        投资组合管理模块集成测试")
    print("="*60)
    
    # 1. 测试基本初始化
    print("\n1. 测试投资组合初始化...")
    try:
        portfolio = PortfolioManager(
            initial_cash=100000,
            commission_rate=0.001,
            slippage_rate=0.0005
        )
        
        initial_summary = portfolio.get_portfolio_summary()
        print("PASS: 投资组合初始化成功")
        print(f"   初始资金: {initial_summary['initial_cash']:,.2f}")
        print(f"   当前现金: {initial_summary['current_cash']:,.2f}")
        print(f"   总资产: {initial_summary['total_value']:,.2f}")
        print(f"   手续费率: {portfolio.commission_rate:.1%}")
        
    except Exception as e:
        print(f"FAIL: 投资组合初始化失败: {e}")
        return False
    
    # 2. 测试买入交易
    print("\n2. 测试买入交易...")
    try:
        test_symbol = "600519"
        buy_price = 1800.0
        buy_shares = 50
        
        success = portfolio.execute_trade(
            symbol=test_symbol,
            action="BUY",
            shares=buy_shares,
            price=buy_price,
            reason="测试买入交易"
        )
        
        if success:
            print(f"PASS: 买入交易成功: {test_symbol}")
            print(f"   数量: {buy_shares} 股")
            print(f"   价格: {buy_price}")
            
            # 检查持仓
            positions = portfolio.get_positions()
            if test_symbol in positions:
                position = positions[test_symbol]
                print(f"   持仓数量: {position['shares']}")
                print(f"   平均成本: {position['avg_cost']:.2f}")
            else:
                print("FAIL: 持仓未正确记录")
                return False
        else:
            print("FAIL: 买入交易失败")
            return False
            
    except Exception as e:
        print(f"FAIL: 买入交易测试失败: {e}")
        return False
    
    # 3. 测试卖出交易
    print("\n3. 测试卖出交易...")
    try:
        sell_price = 1850.0
        sell_shares = 20
        
        success = portfolio.execute_trade(
            symbol=test_symbol,
            action="SELL",
            shares=sell_shares,
            price=sell_price,
            reason="测试卖出交易"
        )
        
        if success:
            print(f"PASS: 卖出交易成功: {test_symbol}")
            print(f"   数量: {sell_shares} 股")
            print(f"   价格: {sell_price}")
            
            # 检查持仓变化
            positions = portfolio.get_positions()
            if test_symbol in positions:
                remaining_shares = positions[test_symbol]['shares']
                expected_shares = buy_shares - sell_shares
                if remaining_shares == expected_shares:
                    print(f"PASS: 持仓数量正确: {remaining_shares} 股")
                else:
                    print(f"FAIL: 持仓数量错误: 期望 {expected_shares}, 实际 {remaining_shares}")
                    return False
            else:
                print("FAIL: 卖出后持仓记录异常")
                return False
        else:
            print("FAIL: 卖出交易失败")
            return False
            
    except Exception as e:
        print(f"FAIL: 卖出交易测试失败: {e}")
        return False
    
    # 4. 测试多股票组合
    print("\n4. 测试多股票投资组合...")
    try:
        symbol2 = "000001"
        success1 = portfolio.execute_trade(
            symbol=symbol2,
            action="BUY", 
            shares=100,
            price=12.50,
            reason="构建多股票组合"
        )
        
        symbol3 = "000002"
        success2 = portfolio.execute_trade(
            symbol=symbol3,
            action="BUY",
            shares=200,
            price=25.80,
            reason="构建多股票组合"
        )
        
        if success1 and success2:
            positions = portfolio.get_positions()
            print(f"PASS: 多股票组合构建成功: {len(positions)} 只股票")
            
            for symbol, position in positions.items():
                print(f"   {symbol}: {position['shares']} 股, 成本 {position['avg_cost']:.2f}")
        else:
            print("FAIL: 多股票组合构建失败")
            return False
            
    except Exception as e:
        print(f"FAIL: 多股票组合测试失败: {e}")
        return False
    
    # 5. 测试市值更新和盈亏计算
    print("\n5. 测试市值更新和盈亏计算...")
    try:
        market_prices = {
            test_symbol: 1900.0,
            symbol2: 11.80,
            symbol3: 26.50
        }
        
        portfolio.update_market_values(market_prices)
        
        summary = portfolio.get_portfolio_summary()
        print("PASS: 市值更新成功")
        print(f"   现金: {summary['current_cash']:,.2f}")
        print(f"   持仓市值: {summary['market_value']:,.2f}")
        print(f"   总资产: {summary['total_value']:,.2f}")
        print(f"   总收益率: {summary['total_return']:.2%}")
        
    except Exception as e:
        print(f"FAIL: 市值更新测试失败: {e}")
        return False
    
    # 6. 测试交易历史
    print("\n6. 测试交易历史...")
    try:
        trades = portfolio.get_trade_history()
        print(f"PASS: 交易历史记录: {len(trades)} 笔交易")
        
        buy_trades = [t for t in trades if t['action'] == 'BUY']
        sell_trades = [t for t in trades if t['action'] == 'SELL']
        print(f"   买入交易: {len(buy_trades)} 笔")
        print(f"   卖出交易: {len(sell_trades)} 笔")
        
    except Exception as e:
        print(f"FAIL: 交易历史分析失败: {e}")
        return False
    
    # 7. 测试风险控制
    print("\n7. 测试风险控制...")
    try:
        # 测试资金不足情况
        insufficient_trade = portfolio.execute_trade(
            symbol="999999",
            action="BUY",
            shares=10000,
            price=100.0,
            reason="测试资金不足"
        )
        
        if not insufficient_trade:
            print("PASS: 资金不足控制正确")
        else:
            print("FAIL: 资金不足控制失效")
            return False
        
        # 测试卖空控制
        short_trade = portfolio.execute_trade(
            symbol=test_symbol,
            action="SELL",
            shares=1000,
            price=1900.0,
            reason="测试卖空控制"
        )
        
        if not short_trade:
            print("PASS: 卖空控制正确")
        else:
            print("FAIL: 卖空控制失效")
            return False
        
    except Exception as e:
        print(f"FAIL: 风险控制测试失败: {e}")
        return False
    
    print("\n" + "="*60)
    print("PASS: 投资组合管理模块集成测试全部通过!")
    print("="*60)
    
    return True


if __name__ == "__main__":
    success = test_portfolio_manager()
    if success:
        print("\n投资组合管理模块已准备就绪！")
    else:
        print("\n投资组合管理模块存在问题，需要修复")
    exit(0 if success else 1)