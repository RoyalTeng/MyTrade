"""
MyTrade CLI主程序

提供命令行接口来使用系统的各种功能。
"""

import click
import logging
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mytrade import (
    get_config, get_config_manager,
    MarketDataFetcher, SignalGenerator, 
    BacktestEngine, PortfolioManager,
    InterpretableLogger
)
from mytrade.backtest import BacktestConfig


@click.group()
@click.option('--config', '-c', default='config.yaml', help='配置文件路径')
@click.option('--verbose', '-v', is_flag=True, help='详细输出')
@click.option('--debug', is_flag=True, help='调试模式')
@click.pass_context
def cli(ctx, config, verbose, debug):
    """MyTrade - 基于TradingAgents的量化交易系统"""
    # 设置日志级别
    log_level = logging.DEBUG if debug else (logging.INFO if verbose else logging.WARNING)
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 初始化配置
    try:
        config_manager = get_config_manager(config)
        ctx.ensure_object(dict)
        ctx.obj['config_manager'] = config_manager
        ctx.obj['config'] = config_manager.get_config()
        
        if verbose:
            click.echo(f"配置文件加载成功: {config}")
            
    except Exception as e:
        click.echo(f"❌ 配置文件加载失败: {e}", err=True)
        sys.exit(1)


@cli.group()
@click.pass_context
def data(ctx):
    """数据管理相关命令"""
    pass


@data.command()
@click.argument('symbol')
@click.option('--days', '-d', default=30, help='获取天数')
@click.option('--force', '-f', is_flag=True, help='强制更新')
@click.pass_context
def fetch(ctx, symbol, days, force):
    """获取股票历史数据"""
    click.echo(f"📊 正在获取 {symbol} 最近 {days} 天的数据...")
    
    try:
        config = ctx.obj['config']
        fetcher = MarketDataFetcher(config.data)
        
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        data = fetcher.fetch_history(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            force_update=force
        )
        
        if not data.empty:
            click.echo(f"✅ 成功获取 {len(data)} 条记录")
            click.echo(f"时间范围: {data.index[0]} 到 {data.index[-1]}")
            click.echo(f"最新价格: {data['close'].iloc[-1]:.2f}")
            click.echo(f"期间涨跌幅: {((data['close'].iloc[-1] / data['close'].iloc[0] - 1) * 100):.2f}%")
        else:
            click.echo("⚠️ 未获取到数据")
            
    except Exception as e:
        click.echo(f"❌ 数据获取失败: {e}", err=True)


@data.command()
@click.pass_context
def stocks(ctx):
    """获取股票列表"""
    click.echo("📈 获取股票列表...")
    
    try:
        config = ctx.obj['config']
        fetcher = MarketDataFetcher(config.data)
        
        stock_list = fetcher.get_stock_list()
        
        if not stock_list.empty:
            click.echo(f"✅ 获取到 {len(stock_list)} 只股票")
            click.echo("\n前10只股票:")
            for _, row in stock_list.head(10).iterrows():
                click.echo(f"  {row.get('code', 'N/A')}: {row.get('name', 'N/A')}")
        else:
            click.echo("⚠️ 未获取到股票列表")
            
    except Exception as e:
        click.echo(f"❌ 获取股票列表失败: {e}", err=True)


@cli.group()
@click.pass_context
def signal(ctx):
    """信号生成相关命令"""
    pass


@signal.command()
@click.argument('symbol')
@click.option('--date', '-d', help='目标日期 (YYYY-MM-DD)')
@click.option('--lookback', default=30, help='回看天数')
@click.pass_context
def generate(ctx, symbol, date, lookback):
    """为指定股票生成交易信号"""
    click.echo(f"🧠 正在为 {symbol} 生成交易信号...")
    
    try:
        config = ctx.obj['config']
        generator = SignalGenerator(config)
        
        report = generator.generate_signal(
            symbol=symbol,
            target_date=date,
            lookback_days=lookback
        )
        
        signal = report.signal
        
        click.echo("\n=== 交易信号 ===")
        click.echo(f"股票代码: {signal.symbol}")
        click.echo(f"分析日期: {signal.date}")
        click.echo(f"交易动作: {signal.action}")
        click.echo(f"建议数量: {signal.volume}")
        click.echo(f"置信度: {signal.confidence:.2f}")
        click.echo(f"原因: {signal.reason}")
        
        if report.summary:
            click.echo(f"\n摘要: {report.summary}")
        
        if report.detailed_analyses:
            click.echo(f"\n=== 详细分析 ===")
            for i, analysis in enumerate(report.detailed_analyses, 1):
                agent_name = analysis.get('agent', f'分析师{i}')
                click.echo(f"\n{i}. {agent_name}")
                
                if 'analysis' in analysis:
                    for key, value in analysis['analysis'].items():
                        click.echo(f"   {key}: {value}")
                
                if 'conclusion' in analysis:
                    click.echo(f"   结论: {analysis['conclusion']}")
                    
    except Exception as e:
        click.echo(f"❌ 信号生成失败: {e}", err=True)


