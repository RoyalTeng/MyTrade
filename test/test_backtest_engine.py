"""
测试回测引擎功能
"""

import sys
import logging
from pathlib import Path
from datetime import datetime, timedelta

# 添加src到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mytrade.backtest import BacktestEngine, BacktestConfig
from mytrade.config import get_config_manager


def test_backtest_engine():
    """测试回测引擎功能"""
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("=== 测试回测引擎功能 ===")
    
    # 初始化配置（使用默认配置）
    config_manager = get_config_manager("../config.yaml")
    
    # 创建回测引擎
    backtest_engine = BacktestEngine()
    
    # 1. 测试简单回测配置
    print("\n1. 创建回测配置...")
    
    # 设置回测日期范围（最近一个月）
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)
    
    backtest_config = BacktestConfig(
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d"),
        initial_cash=100000.0,  # 10万初始资金
        commission_rate=0.001,
        slippage_rate=0.0005,
        symbols=["600519", "000001", "000002"],  # 测试几只股票
        max_positions=3,
        position_size_pct=0.3,  # 每个仓位30%
        rebalance_frequency="daily"
    )
    
    print(f"回测配置:")
    print(f"  时间范围: {backtest_config.start_date} 到 {backtest_config.end_date}")
    print(f"  初始资金: ${backtest_config.initial_cash:,.2f}")
    print(f"  股票池: {backtest_config.symbols}")
    print(f"  最大持仓数: {backtest_config.max_positions}")
    print(f"  单个仓位大小: {backtest_config.position_size_pct:.1%}")
    
    # 2. 检查引擎状态
    print("\n2. 检查引擎状态...")
    status = backtest_engine.get_current_status()
    print(f"引擎状态: {status}")
    
    # 3. 运行回测
    print("\n3. 运行回测...")
    try:
        result = backtest_engine.run_backtest(
            backtest_config=backtest_config,
            save_results=True,
            output_dir="test/backtest_results"
        )
        
        print(f"\n回测完成!")
        print(f"  运行时间: {result.duration_seconds:.2f} 秒")
        
        # 显示投资组合摘要
        summary = result.portfolio_summary
        print(f"\n投资组合摘要:")
        print(f"  初始资金: ${summary['initial_cash']:,.2f}")
        print(f"  期末现金: ${summary['current_cash']:,.2f}")
        print(f"  期末市值: ${summary['market_value']:,.2f}")
        print(f"  总资产: ${summary['total_value']:,.2f}")
        print(f"  总收益率: {summary['total_return']:.2%}")
        print(f"  持仓数量: {summary['num_positions']}")
        print(f"  交易次数: {summary['num_trades']}")
        
        # 显示绩效指标
        if result.performance_metrics:
            metrics = result.performance_metrics
            print(f"\n绩效指标:")
            for key, value in metrics.items():
                if isinstance(value, float):
                    if 'return' in key or 'ratio' in key:
                        print(f"  {key}: {value:.4f}")
                    elif 'drawdown' in key:
                        print(f"  {key}: {value:.2%}")
                    else:
                        print(f"  {key}: {value:.2f}")
                else:
                    print(f"  {key}: {value}")
        
        # 显示交易记录摘要
        if result.trade_history:
            print(f"\n交易记录摘要:")
            trades_df = pd.DataFrame(result.trade_history) if result.trade_history else pd.DataFrame()
            if not trades_df.empty:
                buy_trades = trades_df[trades_df['action'] == 'BUY']
                sell_trades = trades_df[trades_df['action'] == 'SELL']
                
                print(f"  买入交易: {len(buy_trades)} 笔")
                print(f"  卖出交易: {len(sell_trades)} 笔")
                
                if len(buy_trades) > 0:
                    print(f"  买入金额: ${buy_trades['total_amount'].sum():,.2f}")
                if len(sell_trades) > 0:
                    print(f"  卖出金额: ${abs(sell_trades['total_amount'].sum()):,.2f}")
        
        # 显示信号统计
        if result.signal_history:
            print(f"\n信号统计:")
            signals_df = pd.DataFrame(result.signal_history)
            if not signals_df.empty:
                action_counts = signals_df['action'].value_counts()
                print(f"  信号总数: {len(signals_df)}")
                for action, count in action_counts.items():
                    print(f"  {action}: {count}")
                
                avg_confidence = signals_df['confidence'].mean()
                print(f"  平均信心度: {avg_confidence:.2f}")
        
    except Exception as e:
        print(f"回测失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 4. 测试引擎状态
    print("\n4. 测试引擎状态...")
    final_status = backtest_engine.get_current_status()
    print(f"最终状态: {final_status}")
    
    # 5. 测试重置功能
    print("\n5. 测试重置功能...")
    backtest_engine.reset()
    reset_status = backtest_engine.get_current_status()
    print(f"重置后状态: {reset_status}")
    
    print("\n回测引擎测试完成!")


if __name__ == "__main__":
    # 导入pandas用于数据分析
    try:
        import pandas as pd
    except ImportError:
        print("需要安装pandas: pip install pandas")
        sys.exit(1)
    
    test_backtest_engine()