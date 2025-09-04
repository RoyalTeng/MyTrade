"""
MyTrade - 基于 TradingAgents 的量化交易系统

一个本地部署的智能量化交易系统，利用TradingAgents多智能体LLM框架
为A股市场进行分析和交易决策。
"""

from .config import get_config, get_config_manager
from .data import MarketDataFetcher
from .trading import SignalGenerator
from .backtest import BacktestEngine, PortfolioManager
from .logging import InterpretableLogger
from .cli import cli

__version__ = "0.1.0"
__author__ = "MyTrade Team"
__email__ = "team@mytrade.com"

__all__ = [
    "get_config",
    "get_config_manager", 
    "MarketDataFetcher",
    "SignalGenerator",
    "BacktestEngine",
    "PortfolioManager",
    "InterpretableLogger",
    "cli"
]