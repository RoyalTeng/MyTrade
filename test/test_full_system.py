"""
完整系统集成测试

测试所有模块的集成和协作功能。
"""

import sys
import logging
from pathlib import Path
from datetime import datetime, timedelta

# 添加src到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mytrade import (
    get_config_manager,
    MarketDataFetcher, SignalGenerator,
    BacktestEngine, PortfolioManager,
    InterpretableLogger
)
from mytrade.backtest import BacktestConfig
from mytrade.logging import AgentType


def test_full_system():
    """完整系统集成测试"""
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("="*60)
    print("           MyTrade 完整系统集成测试")
    print("="*60)
    
    # 1. 测试配置管理
    print("\n1️⃣ 测试配置管理...")
    try:
        config_manager = get_config_manager("../config.yaml")
        config = config_manager.get_config()
        print(f"✅ 配置加载成功")
        print(f"   数据源: {config.data.source}")
        print(f"   缓存目录: {config.data.cache_dir}")
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return
    
    # 2. 测试数据获取
    print("\n2️⃣ 测试数据获取...")
    try:
        fetcher = MarketDataFetcher(config.data)
        
        # 获取股票列表
        stock_list = fetcher.get_stock_list()
        print(f"✅ 获取股票列表成功: {len(stock_list)} 只股票")
        
        # 获取历史数据
        test_symbol = "600519"
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        data = fetcher.fetch_history(test_symbol, start_date, end_date)
        print(f"✅ 获取历史数据成功: {test_symbol}, {len(data)} 条记录")
        
        # 缓存信息
        cache_info = fetcher.get_cache_info()
        print(f"   缓存文件: {cache_info['file_count']} 个")
        print(f"   缓存大小: {cache_info['total_size_mb']:.1f} MB")
        
    except Exception as e:
        print(f"❌ 数据获取测试失败: {e}")
        return
    
    # 3. 测试信号生成
    print("\n3️⃣ 测试信号生成...")
    try:
        generator = SignalGenerator(config)
        
        # 健康检查
        health = generator.health_check()
        print(f"✅ 信号生成器健康检查: {health['status']}")
        
        # 生成单个信号
        report = generator.generate_signal(test_symbol)
        signal = report.signal
        print(f"✅ 单个信号生成成功: {signal.action} (置信度: {signal.confidence:.2f})")
        print(f"   原因: {signal.reason}")
        
        # 批量信号生成
        test_symbols = ["600519", "000001", "000002"]
        batch_results = generator.generate_batch_signals(test_symbols)
        print(f"✅ 批量信号生成成功: {len(batch_results)} 个结果")
        
        for symbol, report in batch_results.items():
            s = report.signal
            print(f"   {symbol}: {s.action} (置信度: {s.confidence:.2f})")
    
    except Exception as e:
        print(f"❌ 信号生成测试失败: {e}")
        return
    
    # 4. 测试投资组合管理
    print("\n4️⃣ 测试投资组合管理...")
    try:
        portfolio = PortfolioManager(initial_cash=100000, commission_rate=0.001)
        
        # 执行买入交易
        success = portfolio.execute_trade(
            symbol=test_symbol,
            action="BUY",
            shares=100,
            price=45.0,
            reason="测试买入"
        )
        print(f"✅ 买入交易执行: {'成功' if success else '失败'}")
        
        # 更新市值
        portfolio.update_market_values({test_symbol: 46.0})
        
        # 获取投资组合摘要
        summary = portfolio.get_portfolio_summary()
        print(f"✅ 投资组合管理正常")
        print(f"   总资产: ¥{summary['total_value']:,.2f}")
        print(f"   总收益率: {summary['total_return']:.2%}")
        print(f"   持仓数: {summary['num_positions']}")
        
    except Exception as e:
        print(f"❌ 投资组合管理测试失败: {e}")
        return
    
    # 5. 测试回测引擎
    print("\n5️⃣ 测试回测引擎...")
    try:
        engine = BacktestEngine(config)
        
        # 创建简单回测配置
        backtest_config = BacktestConfig(
            start_date=(datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d'),
            end_date=datetime.now().strftime('%Y-%m-%d'),
            initial_cash=50000,
            symbols=[test_symbol],
            max_positions=1,
            position_size_pct=0.5,
            rebalance_frequency="daily"
        )
        
        # 运行回测
        result = engine.run_backtest(
            backtest_config=backtest_config,
            save_results=False
        )
        
        print(f"✅ 回测执行成功")
        print(f"   运行时间: {result.duration_seconds:.1f} 秒")
        print(f"   总收益率: {result.portfolio_summary['total_return']:.2%}")
        print(f"   交易次数: {result.portfolio_summary['num_trades']}")
        
        if result.performance_metrics:
            metrics = result.performance_metrics
            if 'sharpe_ratio' in metrics:
                print(f"   夏普比率: {metrics['sharpe_ratio']:.2f}")
        
    except Exception as e:
        print(f"❌ 回测引擎测试失败: {e}")
        return
    
    # 6. 测试可解释性日志
    print("\n6️⃣ 测试可解释性日志...")
    try:
        logger = InterpretableLogger(
            log_dir="test/integration_logs",
            enable_console_output=False
        )
        
        # 开始会话
        session_id = logger.start_trading_session(
            symbol=test_symbol,
            date=datetime.now().strftime('%Y-%m-%d')
        )
        
        # 记录分析步骤
        logger.log_analysis_step(
            agent_type=AgentType.TECHNICAL_ANALYST,
            input_data={"test": "integration_test"},
            analysis_process="集成测试分析",
            conclusion="测试结论",
            confidence=0.8,
            reasoning=["测试推理1", "测试推理2"]
        )
        
        # 记录决策点
        logger.log_decision_point(
            context="集成测试决策",
            options=[{"action": "BUY"}, {"action": "HOLD"}],
            chosen_option={"action": "BUY"},
            rationale="测试决策理由",
            confidence=0.75
        )
        
        # 结束会话
        summary = logger.end_trading_session(
            final_decision={"action": "BUY", "volume": 100},
            performance_data={"test_mode": True}
        )
        
        print(f"✅ 可解释性日志测试成功")
        print(f"   会话ID: {summary['session_id']}")
        print(f"   分析步骤: {summary['total_analysis_steps']}")
        print(f"   决策点: {summary['total_decision_points']}")
        
    except Exception as e:
        print(f"❌ 可解释性日志测试失败: {e}")
        return
    
    # 7. 测试完整交易流程
    print("\n7️⃣ 测试完整交易流程...")
    try:
        # 创建新的组件实例
        flow_generator = SignalGenerator(config)
        flow_portfolio = PortfolioManager(initial_cash=100000)
        flow_logger = InterpretableLogger(
            log_dir="test/flow_logs",
            enable_console_output=False
        )
        
        # 开始交易会话
        session_id = flow_logger.start_trading_session(test_symbol, datetime.now().strftime('%Y-%m-%d'))
        
        # 生成信号
        report = flow_generator.generate_signal(test_symbol)
        signal = report.signal
        
        # 记录分析过程到日志
        for analysis in report.detailed_analyses:
            flow_logger.log_analysis_step(
                agent_type=AgentType.TECHNICAL_ANALYST,  # 简化使用
                input_data=analysis.get('input', {}),
                analysis_process=analysis.get('process', '流程测试'),
                conclusion=analysis.get('conclusion', '测试结论'),
                confidence=0.7,
                reasoning=[analysis.get('reason', '测试推理')]
            )
        
        # 执行交易
        if signal.action == "BUY" and signal.volume > 0:
            success = flow_portfolio.execute_trade(
                symbol=test_symbol,
                action=signal.action,
                shares=min(signal.volume, 100),  # 限制数量
                price=45.0,
                reason=signal.reason
            )
            
            # 记录交易决策
            flow_logger.log_decision_point(
                context="执行交易决策",
                options=[{"action": signal.action}],
                chosen_option={"action": signal.action, "executed": success},
                rationale=signal.reason,
                confidence=signal.confidence
            )
            
        # 结束流程
        final_summary = flow_portfolio.get_portfolio_summary()
        flow_logger.end_trading_session(
            final_decision={
                "action": signal.action,
                "executed": success,
                "portfolio_value": final_summary['total_value']
            }
        )
        
        print(f"✅ 完整交易流程测试成功")
        print(f"   信号: {signal.action} (置信度: {signal.confidence:.2f})")
        print(f"   执行: {'成功' if success else '失败'}")
        print(f"   账户总值: ¥{final_summary['total_value']:,.2f}")
        
    except Exception as e:
        print(f"❌ 完整交易流程测试失败: {e}")
        return
    
    # 测试总结
    print("\n" + "="*60)
    print("🎉 完整系统集成测试全部通过!")
    print("="*60)
    print("\n✅ 测试通过的功能:")
    print("   1. 配置管理和参数加载")
    print("   2. 数据获取和缓存机制")
    print("   3. 交易信号生成 (TradingAgents集成)")
    print("   4. 投资组合管理和交易执行")
    print("   5. 回测引擎和绩效分析")
    print("   6. 可解释性日志记录")
    print("   7. 端到端交易流程")
    
    print("\n📊 系统状态:")
    print(f"   数据源: {config.data.source}")
    print(f"   支持股票数: {len(stock_list)}")
    print(f"   模型配置: {config.trading_agents.model_fast}")
    print(f"   缓存文件: {cache_info['file_count']} 个")
    
    print("\n🚀 系统已准备就绪，可以开始正式使用!")


if __name__ == "__main__":
    test_full_system()