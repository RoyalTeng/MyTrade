"""
最小化集成测试

测试核心功能，不依赖外部网络服务。
"""

import sys
import os
import tempfile
from pathlib import Path
from datetime import datetime, timedelta

# 添加src到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# 导入编码修复工具
from test_encoding_fix import safe_print

def test_basic_imports():
    """测试基本导入功能"""
    safe_print("="*60)
    safe_print("           最小化集成测试")
    safe_print("="*60)
    
    safe_print("\n1. 测试基本模块导入...")
    
    # 测试配置模块
    try:
        from mytrade.config.config_manager import ConfigManager
        safe_print("Pass: 配置管理模块导入成功")
    except ImportError as e:
        safe_print(f"❌ 配置管理模块导入失败: {e}")
        return False
    
    # 测试数据模块
    try:
        from mytrade.data.market_data_fetcher import MarketDataFetcher
        safe_print("✅ 数据获取模块导入成功")
    except ImportError as e:
        safe_print(f"❌ 数据获取模块导入失败: {e}")
        return False
    
    # 测试交易模块
    try:
        from mytrade.trading.signal_generator import SignalGenerator
        safe_print("✅ 信号生成模块导入成功")
    except ImportError as e:
        safe_print(f"❌ 信号生成模块导入失败: {e}")
        return False
    
    # 测试回测模块
    try:
        from mytrade.backtest.backtest_engine import BacktestEngine
        from mytrade.backtest.portfolio_manager import PortfolioManager
        safe_print("✅ 回测模块导入成功")
    except ImportError as e:
        safe_print(f"❌ 回测模块导入失败: {e}")
        return False
    
    # 测试日志模块
    try:
        from mytrade.logging.interpretable_logger import InterpretableLogger
        safe_print("✅ 日志模块导入成功")
    except ImportError as e:
        safe_print(f"❌ 日志模块导入失败: {e}")
        return False
    
    return True


def test_portfolio_basic():
    """测试投资组合基本功能"""
    safe_print("\n2️⃣ 测试投资组合基本功能...")
    
    try:
        from mytrade.backtest.portfolio_manager import PortfolioManager
        
        # 创建投资组合
        portfolio = PortfolioManager(
            initial_cash=100000,
            commission_rate=0.001
        )
        
        # 获取初始摘要
        summary = portfolio.get_portfolio_summary()
        if summary['cash'] == 100000 and summary['total_value'] == 100000:
            safe_print("✅ 投资组合初始化正确")
        else:
            safe_print("❌ 投资组合初始化失败")
            return False
        
        # 测试买入交易
        success = portfolio.execute_trade(
            symbol="TEST001",
            action="BUY",
            shares=100,
            price=50.0,
            reason="测试买入"
        )
        
        if success:
            positions = portfolio.get_positions()
            if "TEST001" in positions and positions["TEST001"]["shares"] == 100:
                safe_print("✅ 买入交易执行正确")
            else:
                safe_print("❌ 买入交易记录错误")
                return False
        else:
            safe_print("❌ 买入交易失败")
            return False
        
        # 测试卖出交易
        success = portfolio.execute_trade(
            symbol="TEST001",
            action="SELL",
            shares=50,
            price=55.0,
            reason="测试卖出"
        )
        
        if success:
            positions = portfolio.get_positions()
            if "TEST001" in positions and positions["TEST001"]["shares"] == 50:
                safe_print("✅ 卖出交易执行正确")
            else:
                safe_print("❌ 卖出交易记录错误")
                return False
        else:
            safe_print("❌ 卖出交易失败")
            return False
        
        # 测试市值更新
        portfolio.update_market_values({"TEST001": 60.0})
        updated_summary = portfolio.get_portfolio_summary()
        expected_market_value = 50 * 60.0  # 50股 * 60元
        
        if abs(updated_summary['market_value'] - expected_market_value) < 0.01:
            safe_print("✅ 市值更新正确")
        else:
            safe_print(f"❌ 市值更新错误: 期望 {expected_market_value}, 实际 {updated_summary['market_value']}")
            return False
        
        return True
        
    except Exception as e:
        safe_print(f"❌ 投资组合测试失败: {e}")
        return False


