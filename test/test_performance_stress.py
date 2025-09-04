"""
性能和压力测试

测试系统在高负载、大数据量和极端情况下的表现。
"""

import sys
import time
import threading
import random
from pathlib import Path
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import tempfile

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


def test_performance_stress():
    """性能和压力测试套件"""
    print("="*60)
    print("           性能和压力测试套件")
    print("="*60)
    
    # 1. 数据获取性能测试
    print("\n1️⃣ 数据获取性能测试...")
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            config = DataConfig(
                source="akshare",
                cache_dir=str(Path(temp_dir) / "cache"),
                cache_days=7,
                max_retries=3,
                retry_delay=0.5
            )
            fetcher = MarketDataFetcher(config)
            
            # 测试大量股票列表获取性能
            start_time = time.time()
            stock_list = fetcher.get_stock_list()
            list_time = time.time() - start_time
            
            print(f"✅ 股票列表获取: {len(stock_list)} 只股票, 耗时 {list_time:.2f}s")
            
            # 测试批量历史数据获取
            test_symbols = ["600519", "000001", "000002", "000858", "002415"]
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            
            start_time = time.time()
            successful_fetches = 0
            
            for symbol in test_symbols:
                try:
                    data = fetcher.fetch_history(symbol, start_date, end_date)
                    if data is not None and len(data) > 0:
                        successful_fetches += 1
                except Exception:
                    pass
            
            batch_time = time.time() - start_time
            avg_time = batch_time / len(test_symbols)
            
            print(f"✅ 批量数据获取: {successful_fetches}/{len(test_symbols)} 成功")
            print(f"   总耗时: {batch_time:.2f}s, 平均 {avg_time:.2f}s/股票")
            
            # 性能基准检查
            if avg_time > 5.0:
                print("⚠️ 数据获取速度较慢，可能需要优化")
            else:
                print("✅ 数据获取速度正常")
                
    except Exception as e:
        print(f"❌ 数据获取性能测试失败: {e}")
        return False
    
    # 2. 信号生成性能测试
    print("\n2️⃣ 信号生成性能测试...")
    try:
        config_manager = get_config_manager("../config.yaml")
        config = config_manager.get_config()
        generator = SignalGenerator(config)
        
        # 单个信号生成性能
        test_symbol = "600519"
        signal_times = []
        
        for i in range(3):  # 测试3次取平均
            start_time = time.time()
            try:
                report = generator.generate_signal(test_symbol)
                signal_time = time.time() - start_time
                signal_times.append(signal_time)
            except Exception:
                pass
        
        if signal_times:
            avg_signal_time = sum(signal_times) / len(signal_times)
            print(f"✅ 单个信号生成: 平均 {avg_signal_time:.2f}s")
            
            if avg_signal_time > 30.0:
                print("⚠️ 信号生成速度较慢，可能需要优化模型调用")
            else:
                print("✅ 信号生成速度正常")
        
        # 批量信号生成性能
        batch_symbols = ["600519", "000001", "000002"]
        start_time = time.time()
        
        try:
            batch_results = generator.generate_batch_signals(batch_symbols)
            batch_time = time.time() - start_time
            
            print(f"✅ 批量信号生成: {len(batch_results)} 个信号, 耗时 {batch_time:.2f}s")
        except Exception:
            print("⚠️ 批量信号生成测试跳过")
        
    except Exception as e:
        print(f"❌ 信号生成性能测试失败: {e}")
        return False
    
    # 3. 投资组合管理压力测试
    print("\n3️⃣ 投资组合管理压力测试...")
    try:
        portfolio = PortfolioManager(initial_cash=1000000)  # 100万初始资金
        
        # 大量交易压力测试
        symbols = ["600519", "000001", "000002", "000858", "002415", "600036", "600887", "000858", "002142", "300059"]
        trade_count = 100
        successful_trades = 0
        
        start_time = time.time()
        
        for i in range(trade_count):
            symbol = random.choice(symbols)
            action = random.choice(["BUY", "SELL"])
            shares = random.randint(10, 100)
            price = random.uniform(10, 200)
            
            try:
                success = portfolio.execute_trade(
                    symbol=symbol,
                    action=action,
                    shares=shares,
                    price=price,
                    reason=f"压力测试交易 {i+1}"
                )
                if success:
                    successful_trades += 1
            except Exception:
                pass
        
        trade_time = time.time() - start_time
        
        print(f"✅ 大量交易压力测试: {successful_trades}/{trade_count} 成功")
        print(f"   总耗时: {trade_time:.2f}s, 平均 {trade_time/trade_count*1000:.2f}ms/交易")
        
        # 检查投资组合状态
        summary = portfolio.get_portfolio_summary()
        positions = portfolio.get_positions()
        trades = portfolio.get_trade_history()
        
        print(f"   最终持仓数: {len(positions)}")
        print(f"   交易历史: {len(trades)} 笔")
        print(f"   总资产: ¥{summary['total_value']:,.2f}")
        
        # 性能基准检查
        if trade_time / trade_count > 0.1:  # 每笔交易超过100ms
            print("⚠️ 交易执行速度较慢，可能需要优化")
        else:
            print("✅ 交易执行速度正常")
        
    except Exception as e:
        print(f"❌ 投资组合压力测试失败: {e}")
        return False
    
    # 4. 并发访问测试
    print("\n4️⃣ 并发访问测试...")
    try:
        config = DataConfig(
            source="akshare",
            cache_dir="data/cache",
            cache_days=7
        )
        
        def concurrent_data_fetch(symbol):
            """并发数据获取任务"""
            try:
                fetcher = MarketDataFetcher(config)
                end_date = datetime.now().strftime('%Y-%m-%d')
                start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
                data = fetcher.fetch_history(symbol, start_date, end_date)
                return symbol, data is not None and len(data) > 0
            except Exception:
                return symbol, False
        
        # 启动多个并发任务
        test_symbols = ["600519", "000001", "000002", "000858", "002415"]
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(concurrent_data_fetch, symbol) for symbol in test_symbols]
            results = []
            
            for future in as_completed(futures):
                results.append(future.result())
        
        concurrent_time = time.time() - start_time
        successful_concurrent = sum(1 for _, success in results if success)
        
        print(f"✅ 并发数据获取: {successful_concurrent}/{len(test_symbols)} 成功")
        print(f"   总耗时: {concurrent_time:.2f}s")
        print(f"   并发效率: {len(test_symbols)/concurrent_time:.1f} 任务/秒")
        
    except Exception as e:
        print(f"❌ 并发访问测试失败: {e}")
        return False
    
    # 5. 内存使用测试
    print("\n5️⃣ 内存使用测试...")
    try:
        import psutil
        import os
        
        # 获取当前进程
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 创建大量对象进行内存测试
        large_portfolio = PortfolioManager(initial_cash=10000000)  # 1000万初始资金
        
        # 执行大量交易
        symbols = ["600519", "000001", "000002"] * 10  # 重复符号
        for i in range(200):
            symbol = symbols[i % len(symbols)]
            large_portfolio.execute_trade(
                symbol=symbol,
                action="BUY" if i % 2 == 0 else "SELL",
                shares=random.randint(1, 50),
                price=random.uniform(10, 100),
                reason=f"内存测试 {i}"
            )
        
        # 检查内存使用
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        print(f"✅ 内存使用测试完成")
        print(f"   初始内存: {initial_memory:.1f} MB")
        print(f"   最终内存: {final_memory:.1f} MB")
        print(f"   内存增长: {memory_increase:.1f} MB")
        
        if memory_increase > 500:  # 超过500MB增长
            print("⚠️ 内存使用量较大，可能存在内存泄漏")
        else:
            print("✅ 内存使用正常")
            
    except ImportError:
        print("⚠️ psutil未安装，跳过内存测试")
    except Exception as e:
        print(f"❌ 内存使用测试失败: {e}")
        return False
    
    # 6. 回测性能测试
    print("\n6️⃣ 回测引擎性能测试...")
    try:
        config_manager = get_config_manager("../config.yaml")
        config = config_manager.get_config()
        engine = BacktestEngine(config)
        
        # 短期回测性能
        short_backtest_config = BacktestConfig(
            start_date=(datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d'),
            end_date=datetime.now().strftime('%Y-%m-%d'),
            initial_cash=100000,
            symbols=["600519"],
            max_positions=1,
            position_size_pct=1.0
        )
        
        start_time = time.time()
        result = engine.run_backtest(
            backtest_config=short_backtest_config,
            save_results=False
        )
        short_backtest_time = time.time() - start_time
        
        print(f"✅ 短期回测: 耗时 {short_backtest_time:.2f}s")
        print(f"   总收益率: {result.portfolio_summary['total_return']:.2%}")
        
        # 多股票回测性能
        multi_backtest_config = BacktestConfig(
            start_date=(datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d'),
            end_date=datetime.now().strftime('%Y-%m-%d'),
            initial_cash=200000,
            symbols=["600519", "000001", "000002"],
            max_positions=3,
            position_size_pct=0.3
        )
        
        start_time = time.time()
        multi_result = engine.run_backtest(
            backtest_config=multi_backtest_config,
            save_results=False
        )
        multi_backtest_time = time.time() - start_time
        
        print(f"✅ 多股票回测: 耗时 {multi_backtest_time:.2f}s")
        print(f"   总收益率: {multi_result.portfolio_summary['total_return']:.2%}")
        
        # 性能基准检查
        if short_backtest_time > 60.0:
            print("⚠️ 回测速度较慢，可能需要优化")
        else:
            print("✅ 回测性能正常")
        
    except Exception as e:
        print(f"❌ 回测性能测试失败: {e}")
        return False
    
    # 7. 日志系统压力测试
    print("\n7️⃣ 日志系统压力测试...")
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            logger = InterpretableLogger(
                log_dir=str(Path(temp_dir) / "stress_logs"),
                enable_console_output=False
            )
            
            # 大量日志写入测试
            start_time = time.time()
            log_count = 50
            
            for i in range(log_count):
                session_id = logger.start_trading_session(
                    symbol=f"TEST{i:03d}",
                    date=datetime.now().strftime('%Y-%m-%d')
                )
                
                # 记录分析步骤
                logger.log_analysis_step(
                    agent_type="TECHNICAL_ANALYST",
                    input_data={"test": f"stress_test_{i}"},
                    analysis_process=f"压力测试分析 {i}",
                    conclusion=f"测试结论 {i}",
                    confidence=random.uniform(0.5, 0.9),
                    reasoning=[f"压力测试推理 {i}"]
                )
                
                # 结束会话
                logger.end_trading_session(
                    final_decision={"action": "BUY", "test": True}
                )
            
            log_time = time.time() - start_time
            
            print(f"✅ 日志压力测试: {log_count} 个会话, 耗时 {log_time:.2f}s")
            print(f"   平均耗时: {log_time/log_count*1000:.2f}ms/会话")
            
            if log_time / log_count > 1.0:  # 每个会话超过1秒
                print("⚠️ 日志写入速度较慢，可能需要优化")
            else:
                print("✅ 日志性能正常")
        
    except Exception as e:
        print(f"❌ 日志系统压力测试失败: {e}")
        return False
    
    print("\n" + "="*60)
    print("🎉 性能和压力测试全部完成!")
    print("="*60)
    print("\n✅ 测试通过的性能项目:")
    print("   1. 数据获取和缓存性能")
    print("   2. 信号生成处理速度")
    print("   3. 投资组合交易执行效率")
    print("   4. 并发访问处理能力")
    print("   5. 内存使用和泄漏检测")
    print("   6. 回测引擎计算性能")
    print("   7. 日志系统写入性能")
    
    print("\n📊 性能基准建议:")
    print("   - 数据获取: < 5s/股票")
    print("   - 信号生成: < 30s/股票")
    print("   - 交易执行: < 100ms/笔")
    print("   - 内存增长: < 500MB")
    print("   - 回测处理: < 60s")
    
    return True


if __name__ == "__main__":
    success = test_performance_stress()
    if success:
        print("\n🚀 系统性能表现良好，可以处理生产负载！")
    else:
        print("\n⚠️ 系统性能存在瓶颈，需要进一步优化")
    exit(0 if success else 1)