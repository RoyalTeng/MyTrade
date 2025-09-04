"""
交易信号生成器

封装TradingAgents多智能体框架，提供统一的信号生成接口。
"""

import logging
from typing import Dict, Any, Optional, Union
from datetime import datetime, date

import pandas as pd
from pydantic import BaseModel

from ..config import get_config
from ..data import MarketDataFetcher
from ..data.market_data_fetcher import DataSourceConfig
from .mock_trading_agents import MockTradingAgents


class TradingSignal(BaseModel):
    """交易信号数据结构"""
    symbol: str
    date: str
    action: str  # BUY, SELL, HOLD
    volume: int
    confidence: float
    reason: str
    timestamp: str


class AnalysisReport(BaseModel):
    """分析报告数据结构"""
    symbol: str
    date: str
    signal: TradingSignal
    detailed_analyses: list
    risk_assessment: dict
    summary: str
    timestamp: str


class SignalGenerator:
    """
    交易信号生成器
    
    功能：
    - 封装TradingAgents多智能体分析流程
    - 提供统一的信号生成接口
    - 支持批量信号生成
    - 处理数据获取和异常情况
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化信号生成器
        
        Args:
            config: 配置字典，如果为None则使用全局配置
        """
        self.config = config or get_config()
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # 初始化数据获取器
        data_config = DataSourceConfig(
            source=self.config.data.source,
            tushare_token=self.config.data.tushare_token,
            cache_dir=self.config.data.cache_dir
        )
        self.data_fetcher = MarketDataFetcher(data_config)
        
        # 初始化TradingAgents（这里使用模拟版本）
        trading_agents_config = {
            'model_fast': self.config.trading_agents.model_fast,
            'model_deep': self.config.trading_agents.model_deep,
            'use_online_data': self.config.trading_agents.use_online_data,
            'debate_rounds': self.config.trading_agents.debate_rounds,
            'openai_api_key': self.config.trading_agents.openai_api_key
        }
        
        # TODO: 在实际部署时，这里应该使用真实的TradingAgents
        # from tradingagents import TradingAgentsGraph
        # self.trading_agents = TradingAgentsGraph(config=trading_agents_config)
        
        self.trading_agents = MockTradingAgents(trading_agents_config)
        
        self.logger.info("SignalGenerator initialized")
    
    def generate_signal(
        self, 
        symbol: str, 
        target_date: Optional[Union[str, date]] = None,
        lookback_days: int = 30,
        force_update: bool = False
    ) -> AnalysisReport:
        """
        为指定股票生成交易信号
        
        Args:
            symbol: 股票代码
            target_date: 目标日期，默认为当前日期
            lookback_days: 回看天数，用于获取历史数据
            force_update: 是否强制更新数据
        
        Returns:
            分析报告对象
        """
        if target_date is None:
            target_date = datetime.now().date()
        elif isinstance(target_date, str):
            target_date = datetime.strptime(target_date, "%Y-%m-%d").date()
        
        target_date_str = target_date.strftime("%Y-%m-%d")
        
        self.logger.info(f"Generating signal for {symbol} on {target_date_str}")
        
        try:
            # 获取历史数据
            end_date = target_date_str
            start_date = (target_date - pd.Timedelta(days=lookback_days*2)).strftime("%Y-%m-%d")  # 多取一些数据确保够用
            
            market_data = self.data_fetcher.fetch_history(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                force_update=force_update
            )
            
            if market_data.empty:
                raise ValueError(f"No market data available for {symbol}")
            
            # 确保有足够的数据
            if len(market_data) < 5:
                self.logger.warning(f"Limited data for {symbol}: {len(market_data)} records")
            
            # 使用TradingAgents进行分析
            analysis_result = self.trading_agents.run_analysis(
                symbol=symbol,
                market_data=market_data,
                target_date=target_date_str
            )
            
            if 'error' in analysis_result:
                raise ValueError(f"TradingAgents analysis failed: {analysis_result['error']}")
            
            # 构建交易信号
            signal_data = analysis_result.get('signal', {})
            signal = TradingSignal(
                symbol=symbol,
                date=target_date_str,
                action=signal_data.get('action', 'HOLD'),
                volume=signal_data.get('volume', 0),
                confidence=signal_data.get('confidence', 0.5),
                reason=signal_data.get('reason', 'No clear signal'),
                timestamp=analysis_result.get('timestamp', datetime.now().isoformat())
            )
            
            # 构建分析报告
            report = AnalysisReport(
                symbol=symbol,
                date=target_date_str,
                signal=signal,
                detailed_analyses=analysis_result.get('detailed_analyses', []),
                risk_assessment=analysis_result.get('risk_assessment', {}),
                summary=analysis_result.get('summary', ''),
                timestamp=analysis_result.get('timestamp', datetime.now().isoformat())
            )
            
            self.logger.info(f"Signal generated: {symbol} -> {signal.action} (confidence: {signal.confidence:.2f})")
            return report
            
        except Exception as e:
            self.logger.error(f"Failed to generate signal for {symbol}: {e}")
            
            # 返回默认的HOLD信号
            signal = TradingSignal(
                symbol=symbol,
                date=target_date_str,
                action='HOLD',
                volume=0,
                confidence=0.0,
                reason=f'Signal generation failed: {str(e)}',
                timestamp=datetime.now().isoformat()
            )
            
            report = AnalysisReport(
                symbol=symbol,
                date=target_date_str,
                signal=signal,
                detailed_analyses=[],
                risk_assessment={},
                summary=f'Analysis failed: {str(e)}',
                timestamp=datetime.now().isoformat()
            )
            
            return report
    
    def generate_batch_signals(
        self, 
        symbols: list, 
        target_date: Optional[Union[str, date]] = None,
        max_concurrent: int = 3
    ) -> Dict[str, AnalysisReport]:
        """
        批量生成交易信号
        
        Args:
            symbols: 股票代码列表
            target_date: 目标日期
            max_concurrent: 最大并发数（暂未实现并发）
        
        Returns:
            股票代码到分析报告的映射
        """
        self.logger.info(f"Generating batch signals for {len(symbols)} symbols")
        
        results = {}
        for i, symbol in enumerate(symbols, 1):
            self.logger.info(f"Processing {i}/{len(symbols)}: {symbol}")
            
            try:
                report = self.generate_signal(symbol, target_date)
                results[symbol] = report
            except Exception as e:
                self.logger.error(f"Failed to generate signal for {symbol}: {e}")
                # 即使失败也要记录结果
                signal = TradingSignal(
                    symbol=symbol,
                    date=target_date.strftime("%Y-%m-%d") if target_date else datetime.now().strftime("%Y-%m-%d"),
                    action='HOLD',
                    volume=0,
                    confidence=0.0,
                    reason=f'Batch processing failed: {str(e)}',
                    timestamp=datetime.now().isoformat()
                )
                
                results[symbol] = AnalysisReport(
                    symbol=symbol,
                    date=signal.date,
                    signal=signal,
                    detailed_analyses=[],
                    risk_assessment={},
                    summary=f'Batch analysis failed: {str(e)}',
                    timestamp=datetime.now().isoformat()
                )
        
        self.logger.info(f"Batch signal generation completed: {len(results)} results")
        return results
    
    def get_signal_history(self, symbol: str, days: int = 30) -> list:
        """
        获取信号历史记录（模拟实现）
        
        Args:
            symbol: 股票代码
            days: 查询天数
        
        Returns:
            历史信号列表
        """
        # 这里应该从数据库或文件中读取历史信号
        # 暂时返回空列表
        self.logger.info(f"Getting signal history for {symbol} (last {days} days)")
        return []
    
    def update_model_config(self, config_updates: Dict[str, Any]) -> None:
        """
        更新模型配置
        
        Args:
            config_updates: 配置更新字典
        """
        try:
            # 更新TradingAgents配置
            if hasattr(self.trading_agents, 'update_config'):
                self.trading_agents.update_config(config_updates)
            
            self.logger.info("Model configuration updated")
            
        except Exception as e:
            self.logger.error(f"Failed to update model configuration: {e}")
            raise
    
    def get_supported_symbols(self) -> list:
        """
        获取支持的股票代码列表
        
        Returns:
            股票代码列表
        """
        try:
            stock_list = self.data_fetcher.get_stock_list()
            if not stock_list.empty and 'code' in stock_list.columns:
                return stock_list['code'].tolist()[:100]  # 返回前100只作为示例
            else:
                # 返回一些常见股票代码作为示例
                return [
                    '600519', '000001', '000002', '600036', '000858',
                    '600000', '000166', '600519', '002415', '000568'
                ]
        except Exception as e:
            self.logger.warning(f"Failed to get stock list: {e}")
            return []
    
    def health_check(self) -> Dict[str, Any]:
        """
        健康检查
        
        Returns:
            健康状态字典
        """
        status = {
            'status': 'healthy',
            'components': {},
            'timestamp': datetime.now().isoformat()
        }
        
        # 检查数据获取器
        try:
            cache_info = self.data_fetcher.get_cache_info()
            status['components']['data_fetcher'] = {
                'status': 'healthy',
                'cache_files': cache_info['file_count'],
                'cache_size_mb': cache_info['total_size_mb']
            }
        except Exception as e:
            status['components']['data_fetcher'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
            status['status'] = 'degraded'
        
        # 检查TradingAgents
        try:
            # 简单的健康检查
            if hasattr(self.trading_agents, 'health_check'):
                ta_status = self.trading_agents.health_check()
            else:
                ta_status = {'status': 'healthy'}
                
            status['components']['trading_agents'] = ta_status
        except Exception as e:
            status['components']['trading_agents'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
            status['status'] = 'degraded'
        
        return status