"""
OpenAI LLM适配器

支持OpenAI官方API及兼容API服务
参考TradingAgents-CN的OpenAI适配器实现
"""

import openai
from typing import List, Dict, Any
import time
import logging
from .base_adapter import BaseLLMAdapter, LLMResponse, LLMConfig


class OpenAIAdapter(BaseLLMAdapter):
    """OpenAI适配器"""
    
    def _initialize_client(self):
        """初始化OpenAI客户端"""
        self.validate_config()
        
        kwargs = {
            'api_key': self.config.api_key
        }
        
        if self.config.base_url:
            kwargs['base_url'] = self.config.base_url
            
        self.client = openai.OpenAI(**kwargs)
        logging.info(f"OpenAI客户端初始化成功: {self.config.model}")
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """聊天接口"""
        try:
            # 合并配置参数
            params = {
                'model': self.config.model,
                'messages': messages,
                'temperature': kwargs.get('temperature', self.config.temperature),
                'max_tokens': kwargs.get('max_tokens', self.config.max_tokens),
                'timeout': kwargs.get('timeout', self.config.timeout)
            }
            
            # 添加额外参数
            if self.config.extra_params:
                params.update(self.config.extra_params)
            
            # 调用API
            response = self.client.chat.completions.create(**params)
            
            # 解析响应
            return LLMResponse(
                content=response.choices[0].message.content,
                usage=response.usage.model_dump() if response.usage else None,
                model=response.model,
                finish_reason=response.choices[0].finish_reason,
                metadata={'response_time': time.time()}
            )
            
        except Exception as e:
            logging.error(f"OpenAI API调用失败: {e}")
            raise
    
    def chat_with_tools(self, messages: List[Dict[str, str]], tools: List[Dict[str, Any]], **kwargs) -> LLMResponse:
        """带工具的聊天接口"""
        try:
            params = {
                'model': self.config.model,
                'messages': messages,
                'tools': tools,
                'tool_choice': kwargs.get('tool_choice', 'auto'),
                'temperature': kwargs.get('temperature', self.config.temperature),
                'max_tokens': kwargs.get('max_tokens', self.config.max_tokens),
                'timeout': kwargs.get('timeout', self.config.timeout)
            }
            
            if self.config.extra_params:
                params.update(self.config.extra_params)
            
            response = self.client.chat.completions.create(**params)
            
            return LLMResponse(
                content=response.choices[0].message.content,
                usage=response.usage.model_dump() if response.usage else None,
                model=response.model,
                finish_reason=response.choices[0].finish_reason,
                metadata={
                    'response_time': time.time(),
                    'tool_calls': response.choices[0].message.tool_calls
                }
            )
            
        except Exception as e:
            logging.error(f"OpenAI工具调用失败: {e}")
            raise
    
    def validate_config(self) -> bool:
        """验证OpenAI配置"""
        super().validate_config()
        
        if not self.config.api_key:
            raise ValueError("OpenAI API密钥未配置")
            
        if not self.config.model.startswith(('gpt-', 'o1-', 'text-')):
            logging.warning(f"模型名称可能不正确: {self.config.model}")
            
        return True