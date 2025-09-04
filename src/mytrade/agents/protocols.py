"""
Agent统一协议定义

严格对齐TradingAgents企业级架构：
分析师→研究员→交易员→风险团队→基金经理的现实公司化流程
"""

from typing import TypedDict, Literal, Optional, Dict, Any, Union, List
from datetime import datetime
from enum import Enum
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field


class AgentRole(Enum):
    """智能体角色枚举"""
    # 分析师层 - Analysts
    FUNDAMENTAL = "Fundamentals"
    SENTIMENT = "Sentiment" 
    NEWS = "News"
    TECHNICAL = "Technical"
    
    # 研究员层 - Researchers
    BULL = "Bull"           # 多头研究员
    BEAR = "Bear"           # 空头研究员
    
    # 交易员层 - Trader
    TRADER = "Trader"
    
    # 风险管理层 - Risk
    RISK_SEEKING = "Risk_Seeking"          # 激进风控
    RISK_NEUTRAL = "Risk_Neutral"          # 中性风控  
    RISK_CONSERVATIVE = "Risk_Conservative" # 保守风控
    
    # 管理层 - Portfolio Manager
    PM = "PM"


class DecisionAction(Enum):
    """交易决策动作"""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    REDUCE = "REDUCE"      # 减仓
    INCREASE = "INCREASE"   # 加仓


class AgentDecision(BaseModel):
    """Agent决策信息 - 仅Trader/Risk/PM角色产生"""
    action: DecisionAction
    weight: float = Field(ge=0, le=1, description="仓位权重 0-1")
    confidence: float = Field(ge=0, le=1, description="决策置信度")
    reasoning: str = Field(max_length=500, description="决策推理")
    risk_level: Literal["low", "medium", "high"] = "medium"
    expected_return: Optional[float] = None
    max_loss: Optional[float] = None
    time_horizon: Optional[str] = None  # "1D", "1W", "1M", "3M", "6M", "1Y"


class AgentMetadata(BaseModel):
    """Agent元数据"""
    agent_id: str
    version: str = "1.0.0"
    model_name: Optional[str] = None
    execution_time_ms: Optional[int] = None
    token_usage: Optional[Dict[str, int]] = None
    data_sources: List[str] = []


class AgentOutput(BaseModel):
    """统一Agent输出协议"""
    
    # 基础信息
    role: AgentRole
    timestamp: datetime = Field(default_factory=datetime.now)
    symbol: str = Field(min_length=6, max_length=10, description="股票代码")
    
    # 量化输出
    score: Optional[float] = Field(None, ge=0, le=1, description="量化分数 0-1")
    confidence: float = Field(ge=0, le=1, description="置信度")
    
    # 决策信息 (仅特定角色)
    decision: Optional[AgentDecision] = Field(
        None, 
        description="决策信息，仅Trader/Risk/PM角色产生"
    )
    
    # 特征与解释
    features: Dict[str, Any] = Field(
        default_factory=dict,
        description="关键指标特征，如{'rsi':54.2,'pe':15.3}"
    )
    rationale: str = Field(
        max_length=300, 
        description="自然语言解释要点，限制300字以内"
    )
    
    # 元数据
    metadata: AgentMetadata
    
    # 扩展字段
    tags: List[str] = Field(default_factory=list, description="标签列表")
    alerts: List[str] = Field(default_factory=list, description="告警信息")
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def validate_role_decision(self):
        """验证角色与决策的匹配性"""
        decision_role_values = {
            AgentRole.TRADER.value, 
            AgentRole.RISK_SEEKING.value, 
            AgentRole.RISK_NEUTRAL.value,
            AgentRole.RISK_CONSERVATIVE.value, 
            AgentRole.PM.value
        }
        
        if self.role in decision_role_values and self.decision is None:
            raise ValueError(f"角色 {self.role} 必须提供决策信息")
        
        if self.role not in decision_role_values and self.decision is not None:
            raise ValueError(f"角色 {self.role} 不应提供决策信息")


class AgentContext(BaseModel):
    """Agent执行上下文"""
    symbol: str
    date: str
    market_data: Optional[Dict[str, Any]] = None
    news_data: Optional[List[Dict[str, Any]]] = None
    previous_outputs: List[AgentOutput] = []
    config: Dict[str, Any] = {}
    
    # 全局状态
    market_condition: Optional[str] = None
    volatility_level: Optional[Literal["low", "medium", "high"]] = None
    sentiment_score: Optional[float] = None


class AgentInterface(ABC):
    """Agent标准接口"""
    
    @abstractmethod
    def run(self, context: AgentContext) -> AgentOutput:
        """
        Agent标准执行方法
        
        Args:
            context: 执行上下文
            
        Returns:
            AgentOutput: 标准化输出
        """
        pass
    
    def health_check(self) -> Dict[str, Any]:
        """
        健康检查
        
        Returns:
            健康状态信息
        """
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "agent_id": self.__class__.__name__
        }


# 类型别名
AgentOutputDict = Dict[str, Any]  # 兼容旧版本的字典格式
AgentRole_T = Union[AgentRole, str]  # 兼容字符串角色