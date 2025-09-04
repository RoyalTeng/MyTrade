"""
LLM适配器工厂

统一创建和管理各种LLM适配器
参考TradingAgents-CN的工厂模式设计
"""

import os
from typing import Dict, Type, Optional
import logging
from .base_adapter import BaseLLMAdapter, LLMConfig
from .openai_adapter import OpenAIAdapter
from .deepseek_adapter import DeepSeekAdapter


class LLMAdapterFactory:
    """LLM适配器工厂"""
    
    # 注册的适配器类型
    _adapters: Dict[str, Type[BaseLLMAdapter]] = {
        'deepseek': DeepSeekAdapter,  # DeepSeek官方API
        'openai': OpenAIAdapter,
        'openrouter': OpenAIAdapter,  # OpenRouter使用OpenAI兼容接口
        'siliconflow': OpenAIAdapter,  # SiliconFlow使用OpenAI兼容接口
    }
    
    # 默认配置
    _default_configs = {
        'deepseek': {
            'base_url': 'https://api.deepseek.com/v1',
            'model': 'deepseek-chat'
        },
        'openai': {
            'base_url': 'https://api.openai.com/v1',
            'model': 'gpt-3.5-turbo'
        },
        'openrouter': {
            'base_url': 'https://openrouter.ai/api/v1',
            'model': 'openai/gpt-3.5-turbo'
        },
        'siliconflow': {
            'base_url': 'https://api.siliconflow.cn/v1',
            'model': 'Qwen/Qwen2.5-7B-Instruct'
        }
    }
    
    @classmethod
    def create_adapter(cls, provider: str, **kwargs) -> BaseLLMAdapter:
        """创建LLM适配器
        
        Args:
            provider: LLM服务提供商名称
            **kwargs: 配置参数
            
        Returns:
            BaseLLMAdapter: LLM适配器实例
        """
        if provider not in cls._adapters:
            raise ValueError(f"不支持的LLM提供商: {provider}. 支持的提供商: {list(cls._adapters.keys())}")
        
        # 获取默认配置
        default_config = cls._default_configs.get(provider, {})
        
        # 合并配置，并转换字段名
        config_dict = {
            'provider': provider,
            **default_config
        }
        
        # 处理kwargs中的字段名转换
        for key, value in kwargs.items():
            if key == 'llm_max_tokens':
                config_dict['max_tokens'] = value
            elif key == 'llm_temperature':
                config_dict['temperature'] = value  
            elif key == 'llm_model':
                config_dict['model'] = value
            elif key == 'llm_provider':
                # 已经在上面设置了，跳过
                continue
            else:
                config_dict[key] = value
        
        # 自动获取API密钥
        if not config_dict.get('api_key'):
            config_dict['api_key'] = cls._get_api_key(provider)
        
        # 创建配置对象
        config = LLMConfig(**config_dict)
        
        # 创建适配器
        adapter_class = cls._adapters[provider]
        adapter = adapter_class(config)
        
        logging.info(f"已创建 {provider} 适配器: {config.model}")
        return adapter
    
    @classmethod
    def _get_api_key(cls, provider: str) -> Optional[str]:
        """自动获取API密钥"""
        key_mappings = {
            'deepseek': ['DEEPSEEK_API_KEY'],
            'openai': ['OPENAI_API_KEY'],
            'openrouter': ['OPENROUTER_API_KEY', 'OPENAI_API_KEY'],
            'siliconflow': ['SILICONFLOW_API_KEY']
        }
        
        keys = key_mappings.get(provider, [])
        for key in keys:
            value = os.getenv(key)
            if value:
                return value
        
        logging.warning(f"未找到 {provider} 的API密钥，需要手动设置")
        return None
    
    @classmethod
    def register_adapter(cls, provider: str, adapter_class: Type[BaseLLMAdapter]):
        """注册新的适配器类型"""
        cls._adapters[provider] = adapter_class
        logging.info(f"已注册新的适配器: {provider}")
    
    @classmethod
    def list_providers(cls) -> list:
        """列出支持的提供商"""
        return list(cls._adapters.keys())
    
    @classmethod
    def create_from_config(cls, config_dict: Dict) -> BaseLLMAdapter:
        """从配置字典创建适配器"""
        provider = config_dict.get('provider')
        if not provider:
            raise ValueError("配置中缺少provider字段")
        
        # 创建配置副本，移除provider以避免重复
        config_copy = config_dict.copy()
        config_copy.pop('provider', None)
        
        return cls.create_adapter(provider, **config_copy)