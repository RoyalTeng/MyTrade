"""
DeepSeek LLM适配器实现

支持DeepSeek API，提供深度求索模型的访问接口
"""

import os
import json
import requests
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from .base_adapter import BaseLLMAdapter, LLMResponse, LLMConfig


class DeepSeekAdapter(BaseLLMAdapter):
    """DeepSeek API适配器"""
    
    def __init__(self, config: LLMConfig):
        """初始化DeepSeek适配器
        
        Args:
            config: LLM配置对象
        """
        super().__init__(config)
        
        # DeepSeek API配置
        self.base_url = config.base_url or "https://api.deepseek.com/v1"
        self.api_key = config.api_key or os.getenv('DEEPSEEK_API_KEY')
        
        if not self.api_key:
            raise ValueError("DeepSeek API密钥未提供，请设置api_key或DEEPSEEK_API_KEY环境变量")
        
        # 设置请求头
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        
        # 默认参数
        self.default_model = config.model or 'deepseek-chat'
        self.default_temperature = config.temperature or 0.3
        self.default_max_tokens = config.max_tokens or 2000
        
        self.logger = logging.getLogger("adapters.deepseek")
        self.logger.info(f"DeepSeek适配器初始化完成: {self.default_model}")
    
    def _initialize_client(self):
        """初始化客户端（DeepSeek使用HTTP请求，不需要特殊客户端）"""
        pass
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """发送聊天请求到DeepSeek API
        
        Args:
            messages: 消息列表，格式: [{"role": "user", "content": "..."}]
            **kwargs: 其他参数
            
        Returns:
            LLMResponse: 响应对象
        """
        try:
            # 准备请求数据
            request_data = {
                'model': kwargs.get('model', self.default_model),
                'messages': messages,
                'temperature': kwargs.get('temperature', self.default_temperature),
                'max_tokens': kwargs.get('max_tokens', self.default_max_tokens),
                'stream': False
            }
            
            # 添加其他可选参数
            if 'top_p' in kwargs:
                request_data['top_p'] = kwargs['top_p']
            if 'frequency_penalty' in kwargs:
                request_data['frequency_penalty'] = kwargs['frequency_penalty']
            if 'presence_penalty' in kwargs:
                request_data['presence_penalty'] = kwargs['presence_penalty']
            
            # 发送请求
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=request_data,
                timeout=kwargs.get('timeout', 60)
            )
            
            if response.status_code != 200:
                error_msg = f"DeepSeek API请求失败: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                raise Exception(error_msg)
            
            # 解析响应
            response_data = response.json()
            
            if 'choices' not in response_data or len(response_data['choices']) == 0:
                raise Exception("DeepSeek API返回空响应")
            
            choice = response_data['choices'][0]
            content = choice['message']['content']
            
            # 计算token使用情况
            usage = response_data.get('usage', {})
            prompt_tokens = usage.get('prompt_tokens', 0)
            completion_tokens = usage.get('completion_tokens', 0)
            total_tokens = usage.get('total_tokens', 0)
            
            return LLMResponse(
                content=content,
                model=request_data['model'],
                usage={
                    'prompt_tokens': prompt_tokens,
                    'completion_tokens': completion_tokens,
                    'total_tokens': total_tokens
                },
                raw_response=response_data,
                timestamp=datetime.now()
            )
            
        except requests.exceptions.Timeout:
            error_msg = "DeepSeek API请求超时"
            self.logger.error(error_msg)
            raise Exception(error_msg)
        except requests.exceptions.RequestException as e:
            error_msg = f"DeepSeek API网络请求失败: {e}"
            self.logger.error(error_msg)
            raise Exception(error_msg)
        except json.JSONDecodeError as e:
            error_msg = f"DeepSeek API响应解析失败: {e}"
            self.logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            self.logger.error(f"DeepSeek适配器调用失败: {e}")
            raise
    
    def chat_with_tools(self, 
                       messages: List[Dict[str, str]], 
                       tools: List[Dict[str, Any]], 
                       **kwargs) -> LLMResponse:
        """带工具调用的聊天请求
        
        Args:
            messages: 消息列表
            tools: 工具定义列表
            **kwargs: 其他参数
            
        Returns:
            LLMResponse: 响应对象
        """
        try:
            # 准备请求数据
            request_data = {
                'model': kwargs.get('model', self.default_model),
                'messages': messages,
                'temperature': kwargs.get('temperature', self.default_temperature),
                'max_tokens': kwargs.get('max_tokens', self.default_max_tokens),
                'tools': tools,
                'tool_choice': kwargs.get('tool_choice', 'auto'),
                'stream': False
            }
            
            # 发送请求
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=request_data,
                timeout=kwargs.get('timeout', 60)
            )
            
            if response.status_code != 200:
                error_msg = f"DeepSeek API工具调用请求失败: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                raise Exception(error_msg)
            
            # 解析响应
            response_data = response.json()
            
            if 'choices' not in response_data or len(response_data['choices']) == 0:
                raise Exception("DeepSeek API工具调用返回空响应")
            
            choice = response_data['choices'][0]
            message = choice['message']
            
            # 提取工具调用信息
            tool_calls = message.get('tool_calls', [])
            
            # 计算token使用情况
            usage = response_data.get('usage', {})
            
            return LLMResponse(
                content=message.get('content', ''),
                model=request_data['model'],
                usage={
                    'prompt_tokens': usage.get('prompt_tokens', 0),
                    'completion_tokens': usage.get('completion_tokens', 0),
                    'total_tokens': usage.get('total_tokens', 0)
                },
                raw_response=response_data,
                timestamp=datetime.now(),
                tool_calls=tool_calls
            )
            
        except Exception as e:
            self.logger.error(f"DeepSeek工具调用失败: {e}")
            raise
    
    def validate_config(self) -> bool:
        """验证配置
        
        Returns:
            bool: 配置是否有效
        """
        try:
            # 检查API密钥
            if not self.api_key:
                self.logger.error("DeepSeek API密钥未配置")
                return False
            
            # 简单的API连通性测试
            test_messages = [{"role": "user", "content": "Hello"}]
            
            request_data = {
                'model': self.default_model,
                'messages': test_messages,
                'max_tokens': 10,
                'temperature': 0
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=request_data,
                timeout=30
            )
            
            if response.status_code == 200:
                self.logger.info("DeepSeek API配置验证成功")
                return True
            else:
                self.logger.error(f"DeepSeek API配置验证失败: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"DeepSeek配置验证异常: {e}")
            return False
    
    def health_check(self) -> bool:
        """健康检查
        
        Returns:
            bool: 服务是否健康
        """
        try:
            # 发送简单的健康检查请求
            test_messages = [{"role": "user", "content": "ping"}]
            
            request_data = {
                'model': self.default_model,
                'messages': test_messages,
                'max_tokens': 5,
                'temperature': 0
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=request_data,
                timeout=15
            )
            
            return response.status_code == 200
            
        except Exception as e:
            self.logger.error(f"DeepSeek健康检查失败: {e}")
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息
        
        Returns:
            Dict[str, Any]: 模型信息
        """
        return {
            'provider': 'deepseek',
            'model': self.default_model,
            'base_url': self.base_url,
            'temperature': self.default_temperature,
            'max_tokens': self.default_max_tokens,
            'support_tools': True,
            'support_streaming': True,
            'api_version': 'v1'
        }