def test_config_basic():
    """测试配置管理基本功能"""
    safe_print("\n3️⃣ 测试配置管理基本功能...")
    
    try:
        from mytrade.config.config_manager import ConfigManager
        import yaml
        
        # 创建临时配置文件
        test_config = {
            'data': {
                'source': 'akshare',
                'cache_dir': 'data/cache',
                'cache_days': 7
            },
            'trading_agents': {
                'model_fast': 'gpt-3.5-turbo',
                'model_slow': 'gpt-4'
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(test_config, f)
            config_path = f.name
        
        try:
            # 测试配置加载
            config_manager = ConfigManager(config_path)
            config = config_manager.get_config()
            
            if config.data.source == 'akshare' and config.data.cache_days == 7:
                safe_print("✅ 配置文件加载正确")
            else:
                safe_print("❌ 配置文件解析错误")
                return False
            
            # 测试配置验证
            if config_manager.validate_config():
                safe_print("✅ 配置验证通过")
            else:
                safe_print("❌ 配置验证失败")
                return False
            
            return True
            
        finally:
            os.unlink(config_path)
        
    except Exception as e:
        safe_print(f"❌ 配置管理测试失败: {e}")
        return False


def test_logging_basic():
    """测试日志系统基本功能"""
    safe_print("\n4️⃣ 测试日志系统基本功能...")
    
    try:
        from mytrade.logging.interpretable_logger import InterpretableLogger
        
        with tempfile.TemporaryDirectory() as temp_dir:
            logger = InterpretableLogger(
                log_dir=str(Path(temp_dir) / "test_logs"),
                enable_console_output=False
            )
            
            # 开始交易会话
            session_id = logger.start_trading_session("TEST001", "2024-01-01")
            if session_id:
                safe_print("✅ 交易会话开始成功")
            else:
                safe_print("❌ 交易会话开始失败")
                return False
            
            # 记录分析步骤
            logger.log_analysis_step(
                agent_type="TECHNICAL_ANALYST",
                input_data={"test": "data"},
                analysis_process="测试分析过程",
                conclusion="测试结论",
                confidence=0.8,
                reasoning=["测试推理1", "测试推理2"]
            )
            safe_print("✅ 分析步骤记录成功")
            
            # 记录决策点
            logger.log_decision_point(
                context="测试决策",
                options=[{"action": "BUY"}, {"action": "HOLD"}],
                chosen_option={"action": "BUY"},
                rationale="测试理由",
                confidence=0.75
            )
            safe_print("✅ 决策点记录成功")
            
            # 结束会话
            summary = logger.end_trading_session(
                final_decision={"action": "BUY", "shares": 100}
            )
            
            if summary and summary.get('session_id') == session_id:
                safe_print("✅ 交易会话结束成功")
                return True
            else:
                safe_print("❌ 交易会话结束失败")
                return False
        
    except Exception as e:
        safe_print(f"❌ 日志系统测试失败: {e}")
        return False


def test_error_handling_basic():
    """测试基本错误处理"""
    safe_print("\n5️⃣ 测试基本错误处理...")
    
    try:
        from mytrade.backtest.portfolio_manager import PortfolioManager
        
        portfolio = PortfolioManager(initial_cash=1000)
        
        # 测试资金不足
        insufficient_result = portfolio.execute_trade(
            symbol="TEST001",
            action="BUY",
            shares=100,
            price=50.0,  # 需要5000元，但只有1000元
            reason="测试资金不足"
        )
        
        if not insufficient_result:
            safe_print("✅ 资金不足错误处理正确")
        else:
            safe_print("❌ 资金不足错误处理失效")
            return False
        
        # 测试卖空保护
        oversell_result = portfolio.execute_trade(
            symbol="TEST001",
            action="SELL",
            shares=10,  # 卖出未持有的股票
            price=50.0,
            reason="测试卖空"
        )
        
        if not oversell_result:
            safe_print("✅ 卖空保护正确")
        else:
            safe_print("❌ 卖空保护失效")
            return False
        
        return True
        
    except Exception as e:
        safe_print(f"❌ 错误处理测试失败: {e}")
        return False


def main():
    """主测试函数"""
    safe_print("开始最小化集成测试...")
    
    test_results = []
    
    # 运行各项测试
    tests = [
        ("基本模块导入", test_basic_imports),
        ("投资组合功能", test_portfolio_basic),
        ("配置管理功能", test_config_basic),
        ("日志系统功能", test_logging_basic),
        ("错误处理能力", test_error_handling_basic)
    ]
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            test_results.append((test_name, result))
        except Exception as e:
            safe_print(f"❌ {test_name}测试异常: {e}")
            test_results.append((test_name, False))
    
    # 输出测试结果
    safe_print("\n" + "="*60)
    safe_print("           测试结果汇总")
    safe_print("="*60)
    
    passed_count = sum(1 for _, result in test_results if result)
    total_count = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        safe_print(f"   {status} - {test_name}")
    
    safe_print(f"\n总计: {passed_count}/{total_count} 测试通过")
    
    if passed_count == total_count:
        safe_print("\n🎉 所有核心功能测试通过！")
        safe_print("系统核心组件工作正常，可以进行进一步开发。")
        return True
    else:
        safe_print(f"\n⚠️ {total_count - passed_count} 个测试失败")
        safe_print("请检查相关模块并修复问题。")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)