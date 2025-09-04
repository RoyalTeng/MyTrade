"""
交易信号生成模块 - TradingAgents集成
"""

from .signal_generator import SignalGenerator
from .mock_trading_agents import MockTradingAgents

__all__ = ["SignalGenerator", "MockTradingAgents"]