@signal.command()
@click.argument('symbols', nargs=-1, required=True)
@click.option('--date', '-d', help='目标日期 (YYYY-MM-DD)')
@click.pass_context
def batch(ctx, symbols, date):
    """批量生成交易信号"""
    symbol_list = list(symbols)
    click.echo(f"🔍 批量生成信号，股票数量: {len(symbol_list)}")
    
    try:
        config = ctx.obj['config']
        generator = SignalGenerator(config)
        
        results = generator.generate_batch_signals(
            symbols=symbol_list,
            target_date=date
        )
        
        click.echo("\n=== 批量信号结果 ===")
        click.echo(f"{'股票代码':<10} {'动作':<6} {'数量':<8} {'置信度':<8} {'原因'}")
        click.echo("-" * 60)
        
        for symbol, report in results.items():
            signal = report.signal
            click.echo(f"{symbol:<10} {signal.action:<6} {signal.volume:<8} {signal.confidence:<8.2f} {signal.reason[:20]}")
            
    except Exception as e:
        click.echo(f"❌ 批量信号生成失败: {e}", err=True)


@cli.group()
@click.pass_context
def backtest(ctx):
    """回测相关命令"""
    pass


@backtest.command()
@click.option('--start-date', required=True, help='开始日期 (YYYY-MM-DD)')
@click.option('--end-date', required=True, help='结束日期 (YYYY-MM-DD)')
@click.option('--symbols', required=True, help='股票代码列表，逗号分隔')
@click.option('--initial-cash', default=1000000.0, help='初始资金')
@click.option('--max-positions', default=10, help='最大持仓数')
@click.option('--position-size', default=0.1, help='单仓位大小比例')
@click.option('--frequency', default='daily', help='调仓频率 (daily/weekly/monthly)')
@click.option('--output-dir', help='输出目录')
@click.pass_context
def run(ctx, start_date, end_date, symbols, initial_cash, max_positions, position_size, frequency, output_dir):
    """运行回测"""
    symbol_list = [s.strip() for s in symbols.split(',')]
    
    click.echo("🚀 开始运行回测...")
    click.echo(f"时间范围: {start_date} 到 {end_date}")
    click.echo(f"股票池: {symbol_list}")
    click.echo(f"初始资金: ¥{initial_cash:,.2f}")
    
    try:
        config = ctx.obj['config']
        engine = BacktestEngine(config)
        
        backtest_config = BacktestConfig(
            start_date=start_date,
            end_date=end_date,
            initial_cash=initial_cash,
            symbols=symbol_list,
            max_positions=max_positions,
            position_size_pct=position_size,
            rebalance_frequency=frequency
        )
        
        result = engine.run_backtest(
            backtest_config=backtest_config,
            save_results=True,
            output_dir=output_dir or "logs/backtest"
        )
        
        # 显示结果摘要
        summary = result.portfolio_summary
        metrics = result.performance_metrics
        
        click.echo("\n=== 回测结果 ===")
        click.echo(f"总收益率: {summary['total_return']:.2%}")
        click.echo(f"期末总资产: ¥{summary['total_value']:,.2f}")
        click.echo(f"期末现金: ¥{summary['current_cash']:,.2f}")
        click.echo(f"期末市值: ¥{summary['market_value']:,.2f}")
        click.echo(f"交易次数: {summary['num_trades']}")
        click.echo(f"持仓数量: {summary['num_positions']}")
        
        if metrics:
            click.echo(f"\n=== 绩效指标 ===")
            if 'annual_return' in metrics:
                click.echo(f"年化收益率: {metrics['annual_return']:.2%}")
            if 'volatility' in metrics:
                click.echo(f"年化波动率: {metrics['volatility']:.2%}")
            if 'sharpe_ratio' in metrics:
                click.echo(f"夏普比率: {metrics['sharpe_ratio']:.2f}")
            if 'max_drawdown' in metrics:
                click.echo(f"最大回撤: {metrics['max_drawdown']:.2%}")
            if 'win_rate' in metrics:
                click.echo(f"胜率: {metrics['win_rate']:.2%}")
        
        click.echo(f"\n✅ 回测完成，运行时间: {result.duration_seconds:.1f}秒")
        click.echo(f"结果已保存到: logs/backtest/")
        
    except Exception as e:
        click.echo(f"❌ 回测失败: {e}", err=True)


