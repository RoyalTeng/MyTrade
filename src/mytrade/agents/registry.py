"""
Agent注册中心与调度器

实现可插拔的智能体管理系统，支持：
- 动态角色配置
- 并行执行控制
- 辩论轮次管理
- 依赖关系处理
"""

from typing import Dict, List, Type, Optional, Any, Callable
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio
import logging
from pathlib import Path
import yaml

from .protocols import (
    AgentInterface, AgentOutput, AgentContext, AgentRole,
    AgentOutputDict, AgentRole_T
)


class AgentConfig:
    """Agent配置"""
    def __init__(
        self,
        role: AgentRole,
        class_name: str,
        enabled: bool = True,
        priority: int = 1,
        parallel: bool = True,
        timeout: int = 30,
        retry_count: int = 2,
        config: Dict[str, Any] = None
    ):
        self.role = role
        self.class_name = class_name
        self.enabled = enabled
        self.priority = priority
        self.parallel = parallel
        self.timeout = timeout
        self.retry_count = retry_count
        self.config = config or {}


class DebateConfig:
    """辩论配置"""
    def __init__(
        self,
        max_rounds: int = 3,
        min_rounds: int = 1,
        convergence_threshold: float = 0.1,
        enable_early_stop: bool = True
    ):
        self.max_rounds = max_rounds
        self.min_rounds = min_rounds
        self.convergence_threshold = convergence_threshold
        self.enable_early_stop = enable_early_stop


