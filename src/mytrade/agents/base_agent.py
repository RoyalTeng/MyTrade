"""
基础智能体抽象类

定义统一的Agent接口和行为规范
参考TradingAgents的Agent设计模式
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json
import logging


@dataclass
class AgentState:
    """Agent状态数据结构"""
    agent_id: str
    agent_type: str
    timestamp: datetime = field(default_factory=datetime.now)
    data: Dict[str, Any] = field(default_factory=dict)
    history: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResponse:
    """Agent响应结果"""
    agent_id: str
    agent_type: str
    content: str
    confidence: float
    reasoning: List[str] = field(default_factory=list)
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseAgent(ABC):
    """基础智能体抽象类"""
    
    def __init__(self, 
                 agent_id: str,
                 agent_type: str,
                 llm_adapter,
                 config: Dict[str, Any] = None):
        """初始化Agent
        
        Args:
            agent_id: Agent唯一标识
            agent_type: Agent类型
            llm_adapter: LLM适配器实例
            config: Agent配置
        """
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.llm_adapter = llm_adapter
        self.config = config or {}
        
        self.state = AgentState(
            agent_id=agent_id,
            agent_type=agent_type
        )
        
        self.logger = logging.getLogger(f"agents.{agent_type}")
        self.logger.info(f"Agent {agent_id} ({agent_type}) 初始化完成")
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """获取系统提示词"""
        pass
    
    @abstractmethod
    def process(self, inputs: Dict[str, Any]) -> AgentResponse:
        """处理输入并生成响应"""
        pass
    
    def get_role_description(self) -> str:
        """获取角色描述"""
        return f"我是 {self.agent_type}，负责 {self.get_role_responsibility()}"
    
    @abstractmethod
    def get_role_responsibility(self) -> str:
        """获取角色职责描述"""
        pass
    
    def update_state(self, data: Dict[str, Any]):
        """更新Agent状态"""
        self.state.data.update(data)
        self.state.timestamp = datetime.now()
        
        # 记录历史
        self.state.history.append({
            'timestamp': datetime.now().isoformat(),
            'data': data.copy()
        })
        
        self.logger.debug(f"Agent {self.agent_id} 状态已更新")
    
    def get_state(self) -> AgentState:
        """获取当前状态"""
        return self.state
    
    def reset_state(self):
        """重置状态"""
        self.state = AgentState(
            agent_id=self.agent_id,
            agent_type=self.agent_type
        )
        self.logger.info(f"Agent {self.agent_id} 状态已重置")
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """验证输入参数"""
        required_fields = self.get_required_inputs()
        for field in required_fields:
            if field not in inputs:
                raise ValueError(f"缺少必需的输入参数: {field}")
        return True
    
    @abstractmethod
    def get_required_inputs(self) -> List[str]:
        """获取必需的输入参数列表"""
        pass
    
    def format_output(self, content: str, confidence: float, reasoning: List[str] = None, **kwargs) -> AgentResponse:
        """格式化输出结果"""
        return AgentResponse(
            agent_id=self.agent_id,
            agent_type=self.agent_type,
            content=content,
            confidence=confidence,
            reasoning=reasoning or [],
            data=kwargs,
            metadata={'config': self.config}
        )
    
    def call_llm(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """调用LLM"""
        try:
            response = self.llm_adapter.chat(messages, **kwargs)
            return response.content
        except Exception as e:
            self.logger.error(f"LLM调用失败: {e}")
            raise
    
    def call_llm_with_tools(self, messages: List[Dict[str, str]], tools: List[Dict[str, Any]], **kwargs) -> str:
        """调用带工具的LLM"""
        try:
            response = self.llm_adapter.chat_with_tools(messages, tools, **kwargs)
            return response.content
        except Exception as e:
            self.logger.error(f"带工具的LLM调用失败: {e}")
            raise