@cli.group()
@click.pass_context
def system(ctx):
    """系统管理相关命令"""
    pass


@system.command()
@click.pass_context
def health(ctx):
    """系统健康检查"""
    click.echo("🏥 正在进行系统健康检查...")
    
    try:
        config = ctx.obj['config']
        
        # 检查信号生成器
        click.echo("\n📊 检查信号生成器...")
        generator = SignalGenerator(config)
        health_status = generator.health_check()
        
        overall_status = health_status.get('status', 'unknown')
        click.echo(f"整体状态: {'✅' if overall_status == 'healthy' else '⚠️'} {overall_status}")
        
        components = health_status.get('components', {})
        for component, status in components.items():
            component_status = status.get('status', 'unknown')
            icon = '✅' if component_status == 'healthy' else '❌'
            click.echo(f"  {component}: {icon} {component_status}")
            
            if 'error' in status:
                click.echo(f"    错误: {status['error']}")
            
            # 显示额外信息
            for key, value in status.items():
                if key not in ['status', 'error']:
                    click.echo(f"    {key}: {value}")
        
        # 检查配置
        click.echo(f"\n⚙️ 配置状态: ✅ 已加载")
        click.echo(f"  数据源: {config.data.source}")
        click.echo(f"  缓存目录: {config.data.cache_dir}")
        click.echo(f"  日志目录: {config.logging.dir}")
        
    except Exception as e:
        click.echo(f"❌ 健康检查失败: {e}", err=True)


@system.command()
@click.pass_context
def info(ctx):
    """显示系统信息"""
    click.echo("ℹ️ 系统信息")
    click.echo("=" * 50)
    
    # 版本信息
    try:
        from mytrade import __version__
        click.echo(f"版本: {__version__}")
    except ImportError:
        click.echo("版本: 开发版本")
    
    # 配置信息
    config = ctx.obj['config']
    click.echo(f"配置文件: {ctx.obj.get('config_file', 'config.yaml')}")
    click.echo(f"数据源: {config.data.source}")
    click.echo(f"模型配置: 快速模型={config.trading_agents.model_fast}, 深度模型={config.trading_agents.model_deep}")
    
    # Python环境
    click.echo(f"Python版本: {sys.version.split()[0]}")
    click.echo(f"运行目录: {Path.cwd()}")


@cli.command()
@click.option('--symbol', default='600519', help='测试股票代码')
@click.pass_context
def demo(ctx, symbol):
    """运行完整演示流程"""
    click.echo("🎬 开始演示完整交易流程...")
    click.echo(f"演示股票: {symbol}")
    
    try:
        config = ctx.obj['config']
        
        # 1. 获取数据
        click.echo("\n1️⃣ 获取市场数据...")
        fetcher = MarketDataFetcher(config.data)
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        data = fetcher.fetch_history(symbol, start_date, end_date)
        click.echo(f"✅ 获取到 {len(data)} 条历史数据")
        
        # 2. 生成信号
        click.echo("\n2️⃣ 生成交易信号...")
        generator = SignalGenerator(config)
        report = generator.generate_signal(symbol)
        
        signal = report.signal
        click.echo(f"✅ 信号生成完成: {signal.action} (置信度: {signal.confidence:.2f})")
        
        # 3. 模拟交易
        click.echo("\n3️⃣ 模拟交易执行...")
        portfolio = PortfolioManager(initial_cash=100000)
        
        if signal.action == "BUY" and signal.volume > 0:
            success = portfolio.execute_trade(
                symbol=symbol,
                action="BUY",
                shares=signal.volume,
                price=data['close'].iloc[-1],
                reason=signal.reason
            )
            if success:
                click.echo(f"✅ 买入成功: {signal.volume} 股")
            else:
                click.echo("❌ 买入失败")
        
        # 4. 显示结果
        click.echo("\n4️⃣ 交易结果...")
        summary = portfolio.get_portfolio_summary()
        click.echo(f"账户余额: ¥{summary['current_cash']:,.2f}")
        click.echo(f"持仓市值: ¥{summary['market_value']:,.2f}")
        click.echo(f"总资产: ¥{summary['total_value']:,.2f}")
        
        click.echo("\n🎉 演示完成!")
        
    except Exception as e:
        click.echo(f"❌ 演示失败: {e}", err=True)


if __name__ == '__main__':
    cli()