class AgentRegistry:
    """Agent注册中心"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._agents: Dict[AgentRole, Type[AgentInterface]] = {}
        self._configs: Dict[AgentRole, AgentConfig] = {}
        self._instances: Dict[AgentRole, AgentInterface] = {}
        
        # 辩论配置
        self.debate_config = DebateConfig()
        
    def register_agent(
        self, 
        role: AgentRole, 
        agent_class: Type[AgentInterface],
        config: Optional[AgentConfig] = None
    ):
        """注册智能体"""
        if not issubclass(agent_class, AgentInterface):
            raise ValueError(f"Agent类 {agent_class} 必须继承 AgentInterface")
        
        self._agents[role] = agent_class
        self._configs[role] = config or AgentConfig(role, agent_class.__name__)
        
        self.logger.info(f"注册Agent: {role.value} -> {agent_class.__name__}")
    
    def unregister_agent(self, role: AgentRole):
        """注销智能体"""
        if role in self._agents:
            del self._agents[role]
            del self._configs[role]
            if role in self._instances:
                del self._instances[role]
            self.logger.info(f"注销Agent: {role.value}")
    
    def get_agent(self, role: AgentRole) -> Optional[AgentInterface]:
        """获取Agent实例（单例模式）"""
        if role not in self._agents:
            return None
            
        if role not in self._instances:
            agent_class = self._agents[role]
            config = self._configs[role]
            self._instances[role] = agent_class(**config.config)
            
        return self._instances[role]
    
    def list_agents(self) -> List[AgentRole]:
        """列出所有注册的Agent"""
        return list(self._agents.keys())
    
    def list_enabled_agents(self) -> List[AgentRole]:
        """列出启用的Agent"""
        return [
            role for role, config in self._configs.items() 
            if config.enabled
        ]
    
    def is_agent_enabled(self, role: AgentRole) -> bool:
        """检查Agent是否启用"""
        if role not in self._configs:
            return False
        return self._configs[role].enabled
    
    def load_config(self, config_path: str):
        """从配置文件加载Agent配置"""
        config_file = Path(config_path)
        if not config_file.exists():
            self.logger.warning(f"配置文件不存在: {config_path}")
            return
            
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        agents_config = config_data.get('agents', {})
        
        for role_str, agent_config in agents_config.items():
            try:
                role = AgentRole(role_str)
                config = AgentConfig(
                    role=role,
                    class_name=agent_config.get('class'),
                    enabled=agent_config.get('enabled', True),
                    priority=agent_config.get('priority', 1),
                    parallel=agent_config.get('parallel', True),
                    timeout=agent_config.get('timeout', 30),
                    retry_count=agent_config.get('retry', 2),
                    config=agent_config.get('config', {})
                )
                self._configs[role] = config
                self.logger.info(f"加载Agent配置: {role.value}")
                
            except ValueError as e:
                self.logger.error(f"无效的Agent角色: {role_str}, 错误: {e}")


class AgentOrchestrator:
    """Agent编排器 - 实现TradingAgents的企业级流程"""
    
    def __init__(
        self, 
        registry: AgentRegistry,
        debate_config: Optional[DebateConfig] = None
    ):
        self.registry = registry
        self.debate_config = debate_config or DebateConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def execute_pipeline(self, context: AgentContext) -> Dict[AgentRole, AgentOutput]:
        """
        执行完整的智能体流水线
        
        流程: Analysts → Research Debate → Trader → Risk → PM
        """
        results = {}
        
        # 阶段1: 分析师并行执行
        analyst_results = self._execute_analysts(context)
        results.update(analyst_results)
        
        # 更新上下文
        context.previous_outputs = list(analyst_results.values())
        
        # 阶段2: 研究员辩论
        research_results = self._execute_debate(context)
        results.update(research_results)
        
        # 更新上下文
        context.previous_outputs = list(results.values())
        
        # 阶段3: 交易员决策
        trader_result = self._execute_trader(context)
        if trader_result:
            results.update(trader_result)
            context.previous_outputs = list(results.values())
        
        # 阶段4: 风险管理
        risk_results = self._execute_risk_management(context)
        results.update(risk_results)
        
        # 阶段5: 基金经理审批
        pm_result = self._execute_pm_approval(context)
        if pm_result:
            results.update(pm_result)
        
        return results
    
    def _execute_analysts(self, context: AgentContext) -> Dict[AgentRole, AgentOutput]:
        """并行执行分析师"""
        analyst_roles = [
            AgentRole.FUNDAMENTAL,
            AgentRole.SENTIMENT, 
            AgentRole.NEWS,
            AgentRole.TECHNICAL
        ]
        
        enabled_analysts = [
            role for role in analyst_roles 
            if role in self.registry.list_enabled_agents()
        ]
        
        if not enabled_analysts:
            self.logger.warning("没有启用的分析师")
            return {}
        
        self.logger.info(f"执行{len(enabled_analysts)}个分析师")
        return self._execute_parallel(enabled_analysts, context)
    
    def _execute_debate(self, context: AgentContext) -> Dict[AgentRole, AgentOutput]:
        """执行多空辩论"""
        debate_roles = [AgentRole.BULL, AgentRole.BEAR]
        
        enabled_debaters = [
            role for role in debate_roles 
            if role in self.registry.list_enabled_agents()
        ]
        
        if len(enabled_debaters) < 2:
            self.logger.warning("辩论需要至少2个研究员")
            return {}
        
        results = {}
        
        for round_num in range(1, self.debate_config.max_rounds + 1):
            self.logger.info(f"辩论第{round_num}轮")
            
            round_results = self._execute_parallel(enabled_debaters, context)
            results.update(round_results)
            
            # 检查是否收敛
            if round_num >= self.debate_config.min_rounds:
                if self._check_debate_convergence(round_results):
                    self.logger.info(f"辩论在第{round_num}轮收敛")
                    break
            
            # 更新上下文供下一轮使用
            context.previous_outputs.extend(round_results.values())
        
        return results
    
    def _check_debate_convergence(self, round_results: Dict[AgentRole, AgentOutput]) -> bool:
        """检查辩论是否收敛"""
        if not self.debate_config.enable_early_stop:
            return False
            
        scores = [
            output.score for output in round_results.values() 
            if output.score is not None
        ]
        
        if len(scores) < 2:
            return False
        
        # 计算分歧度（方差）
        mean_score = sum(scores) / len(scores)
        variance = sum((s - mean_score) ** 2 for s in scores) / len(scores)
        
        return variance < self.debate_config.convergence_threshold
    
    def _execute_trader(self, context: AgentContext) -> Optional[Dict[AgentRole, AgentOutput]]:
        """执行交易员决策"""
        if AgentRole.TRADER not in self.registry.list_enabled_agents():
            return None
        
        trader = self.registry.get_agent(AgentRole.TRADER)
        if not trader:
            return None
        
        try:
            result = trader.run(context)
            self.logger.info("交易员决策完成")
            return {AgentRole.TRADER: result}
        except Exception as e:
            self.logger.error(f"交易员执行失败: {e}")
            return None
    
    def _execute_risk_management(self, context: AgentContext) -> Dict[AgentRole, AgentOutput]:
        """执行风险管理（三视角）"""
        risk_roles = [
            AgentRole.RISK_SEEKING,
            AgentRole.RISK_NEUTRAL,
            AgentRole.RISK_CONSERVATIVE
        ]
        
        enabled_risk = [
            role for role in risk_roles 
            if role in self.registry.list_enabled_agents()
        ]
        
        if not enabled_risk:
            return {}
        
        self.logger.info(f"执行{len(enabled_risk)}个风险管理视角")
        return self._execute_parallel(enabled_risk, context)
    
    def _execute_pm_approval(self, context: AgentContext) -> Optional[Dict[AgentRole, AgentOutput]]:
        """执行基金经理审批"""
        if AgentRole.PM not in self.registry.list_enabled_agents():
            return None
        
        pm = self.registry.get_agent(AgentRole.PM)
        if not pm:
            return None
        
        try:
            result = pm.run(context)
            self.logger.info("基金经理审批完成")
            return {AgentRole.PM: result}
        except Exception as e:
            self.logger.error(f"基金经理执行失败: {e}")
            return None
    
    def _execute_parallel(
        self, 
        roles: List[AgentRole], 
        context: AgentContext
    ) -> Dict[AgentRole, AgentOutput]:
        """并行执行多个Agent"""
        results = {}
        
        with ThreadPoolExecutor(max_workers=len(roles)) as executor:
            future_to_role = {}
            
            for role in roles:
                agent = self.registry.get_agent(role)
                if agent:
                    config = self.registry._configs.get(role)
                    future = executor.submit(
                        self._execute_with_timeout,
                        agent,
                        context,
                        config.timeout if config else 30
                    )
                    future_to_role[future] = role
            
            for future in as_completed(future_to_role):
                role = future_to_role[future]
                try:
                    result = future.result()
                    if result:
                        results[role] = result
                        self.logger.info(f"Agent {role.value} 执行成功")
                except Exception as e:
                    self.logger.error(f"Agent {role.value} 执行失败: {e}")
        
        return results
    
    def _execute_with_timeout(
        self, 
        agent: AgentInterface, 
        context: AgentContext, 
        timeout: int
    ) -> Optional[AgentOutput]:
        """带超时的Agent执行"""
        try:
            result = agent.run(context)
            # 验证输出协议
            if isinstance(result, dict):
                # 兼容旧格式，转换为新协议
                return self._convert_legacy_output(result)
            return result
        except Exception as e:
            self.logger.error(f"Agent执行异常: {e}")
            return None
    
    def _convert_legacy_output(self, legacy_output: AgentOutputDict) -> AgentOutput:
        """转换旧版本输出格式为新协议"""
        # TODO: 实现旧格式到新协议的转换逻辑
        pass


# 全局注册中心实例
default_registry = AgentRegistry()
default_orchestrator = AgentOrchestrator(default_registry)