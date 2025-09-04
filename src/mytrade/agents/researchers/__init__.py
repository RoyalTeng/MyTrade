"""
研究员层 - TradingAgents企业级架构

实现Bull/Bear研究员对抗辩论机制
"""

from .bull_researcher import BullResearcher
from .bear_researcher import BearResearcher

__all__ = ['BullResearcher', 'BearResearcher']