"""
简化集成测试 - 避免编码问题

测试核心功能，不使用特殊字符。
"""

import sys
import os
import tempfile
from pathlib import Path

# 添加src到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_imports():
    """测试基本导入"""
    print("\n=== 测试模块导入 ===")
    
    try:
        from mytrade.config.config_manager import ConfigManager
        print("PASS: 配置管理模块")
    except ImportError as e:
        print(f"FAIL: 配置管理模块 - {e}")
        return False
    
    try:
        from mytrade.data.market_data_fetcher import MarketDataFetcher
        print("PASS: 数据获取模块")
    except ImportError as e:
        print(f"FAIL: 数据获取模块 - {e}")
        return False
    
    try:
        from mytrade.backtest.portfolio_manager import PortfolioManager
        print("PASS: 投资组合模块")
    except ImportError as e:
        print(f"FAIL: 投资组合模块 - {e}")
        return False
    
    return True

def test_portfolio():
    """测试投资组合功能"""
    print("\n=== 测试投资组合功能 ===")
    
    try:
        from mytrade.backtest.portfolio_manager import PortfolioManager
        
        # 创建投资组合
        portfolio = PortfolioManager(initial_cash=100000)
        
        # 检查初始状态
        summary = portfolio.get_portfolio_summary()
        if summary['current_cash'] == 100000:
            print("PASS: 投资组合初始化")
        else:
            print("FAIL: 投资组合初始化")
            return False
        
        # 执行买入
        success = portfolio.execute_trade(
            symbol="TEST001",
            action="BUY", 
            shares=100,
            price=50.0,
            reason="测试买入"
        )
        
        if success:
            print("PASS: 买入交易")
        else:
            print("FAIL: 买入交易")
            return False
        
        # 检查持仓
        positions = portfolio.get_positions()
        if "TEST001" in positions:
            print("PASS: 持仓记录")
        else:
            print("FAIL: 持仓记录")
            return False
        
        return True
        
    except Exception as e:
        print(f"FAIL: 投资组合测试异常 - {e}")
        return False

def test_logging():
    """测试日志功能"""
    print("\n=== 测试日志功能 ===")
    
    try:
        from mytrade.logging.interpretable_logger import InterpretableLogger
        
        with tempfile.TemporaryDirectory() as temp_dir:
            logger = InterpretableLogger(
                log_dir=str(Path(temp_dir) / "logs"),
                enable_console_output=False
            )
            
            # 开始会话
            session_id = logger.start_trading_session("TEST", "2024-01-01")
            if session_id:
                print("PASS: 会话开始")
            else:
                print("FAIL: 会话开始")
                return False
            
            # 记录步骤
            logger.log_analysis_step(
                agent_type="TEST",
                input_data={},
                analysis_process="测试",
                conclusion="结论",
                confidence=0.8,
                reasoning=["原因"]
            )
            print("PASS: 步骤记录")
            
            # 结束会话
            logger.end_trading_session(final_decision={"test": True})
            print("PASS: 会话结束")
        
        return True
        
    except Exception as e:
        print(f"FAIL: 日志测试异常 - {e}")
        return False

def main():
    """主函数"""
    print("开始简化集成测试...")
    
    tests = [
        ("模块导入", test_imports),
        ("投资组合", test_portfolio), 
        ("日志功能", test_logging)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"异常: {name} - {e}")
            results.append((name, False))
    
    # 统计结果
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print("\n=== 测试结果 ===")
    for name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{status}: {name}")
    
    print(f"\n总计: {passed}/{total}")
    
    if passed == total:
        print("所有测试通过!")
        return True
    else:
        print("部分测试失败!")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)