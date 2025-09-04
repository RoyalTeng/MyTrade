"""
投资组合管理模块集成测试

测试投资组合管理、交易执行、风险控制和绩效分析。
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
from decimal import Decimal

# 添加src到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mytrade.backtest import PortfolioManager


def test_portfolio_manager():
    """投资组合管理模块集成测试"""
    print("="*60)
    print("        投资组合管理模块集成测试")
    print("="*60)
    
    # 1. 测试基本初始化
    print("\n1️⃣ 测试投资组合初始化...")
    try:
        portfolio = PortfolioManager(
            initial_cash=100000,
            commission_rate=0.001,  # 0.1% 手续费
            min_commission=5,       # 最低5元手续费
            max_positions=10        # 最多10个持仓
        )
        
        initial_summary = portfolio.get_portfolio_summary()
        print("✅ 投资组合初始化成功")
        print(f"   初始资金: ¥{initial_summary['cash']:,.2f}")
        print(f"   总资产: ¥{initial_summary['total_value']:,.2f}")
        print(f"   手续费率: {0.001:.1%}")
        print(f"   最大持仓数: 10")
        
    except Exception as e:
        print(f"❌ 投资组合初始化失败: {e}")
        return False
    
    # 2. 测试买入交易
    print("\n2️⃣ 测试买入交易...")
    try:
        # 执行第一笔买入
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
            print(f"✅ 买入交易成功: {test_symbol}")
            print(f"   数量: {buy_shares} 股")
            print(f"   价格: ¥{buy_price}")
            
            # 检查持仓
            positions = portfolio.get_positions()
            if test_symbol in positions:
                position = positions[test_symbol]
                print(f"   持仓数量: {position['shares']}")
                print(f"   成本价: ¥{position['avg_cost']:.2f}")
            else:
                print("❌ 持仓未正确记录")
                return False
        else:
            print("❌ 买入交易失败")
            return False
            
    except Exception as e:
        print(f"❌ 买入交易测试失败: {e}")
        return False
    
    # 3. 测试卖出交易
    print("\n3️⃣ 测试卖出交易...")
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
            print(f"✅ 卖出交易成功: {test_symbol}")
            print(f"   数量: {sell_shares} 股")
            print(f"   价格: ¥{sell_price}")
            
            # 检查持仓变化
            positions = portfolio.get_positions()
            if test_symbol in positions:
                remaining_shares = positions[test_symbol]['shares']
                expected_shares = buy_shares - sell_shares
                if remaining_shares == expected_shares:
                    print(f"✅ 持仓数量正确: {remaining_shares} 股")
                else:
                    print(f"❌ 持仓数量错误: 期望 {expected_shares}, 实际 {remaining_shares}")
                    return False
            else:
                print("❌ 卖出后持仓记录异常")
                return False
        else:
            print("❌ 卖出交易失败")
            return False
            
    except Exception as e:
        print(f"❌ 卖出交易测试失败: {e}")
        return False
    
    # 4. 测试多股票组合
    print("\n4️⃣ 测试多股票投资组合...")
    try:
        # 买入第二只股票
        symbol2 = "000001"
        success1 = portfolio.execute_trade(
            symbol=symbol2,
            action="BUY", 
            shares=100,
            price=12.50,
            reason="构建多股票组合"
        )
        
        # 买入第三只股票
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
            print(f"✅ 多股票组合构建成功: {len(positions)} 只股票")
            
            for symbol, position in positions.items():
                print(f"   {symbol}: {position['shares']} 股, 成本 ¥{position['avg_cost']:.2f}")
        else:
            print("❌ 多股票组合构建失败")
            return False
            
    except Exception as e:
        print(f"❌ 多股票组合测试失败: {e}")
        return False
    
    # 5. 测试市值更新和盈亏计算
    print("\n5️⃣ 测试市值更新和盈亏计算...")
    try:
        # 更新市场价格
        market_prices = {
            test_symbol: 1900.0,  # 上涨
            symbol2: 11.80,       # 下跌
            symbol3: 26.50        # 上涨
        }
        
        portfolio.update_market_values(market_prices)
        
        # 获取更新后的摘要
        summary = portfolio.get_portfolio_summary()
        print("✅ 市值更新成功")
        print(f"   现金: ¥{summary['cash']:,.2f}")
        print(f"   持仓市值: ¥{summary['market_value']:,.2f}")
        print(f"   总资产: ¥{summary['total_value']:,.2f}")
        print(f"   总收益率: {summary['total_return']:.2%}")
        
        # 检查单股票盈亏
        positions = portfolio.get_positions()
        for symbol, position in positions.items():
            if 'unrealized_pnl' in position:
                pnl = position['unrealized_pnl']
                print(f"   {symbol} 未实现盈亏: ¥{pnl:,.2f}")
        
    except Exception as e:
        print(f"❌ 市值更新测试失败: {e}")
        return False
    
    # 6. 测试交易历史和绩效分析
    print("\n6️⃣ 测试交易历史和绩效分析...")
    try:
        # 获取交易历史
        trades = portfolio.get_trade_history()
        print(f"✅ 交易历史记录: {len(trades)} 笔交易")
        
        # 分析交易
        buy_trades = [t for t in trades if t['action'] == 'BUY']
        sell_trades = [t for t in trades if t['action'] == 'SELL']
        print(f"   买入交易: {len(buy_trades)} 笔")
        print(f"   卖出交易: {len(sell_trades)} 笔")
        
        # 计算总手续费
        total_commission = sum(t.get('commission', 0) for t in trades)
        print(f"   总手续费: ¥{total_commission:,.2f}")
        
        # 检查已实现盈亏
        summary = portfolio.get_portfolio_summary()
        if 'realized_pnl' in summary:
            print(f"   已实现盈亏: ¥{summary['realized_pnl']:,.2f}")
        
    except Exception as e:
        print(f"❌ 交易历史分析失败: {e}")
        return False
    
    # 7. 测试风险控制
    print("\n7️⃣ 测试风险控制...")
    try:
        # 测试资金不足情况
        insufficient_trade = portfolio.execute_trade(
            symbol="999999",
            action="BUY",
            shares=10000,  # 大量买入
            price=100.0,
            reason="测试资金不足"
        )
        
        if not insufficient_trade:
            print("✅ 资金不足控制正确")
        else:
            print("❌ 资金不足控制失效")
            return False
        
        # 测试卖空控制
        short_trade = portfolio.execute_trade(
            symbol=test_symbol,
            action="SELL",
            shares=1000,  # 超过持仓数量
            price=1900.0,
            reason="测试卖空控制"
        )
        
        if not short_trade:
            print("✅ 卖空控制正确")
        else:
            print("❌ 卖空控制失效")
            return False
        
    except Exception as e:
        print(f"❌ 风险控制测试失败: {e}")
        return False
    
    # 8. 测试投资组合清仓
    print("\n8️⃣ 测试投资组合清仓...")
    try:
        positions = portfolio.get_positions()
        liquidation_success = True
        
        for symbol, position in positions.items():
            shares = position['shares']
            if shares > 0:
                success = portfolio.execute_trade(
                    symbol=symbol,
                    action="SELL",
                    shares=shares,
                    price=market_prices[symbol],
                    reason="测试清仓"
                )
                if not success:
                    liquidation_success = False
                    print(f"❌ {symbol} 清仓失败")
        
        if liquidation_success:
            # 检查清仓后状态
            final_positions = portfolio.get_positions()
            if not final_positions:  # 空字典
                print("✅ 投资组合清仓成功")
                
                final_summary = portfolio.get_portfolio_summary()
                print(f"   最终现金: ¥{final_summary['cash']:,.2f}")
                print(f"   最终总收益率: {final_summary['total_return']:.2%}")
            else:
                print("❌ 清仓后仍有持仓")
                return False
        else:
            print("❌ 投资组合清仓失败")
            return False
        
    except Exception as e:
        print(f"❌ 投资组合清仓测试失败: {e}")
        return False
    
    # 9. 测试性能指标计算
    print("\n9️⃣ 测试性能指标计算...")
    try:
        # 重新构建小规模组合进行测试
        test_portfolio = PortfolioManager(initial_cash=50000)
        
        # 模拟一系列交易
        trades_data = [
            ("600519", "BUY", 10, 1800, "2024-01-01"),
            ("600519", "SELL", 5, 1850, "2024-01-15"),
            ("000001", "BUY", 100, 12.0, "2024-01-20"),
        ]
        
        for symbol, action, shares, price, date in trades_data:
            test_portfolio.execute_trade(symbol, action, shares, price, f"测试交易-{date}")
        
        # 更新价格并计算指标
        test_portfolio.update_market_values({"600519": 1900, "000001": 12.5})
        
        performance = test_portfolio.calculate_performance_metrics()
        print("✅ 性能指标计算成功")
        
        if performance:
            for key, value in performance.items():
                if isinstance(value, float):
                    print(f"   {key}: {value:.4f}")
                else:
                    print(f"   {key}: {value}")
        
    except Exception as e:
        print(f"❌ 性能指标计算失败: {e}")
        return False
    
    print("\n" + "="*60)
    print("🎉 投资组合管理模块集成测试全部通过!")
    print("="*60)
    print("\n✅ 测试通过的功能:")
    print("   1. 投资组合初始化和配置")
    print("   2. 买入交易执行和记录")
    print("   3. 卖出交易执行和持仓更新")
    print("   4. 多股票投资组合管理")
    print("   5. 市值更新和盈亏计算")
    print("   6. 交易历史和绩效分析")
    print("   7. 风险控制和限制检查")
    print("   8. 投资组合清仓功能")
    print("   9. 性能指标计算")
    
    return True


if __name__ == "__main__":
    success = test_portfolio_manager()
    if success:
        print("\n🚀 投资组合管理模块已准备就绪！")
    else:
        print("\n❌ 投资组合管理模块存在问题，需要修复")
    exit(0 if success else 1)