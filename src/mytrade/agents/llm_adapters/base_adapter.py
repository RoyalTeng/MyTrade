"""
基础LLM适配器

定义统一的LLM接口规范，参考TradingAgents-CN架构
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class LLMResponse:
    """LLM响应结果"""
    content: str
    usage: Dict[str, int] = None
    model: str = None
    finish_reason: str = None
    metadata: Dict[str, Any] = None
    raw_response: Dict[str, Any] = None
    timestamp: Any = None
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)


@dataclass 
class LLMConfig:
    """LLM配置"""
    provider: str
    model: str
    api_key: str = None
    base_url: str = None
    temperature: float = 0.7
    max_tokens: int = 2000
    timeout: int = 30
    retry_count: int = 3
    extra_params: Dict[str, Any] = None


class BaseLLMAdapter(ABC):
    """基础LLM适配器抽象类"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.client = None
        self._initialize_client()
    
    @abstractmethod
    def _initialize_client(self):
        """初始化LLM客户端"""
        pass
    
    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """聊天接口"""
        pass
    
    @abstractmethod
    def chat_with_tools(self, messages: List[Dict[str, str]], tools: List[Dict[str, Any]], **kwargs) -> LLMResponse:
        """带工具的聊天接口"""
        pass
    
    def validate_config(self) -> bool:
        """验证配置"""
        required_fields = ['provider', 'model']
        for field in required_fields:
            if not getattr(self.config, field):
                raise ValueError(f"Missing required config field: {field}")
        return True
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return {
            'provider': self.config.provider,
            'model': self.config.model,
            'base_url': self.config.base_url,
            'temperature': self.config.temperature,
            'max_tokens': self.config.max_tokens
        }
    
    def health_check(self) -> bool:
        """健康检查"""
        try:
            response = self.chat([{"role": "user", "content": "Hello"}])
            return bool(response.content)
        except Exception:
            return False