"""
工作流状态管理

定义工作流的状态数据结构
参考TradingAgents的状态管理设计
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum


class WorkflowStage(Enum):
    """工作流阶段"""
    INITIALIZED = "初始化"
    ANALYZING = "分析中"
    RESEARCHING = "研究中"
    DEBATING = "辩论中"
    DECIDING = "决策中"
    COMPLETED = "已完成"
    FAILED = "失败"


@dataclass
class AgentResult:
    """单个Agent的结果"""
    agent_id: str
    agent_type: str
    content: str
    confidence: float
    reasoning: List[str]
    data: Dict[str, Any]
    timestamp: datetime
    execution_time: float = 0.0


@dataclass
class WorkflowState:
    """工作流状态"""
    # 基本信息
    workflow_id: str
    symbol: str
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    stage: WorkflowStage = WorkflowStage.INITIALIZED
    
    # 输入数据
    input_data: Dict[str, Any] = field(default_factory=dict)
    
    # Agent结果
    agent_results: Dict[str, AgentResult] = field(default_factory=dict)
    
    # 工作流历史
    stage_history: List[Dict[str, Any]] = field(default_factory=list)
    
    # 错误信息
    errors: List[str] = field(default_factory=list)
    
    # 元数据
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_agent_result(self, agent_result: AgentResult):
        """添加Agent结果"""
        self.agent_results[agent_result.agent_id] = agent_result
        self.updated_at = datetime.now()
    
    def set_stage(self, stage: WorkflowStage):
        """设置工作流阶段"""
        old_stage = self.stage
        self.stage = stage
        self.updated_at = datetime.now()
        
        # 记录阶段历史
        self.stage_history.append({
            'from_stage': old_stage.value if old_stage else None,
            'to_stage': stage.value,
            'timestamp': datetime.now().isoformat(),
            'duration': (datetime.now() - self.created_at).total_seconds()
        })
    
    def add_error(self, error_msg: str):
        """添加错误信息"""
        self.errors.append({
            'timestamp': datetime.now().isoformat(),
            'message': error_msg
        })
        self.updated_at = datetime.now()
    
    def get_agent_results_by_type(self, agent_type: str) -> List[AgentResult]:
        """按类型获取Agent结果"""
        return [result for result in self.agent_results.values() 
                if result.agent_type == agent_type]
    
    def is_completed(self) -> bool:
        """检查是否完成"""
        return self.stage in [WorkflowStage.COMPLETED, WorkflowStage.FAILED]
    
    def get_total_execution_time(self) -> float:
        """获取总执行时间"""
        return (self.updated_at - self.created_at).total_seconds()


@dataclass
class WorkflowResult:
    """工作流最终结果"""
    workflow_id: str
    symbol: str
    action: str  # BUY/SELL/HOLD
    confidence: float
    reasoning: List[str]
    
    # 详细分析结果
    technical_analysis: Dict[str, Any] = field(default_factory=dict)
    fundamental_analysis: Dict[str, Any] = field(default_factory=dict)
    sentiment_analysis: Dict[str, Any] = field(default_factory=dict)
    risk_assessment: Dict[str, Any] = field(default_factory=dict)
    
    # 执行信息
    execution_time: float = 0.0
    agents_used: List[str] = field(default_factory=list)
    
    # 元数据
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'workflow_id': self.workflow_id,
            'symbol': self.symbol,
            'action': self.action,
            'confidence': self.confidence,
            'reasoning': self.reasoning,
            'technical_analysis': self.technical_analysis,
            'fundamental_analysis': self.fundamental_analysis,
            'sentiment_analysis': self.sentiment_analysis,
            'risk_assessment': self.risk_assessment,
            'execution_time': self.execution_time,
            'agents_used': self.agents_used,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat()
        }