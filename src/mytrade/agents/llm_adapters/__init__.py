"""
LLM适配器模块

提供统一的LLM接口，支持多厂商LLM服务
参考TradingAgents-CN的适配器架构设计
"""

from .base_adapter import BaseLLMAdapter, LLMConfig, LLMResponse
from .openai_adapter import OpenAIAdapter
from .deepseek_adapter import DeepSeekAdapter
from .factory import LLMAdapterFactory

__all__ = [
    'BaseLLMAdapter',
    'LLMConfig',
    'LLMResponse',
    'OpenAIAdapter',
    'DeepSeekAdapter',
    'LLMAdapterFactory'
]