"""
工作流管理模块

实现智能体的协作工作流
参考TradingAgents的graph架构设计
"""

from .trading_workflow import TradingWorkflow
from .workflow_state import WorkflowState, WorkflowResult

__all__ = [
    'TradingWorkflow',
    'WorkflowState',
    'WorkflowResult'
]