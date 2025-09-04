"""
回测引擎

协调信号生成、投资组合管理和交易执行，提供完整的回测功能。
"""

import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from pathlib import Path
import json

import pandas as pd
from pydantic import BaseModel

from .portfolio_manager import PortfolioManager, TradeRecord
from ..trading.signal_generator import SignalGenerator, AnalysisReport
from ..config import get_config


class BacktestConfig(BaseModel):
    """回测配置"""
    start_date: str
    end_date: str
    initial_cash: float = 1000000.0
    commission_rate: float = 0.001
    slippage_rate: float = 0.0005
    symbols: List[str] = []
    max_positions: int = 10
    position_size_pct: float = 0.1  # 每个仓位占总资金的比例
    rebalance_frequency: str = "daily"  # daily, weekly, monthly


class BacktestResult(BaseModel):
    """回测结果"""
    config: BacktestConfig
    portfolio_summary: Dict[str, Any]
    performance_metrics: Dict[str, float]
    trade_history: List[Dict[str, Any]]
    daily_values: List[Dict[str, Any]]
    signal_history: List[Dict[str, Any]]
    start_time: str
    end_time: str
    duration_seconds: float


class BacktestEngine:
    """
    回测引擎
    
    功能：
    - 协调信号生成和投资组合管理
    - 执行完整的回测流程
    - 生成回测报告和分析结果
    - 支持不同的回测策略和参数
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化回测引擎
        
        Args:
            config: 配置字典，如果为None则使用全局配置
        """
        self.config = config or get_config()
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # 初始化组件
        self.signal_generator = SignalGenerator(config)
        self.portfolio_manager: Optional[PortfolioManager] = None
        
        # 回测状态
        self.current_backtest: Optional[BacktestResult] = None
        self.is_running = False
        
        self.logger.info("BacktestEngine initialized")
    
    def run_backtest(
        self, 
        backtest_config: Union[BacktestConfig, Dict[str, Any]],
        save_results: bool = True,
        output_dir: Optional[str] = None
    ) -> BacktestResult:
        """
        运行回测
        
        Args:
            backtest_config: 回测配置
            save_results: 是否保存结果到文件
            output_dir: 输出目录，默认为logs/backtest/
        
        Returns:
            回测结果对象
        """
        if isinstance(backtest_config, dict):
            backtest_config = BacktestConfig(**backtest_config)
        
        start_time = datetime.now()
        self.is_running = True
        
        self.logger.info(f"Starting backtest: {backtest_config.start_date} to {backtest_config.end_date}")
        
        try:
            # 初始化投资组合管理器
            self.portfolio_manager = PortfolioManager(
                initial_cash=backtest_config.initial_cash,
                commission_rate=backtest_config.commission_rate,
                slippage_rate=backtest_config.slippage_rate
            )
            
            # 生成交易日历
            trade_dates = self._generate_trade_dates(
                backtest_config.start_date, 
                backtest_config.end_date,
                backtest_config.rebalance_frequency
            )
            
            signal_history = []
            
            # 逐日执行回测
            for i, trade_date in enumerate(trade_dates):
                self.logger.info(f"Processing {trade_date} ({i+1}/{len(trade_dates)})")
                
                try:
                    # 生成当日信号
                    daily_signals = self._generate_daily_signals(
                        backtest_config.symbols, 
                        trade_date
                    )
                    
                    # 记录信号历史
                    for signal_report in daily_signals.values():
                        signal_history.append({
                            'date': trade_date,
                            'symbol': signal_report.symbol,
                            'action': signal_report.signal.action,
                            'volume': signal_report.signal.volume,
                            'confidence': signal_report.signal.confidence,
                            'reason': signal_report.signal.reason
                        })
                    
                    # 执行交易决策
                    self._execute_trading_decisions(
                        daily_signals, 
                        backtest_config,
                        trade_date
                    )
                    
                    # 更新投资组合市值
                    self._update_portfolio_values(
                        backtest_config.symbols, 
                        trade_date
                    )
                    
                except Exception as e:
                    self.logger.error(f"Error processing {trade_date}: {e}")
                    continue
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # 生成回测结果
            result = BacktestResult(
                config=backtest_config,
                portfolio_summary=self.portfolio_manager.get_portfolio_summary(),
                performance_metrics=self.portfolio_manager.calculate_performance_metrics(),
                trade_history=self.portfolio_manager.get_trade_history(),
                daily_values=self.portfolio_manager.daily_values,
                signal_history=signal_history,
                start_time=start_time.isoformat(),
                end_time=end_time.isoformat(),
                duration_seconds=duration
            )
            
            self.current_backtest = result
            
            # 保存结果
            if save_results:
                self._save_backtest_results(result, output_dir)
            
            self.logger.info(f"Backtest completed in {duration:.2f} seconds")
            self.logger.info(f"Total return: {result.performance_metrics.get('total_return', 0):.2%}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Backtest failed: {e}")
            raise
        finally:
            self.is_running = False
    
    def _generate_trade_dates(
        self, 
        start_date: str, 
        end_date: str, 
        frequency: str
    ) -> List[str]:
        """生成交易日期列表"""
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        dates = []
        current = start
        
        if frequency == "daily":
            while current <= end:
                # 跳过周末（简化处理，实际应该使用交易日历）
                if current.weekday() < 5:  # 0-4是周一到周五
                    dates.append(current.strftime("%Y-%m-%d"))
                current += timedelta(days=1)
        elif frequency == "weekly":
            while current <= end:
                if current.weekday() == 0:  # 周一
                    dates.append(current.strftime("%Y-%m-%d"))
                current += timedelta(days=1)
        elif frequency == "monthly":
            while current <= end:
                if current.day == 1:  # 每月1号
                    dates.append(current.strftime("%Y-%m-%d"))
                # 移动到下个月
                if current.month == 12:
                    current = current.replace(year=current.year + 1, month=1)
                else:
                    current = current.replace(month=current.month + 1)
        
        return dates
    
    def _generate_daily_signals(
        self, 
        symbols: List[str], 
        trade_date: str
    ) -> Dict[str, AnalysisReport]:
        """生成当日所有股票的交易信号"""
        try:
            return self.signal_generator.generate_batch_signals(
                symbols=symbols,
                target_date=trade_date
            )
        except Exception as e:
            self.logger.error(f"Failed to generate signals for {trade_date}: {e}")
            return {}
    
    def _execute_trading_decisions(
        self, 
        signals: Dict[str, AnalysisReport],
        config: BacktestConfig,
        trade_date: str
    ) -> None:
        """根据信号执行交易决策"""
        if not self.portfolio_manager:
            return
        
        # 获取当前持仓
        current_positions = self.portfolio_manager.get_positions()
        
        # 处理卖出信号
        for symbol, report in signals.items():
            signal = report.signal
            
            if signal.action == "SELL" and symbol in current_positions:
                position = current_positions[symbol]
                shares_to_sell = min(signal.volume, position['shares'])
                
                if shares_to_sell > 0:
                    success = self.portfolio_manager.execute_trade(
                        symbol=symbol,
                        action="SELL",
                        shares=shares_to_sell,
                        price=self._get_execution_price(symbol, trade_date),
                        timestamp=trade_date,
                        reason=signal.reason
                    )
                    
                    if success:
                        self.logger.info(f"SELL executed: {shares_to_sell} shares of {symbol}")
        
        # 处理买入信号
        buy_signals = [(symbol, report) for symbol, report in signals.items() 
                      if report.signal.action == "BUY"]
        
        # 按信心度排序
        buy_signals.sort(key=lambda x: x[1].signal.confidence, reverse=True)
        
        # 限制最大持仓数量
        current_position_count = len(current_positions)
        
        for symbol, report in buy_signals:
            if current_position_count >= config.max_positions:
                break
                
            signal = report.signal
            
            # 计算买入金额
            available_cash = self.portfolio_manager.cash
            position_value = available_cash * config.position_size_pct
            execution_price = self._get_execution_price(symbol, trade_date)
            
            if execution_price > 0 and position_value > execution_price * 100:  # 至少买100股
                shares_to_buy = int(position_value / execution_price / 100) * 100  # 整百股
                
                success = self.portfolio_manager.execute_trade(
                    symbol=symbol,
                    action="BUY",
                    shares=shares_to_buy,
                    price=execution_price,
                    timestamp=trade_date,
                    reason=signal.reason
                )
                
                if success:
                    self.logger.info(f"BUY executed: {shares_to_buy} shares of {symbol}")
                    current_position_count += 1
    
    def _get_execution_price(self, symbol: str, date: str) -> float:
        """获取执行价格（简化实现，使用收盘价）"""
        try:
            # 这里应该获取实际的价格数据
            # 暂时使用模拟价格
            import random
            base_price = 10.0
            if symbol.startswith('60'):
                base_price = 20.0
            elif symbol.startswith('00'):
                base_price = 15.0
            
            # 添加一些随机波动
            return base_price * (0.9 + random.random() * 0.2)
            
        except Exception as e:
            self.logger.warning(f"Failed to get price for {symbol}: {e}")
            return 10.0  # 默认价格
    
    def _update_portfolio_values(self, symbols: List[str], date: str) -> None:
        """更新投资组合市值"""
        if not self.portfolio_manager:
            return
        
        # 构建价格数据
        price_data = {}
        for symbol in symbols:
            price_data[symbol] = self._get_execution_price(symbol, date)
        
        self.portfolio_manager.update_market_values(price_data, date)
    
    def _save_backtest_results(
        self, 
        result: BacktestResult, 
        output_dir: Optional[str] = None
    ) -> None:
        """保存回测结果到文件"""
        if output_dir is None:
            output_dir = "logs/backtest"
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"backtest_{timestamp}.json"
        
        # 保存JSON结果
        result_file = output_path / filename
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result.dict(), f, indent=2, ensure_ascii=False)
        
        # 保存CSV格式的交易记录
        if result.trade_history:
            trade_df = pd.DataFrame(result.trade_history)
            trade_csv = output_path / f"trades_{timestamp}.csv"
            trade_df.to_csv(trade_csv, index=False, encoding='utf-8')
        
        # 保存CSV格式的净值曲线
        if result.daily_values:
            value_df = pd.DataFrame(result.daily_values)
            value_csv = output_path / f"daily_values_{timestamp}.csv"
            value_df.to_csv(value_csv, index=False, encoding='utf-8')
        
        self.logger.info(f"Backtest results saved to {result_file}")
    
    def get_current_status(self) -> Dict[str, Any]:
        """获取当前状态"""
        return {
            'is_running': self.is_running,
            'has_results': self.current_backtest is not None,
            'portfolio_manager': self.portfolio_manager is not None
        }
    
    def stop_backtest(self) -> None:
        """停止当前回测（如果正在运行）"""
        if self.is_running:
            self.is_running = False
            self.logger.info("Backtest stop requested")
    
    def reset(self) -> None:
        """重置引擎状态"""
        self.portfolio_manager = None
        self.current_backtest = None
        self.is_running = False
        self.logger.info("BacktestEngine reset")