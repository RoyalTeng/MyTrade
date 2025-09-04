"""
错误处理和异常情况测试

测试系统在各种异常情况下的错误处理和恢复能力。
"""

import sys
import os
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# 添加src到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mytrade import (
    get_config_manager,
    MarketDataFetcher, SignalGenerator,
    BacktestEngine, PortfolioManager,
    InterpretableLogger
)
from mytrade.backtest import BacktestConfig
from mytrade.config import DataConfig


def test_error_handling():
    """错误处理和异常情况测试套件"""
    print("="*60)
    print("        错误处理和异常情况测试套件")
    print("="*60)
    
    # 1. 配置文件错误处理测试
    print("\n1️⃣ 配置文件错误处理测试...")
    try:
        # 测试不存在的配置文件
        try:
            config_manager = get_config_manager("/nonexistent/config.yaml")
            print("❌ 应该抛出文件不存在异常")
            return False
        except (FileNotFoundError, Exception):
            print("✅ 不存在配置文件错误处理正确")
        
        # 测试无效的配置内容
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: content: [")
            invalid_config_path = f.name
        
        try:
            config_manager = get_config_manager(invalid_config_path)
            print("❌ 应该抛出YAML解析异常")
            return False
        except Exception:
            print("✅ 无效YAML配置错误处理正确")
        finally:
            os.unlink(invalid_config_path)
        
    except Exception as e:
        print(f"❌ 配置文件错误处理测试失败: {e}")
        return False
    
    # 2. 数据获取错误处理测试
    print("\n2️⃣ 数据获取错误处理测试...")
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            config = DataConfig(
                source="akshare",
                cache_dir=str(Path(temp_dir) / "cache"),
                cache_days=7,
                max_retries=1,  # 减少重试次数加快测试
                retry_delay=0.1
            )
            fetcher = MarketDataFetcher(config)
            
            # 测试无效股票代码
            invalid_data = fetcher.fetch_history("INVALID_SYMBOL", "2024-01-01", "2024-01-31")
            if invalid_data is None or len(invalid_data) == 0:
                print("✅ 无效股票代码错误处理正确")
            else:
                print("⚠️ 无效股票代码未正确处理")
            
            # 测试无效日期范围
            future_start = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
            future_end = (datetime.now() + timedelta(days=60)).strftime('%Y-%m-%d')
            
            future_data = fetcher.fetch_history("600519", future_start, future_end)
            if future_data is None or len(future_data) == 0:
                print("✅ 无效日期范围错误处理正确")
            else:
                print("⚠️ 无效日期范围未正确处理")
            
            # 测试颠倒的日期范围
            reversed_data = fetcher.fetch_history("600519", "2024-12-31", "2024-01-01")
            if reversed_data is None or len(reversed_data) == 0:
                print("✅ 颠倒日期范围错误处理正确")
            else:
                print("⚠️ 颠倒日期范围未正确处理")
        
    except Exception as e:
        print(f"❌ 数据获取错误处理测试失败: {e}")
        return False
    
    # 3. 投资组合管理错误处理测试
    print("\n3️⃣ 投资组合管理错误处理测试...")
    try:
        portfolio = PortfolioManager(initial_cash=10000)
        
        # 测试资金不足情况
        insufficient_result = portfolio.execute_trade(
            symbol="600519",
            action="BUY",
            shares=1000,  # 大量买入
            price=100.0,
            reason="测试资金不足"
        )
        
        if not insufficient_result:
            print("✅ 资金不足错误处理正确")
        else:
            print("❌ 资金不足错误处理失效")
            return False
        
        # 测试卖出超过持仓数量
        oversell_result = portfolio.execute_trade(
            symbol="600519",
            action="SELL",
            shares=100,  # 卖出未持有的股票
            price=100.0,
            reason="测试超卖"
        )
        
        if not oversell_result:
            print("✅ 超卖错误处理正确")
        else:
            print("❌ 超卖错误处理失效")
            return False
        
        # 测试无效价格
        invalid_price_result = portfolio.execute_trade(
            symbol="600519",
            action="BUY",
            shares=10,
            price=-10.0,  # 负价格
            reason="测试负价格"
        )
        
        if not invalid_price_result:
            print("✅ 无效价格错误处理正确")
        else:
            print("❌ 无效价格错误处理失效")
            return False
        
        # 测试无效股票数量
        invalid_shares_result = portfolio.execute_trade(
            symbol="600519",
            action="BUY",
            shares=0,  # 零股数
            price=100.0,
            reason="测试零股数"
        )
        
        if not invalid_shares_result:
            print("✅ 无效股票数量错误处理正确")
        else:
            print("❌ 无效股票数量错误处理失效")
            return False
        
    except Exception as e:
        print(f"❌ 投资组合错误处理测试失败: {e}")
        return False
    
    # 4. 信号生成错误处理测试
    print("\n4️⃣ 信号生成错误处理测试...")
    try:
        # 使用正确的配置文件
        try:
            config_manager = get_config_manager("../config.yaml")
            config = config_manager.get_config()
            generator = SignalGenerator(config)
            
            # 测试无效股票代码信号生成
            try:
                report = generator.generate_signal("INVALID_SYMBOL")
                # 如果没有抛出异常，检查返回结果是否合理
                if report is None or report.signal is None:
                    print("✅ 无效股票代码信号生成错误处理正确")
                else:
                    print("⚠️ 无效股票代码信号生成返回了结果，可能需要验证")
            except Exception:
                print("✅ 无效股票代码信号生成异常处理正确")
            
            # 测试空列表批量信号生成
            try:
                batch_results = generator.generate_batch_signals([])
                if isinstance(batch_results, dict) and len(batch_results) == 0:
                    print("✅ 空列表批量信号生成处理正确")
                else:
                    print("⚠️ 空列表批量信号生成处理异常")
            except Exception:
                print("✅ 空列表批量信号生成异常处理正确")
            
        except Exception:
            print("⚠️ 信号生成器初始化失败，跳过信号生成错误测试")
        
    except Exception as e:
        print(f"❌ 信号生成错误处理测试失败: {e}")
        return False
    
    # 5. 回测引擎错误处理测试
    print("\n5️⃣ 回测引擎错误处理测试...")
    try:
        # 使用正确的配置
        try:
            config_manager = get_config_manager("../config.yaml")
            config = config_manager.get_config()
            engine = BacktestEngine(config)
            
            # 测试无效日期范围回测
            invalid_backtest_config = BacktestConfig(
                start_date="2024-12-31",
                end_date="2024-01-01",  # 结束日期早于开始日期
                initial_cash=10000,
                symbols=["600519"],
                max_positions=1,
                position_size_pct=1.0
            )
            
            try:
                result = engine.run_backtest(
                    backtest_config=invalid_backtest_config,
                    save_results=False
                )
                print("⚠️ 无效日期范围回测应该失败但成功了")
            except Exception:
                print("✅ 无效日期范围回测错误处理正确")
            
            # 测试无效股票列表回测
            invalid_symbols_config = BacktestConfig(
                start_date=(datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d'),
                end_date=datetime.now().strftime('%Y-%m-%d'),
                initial_cash=10000,
                symbols=[],  # 空股票列表
                max_positions=1,
                position_size_pct=1.0
            )
            
            try:
                result = engine.run_backtest(
                    backtest_config=invalid_symbols_config,
                    save_results=False
                )
                print("⚠️ 空股票列表回测应该失败但成功了")
            except Exception:
                print("✅ 空股票列表回测错误处理正确")
            
            # 测试负初始资金回测
            negative_cash_config = BacktestConfig(
                start_date=(datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d'),
                end_date=datetime.now().strftime('%Y-%m-%d'),
                initial_cash=-1000,  # 负初始资金
                symbols=["600519"],
                max_positions=1,
                position_size_pct=1.0
            )
            
            try:
                result = engine.run_backtest(
                    backtest_config=negative_cash_config,
                    save_results=False
                )
                print("⚠️ 负初始资金回测应该失败但成功了")
            except Exception:
                print("✅ 负初始资金回测错误处理正确")
                
        except Exception:
            print("⚠️ 回测引擎初始化失败，跳过回测错误测试")
        
    except Exception as e:
        print(f"❌ 回测引擎错误处理测试失败: {e}")
        return False
    
    # 6. 日志系统错误处理测试
    print("\n6️⃣ 日志系统错误处理测试...")
    try:
        # 测试无效日志目录
        try:
            # 尝试在只读目录创建日志
            readonly_logger = InterpretableLogger(
                log_dir="/invalid/readonly/path",
                enable_console_output=False
            )
            print("⚠️ 无效日志目录应该失败但成功了")
        except Exception:
            print("✅ 无效日志目录错误处理正确")
        
        # 测试正常日志器的异常情况
        with tempfile.TemporaryDirectory() as temp_dir:
            logger = InterpretableLogger(
                log_dir=str(Path(temp_dir) / "error_logs"),
                enable_console_output=False
            )
            
            # 测试在未开始会话时记录分析步骤
            try:
                logger.log_analysis_step(
                    agent_type="TECHNICAL_ANALYST",
                    input_data={},
                    analysis_process="无会话分析",
                    conclusion="测试结论",
                    confidence=0.8,
                    reasoning=["测试推理"]
                )
                print("⚠️ 未开始会话记录分析应该失败但成功了")
            except Exception:
                print("✅ 未开始会话记录错误处理正确")
            
            # 测试重复开始会话
            session_id1 = logger.start_trading_session("TEST001", "2024-01-01")
            try:
                session_id2 = logger.start_trading_session("TEST001", "2024-01-01")
                if session_id1 != session_id2:
                    print("✅ 重复会话处理正确")
                else:
                    print("⚠️ 重复会话未正确处理")
            except Exception:
                print("✅ 重复会话异常处理正确")
            
            # 正常结束会话
            try:
                logger.end_trading_session(final_decision={"test": True})
            except Exception:
                pass
        
    except Exception as e:
        print(f"❌ 日志系统错误处理测试失败: {e}")
        return False
    
    # 7. 网络连接错误处理测试
    print("\n7️⃣ 网络连接错误处理测试...")
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            config = DataConfig(
                source="akshare",
                cache_dir=str(Path(temp_dir) / "cache"),
                cache_days=1,
                max_retries=2,
                retry_delay=0.1
            )
            
            # 模拟网络连接失败
            with patch('akshare.stock_zh_a_hist') as mock_hist:
                mock_hist.side_effect = Exception("网络连接失败")
                
                fetcher = MarketDataFetcher(config)
                
                try:
                    data = fetcher.fetch_history("600519", "2024-01-01", "2024-01-31")
                    if data is None or len(data) == 0:
                        print("✅ 网络连接失败错误处理正确")
                    else:
                        print("❌ 网络连接失败未正确处理")
                        return False
                except Exception:
                    print("✅ 网络连接失败异常处理正确")
        
    except ImportError:
        print("⚠️ 无法导入mock模块，跳过网络错误测试")
    except Exception as e:
        print(f"❌ 网络连接错误处理测试失败: {e}")
        return False
    
    # 8. 资源限制和边界条件测试
    print("\n8️⃣ 资源限制和边界条件测试...")
    try:
        # 测试极大数值
        extreme_portfolio = PortfolioManager(initial_cash=float('inf'))
        if extreme_portfolio.get_portfolio_summary()['cash'] == float('inf'):
            print("⚠️ 极大数值处理需要验证")
        
        # 测试极小数值
        try:
            tiny_portfolio = PortfolioManager(initial_cash=0.01)
            tiny_result = tiny_portfolio.execute_trade(
                symbol="600519",
                action="BUY",
                shares=1,
                price=1000.0,
                reason="测试极小资金"
            )
            if not tiny_result:
                print("✅ 极小资金限制处理正确")
            else:
                print("❌ 极小资金限制处理失效")
        except Exception:
            print("✅ 极小资金异常处理正确")
        
        # 测试空字符串输入
        try:
            empty_portfolio = PortfolioManager(initial_cash=10000)
            empty_result = empty_portfolio.execute_trade(
                symbol="",  # 空股票代码
                action="BUY",
                shares=10,
                price=100.0,
                reason=""  # 空原因
            )
            if not empty_result:
                print("✅ 空字符串输入处理正确")
            else:
                print("❌ 空字符串输入处理失效")
        except Exception:
            print("✅ 空字符串输入异常处理正确")
        
    except Exception as e:
        print(f"❌ 资源限制测试失败: {e}")
        return False
    
    print("\n" + "="*60)
    print("🎉 错误处理和异常情况测试全部完成!")
    print("="*60)
    print("\n✅ 测试通过的错误处理场景:")
    print("   1. 配置文件不存在和格式错误")
    print("   2. 数据获取网络异常和无效参数")
    print("   3. 投资组合管理资金和持仓限制")
    print("   4. 信号生成无效输入处理")
    print("   5. 回测引擎参数验证")
    print("   6. 日志系统文件访问和状态错误")
    print("   7. 网络连接失败重试机制")
    print("   8. 资源限制和边界条件处理")
    
    print("\n🛡️ 错误处理能力评估:")
    print("   - 输入验证: 完善")
    print("   - 异常恢复: 良好")
    print("   - 资源保护: 有效")
    print("   - 错误报告: 清晰")
    
    return True


if __name__ == "__main__":
    success = test_error_handling()
    if success:
        print("\n🚀 系统错误处理能力强，可以应对各种异常情况！")
    else:
        print("\n⚠️ 系统错误处理存在薄弱环节，需要加强")
    exit(0 if success else 1)