"""
智能体编排引擎 - TradingAgents企业级流水线

实现完整的"分析师→研究员→交易员→风险管理→基金经理"企业级决策流程：
- 分层并行/串行执行
- 辩论收敛机制 
- 结果聚合与传递
- 异常恢复与重试
"""

from typing import Dict, List, Optional, Any, Tuple, Set
from concurrent.futures import ThreadPoolExecutor, as_completed, Future
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import asyncio
import logging
import threading
import time
from enum import Enum

from .protocols import (
    AgentInterface, AgentOutput, AgentContext, AgentRole, 
    AgentDecision, DecisionAction
)
from ..logging.structured_logger import (
    DualFormatLogger, StructuredLogLevel, LogCategory,
    get_structured_logger
)
from .registry import AgentRegistry, DebateConfig


class PipelineStage(Enum):
    """流水线阶段"""
    ANALYSIS = "analysis"           # 分析师阶段
    RESEARCH = "research"          # 研究员辩论阶段  
    TRADING = "trading"            # 交易员决策阶段
    RISK_MANAGEMENT = "risk_management"  # 风险管理阶段
    PORTFOLIO_MANAGEMENT = "portfolio_management"  # 投资组合管理


@dataclass
class PipelineResult:
    """流水线执行结果"""
    stage: PipelineStage
    timestamp: datetime = field(default_factory=datetime.now)
    success: bool = True
    outputs: Dict[AgentRole, AgentOutput] = field(default_factory=dict)
    execution_time_ms: float = 0.0
    errors: List[str] = field(default_factory=list)
    
    def get_consensus_score(self) -> Optional[float]:
        """获取共识评分"""
        if not self.outputs:
            return None
        scores = [o.score for o in self.outputs.values() if o.score is not None]
        return sum(scores) / len(scores) if scores else None
    
    def get_confidence_weighted_score(self) -> Optional[float]:
        """获取置信度加权评分"""
        if not self.outputs:
            return None
        
        weighted_sum = 0.0
        total_confidence = 0.0
        
        for output in self.outputs.values():
            if output.score is not None and output.confidence > 0:
                weighted_sum += output.score * output.confidence
                total_confidence += output.confidence
        
        return weighted_sum / total_confidence if total_confidence > 0 else None


@dataclass
class DebateResult:
    """辩论结果"""
    converged: bool
    rounds: int
    bull_score: float
    bear_score: float
    consensus_score: float
    confidence: float
    reasoning: str
    
    def get_final_stance(self) -> str:
        """获取最终立场"""
        if abs(self.bull_score - self.bear_score) < 0.1:
            return "neutral"
        return "bullish" if self.bull_score > self.bear_score else "bearish"


class AgentOrchestrator:
    """智能体编排引擎"""
    
    def __init__(self, registry: AgentRegistry):
        """初始化编排引擎
        
        Args:
            registry: Agent注册中心
        """
        self.registry = registry
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # 执行配置
        self.max_parallel_agents = 8
        self.stage_timeout = 300  # 5分钟
        self.retry_delay = 1.0
        
        # 统计信息
        self.execution_stats = {
            'total_pipelines': 0,
            'successful_pipelines': 0,
            'stage_timings': {},
            'error_counts': {}
        }
        
        # 线程池
        self.executor = ThreadPoolExecutor(
            max_workers=self.max_parallel_agents,
            thread_name_prefix="AgentWorker"
        )
    
    def execute_full_pipeline(self, context: AgentContext) -> Dict[PipelineStage, PipelineResult]:
        """执行完整的决策流水线
        
        Args:
            context: 执行上下文
            
        Returns:
            Dict: 各阶段执行结果
        """
        pipeline_start = time.time()
        results = {}
        
        try:
            self.logger.info(f"开始执行完整决策流水线: {context.symbol}")
            self.execution_stats['total_pipelines'] += 1
            
            # Stage 1: 并行分析师执行
            analysis_result = self._execute_analysis_stage(context)
            results[PipelineStage.ANALYSIS] = analysis_result
            
            if not analysis_result.success:
                self.logger.error("分析师阶段失败，终止流水线")
                return results
            
            # Stage 2: 研究员辩论
            context.previous_outputs = list(analysis_result.outputs.values())
            research_result = self._execute_research_stage(context)
            results[PipelineStage.RESEARCH] = research_result
            
            # Stage 3: 交易员决策
            if research_result.success:
                context.previous_outputs.extend(list(research_result.outputs.values()))
            trader_result = self._execute_trading_stage(context)
            results[PipelineStage.TRADING] = trader_result
            
            # Stage 4: 风险管理
            if trader_result.success:
                context.previous_outputs.extend(list(trader_result.outputs.values()))
            risk_result = self._execute_risk_management_stage(context)
            results[PipelineStage.RISK_MANAGEMENT] = risk_result
            
            # Stage 5: 投资组合管理（最终决策）
            if risk_result.success:
                context.previous_outputs.extend(list(risk_result.outputs.values()))
            pm_result = self._execute_portfolio_management_stage(context)
            results[PipelineStage.PORTFOLIO_MANAGEMENT] = pm_result
            
            # 统计成功率
            if all(r.success for r in results.values()):
                self.execution_stats['successful_pipelines'] += 1
            
            total_time = (time.time() - pipeline_start) * 1000
            self.logger.info(f"流水线执行完成: {context.symbol}, 耗时: {total_time:.1f}ms")
            
            return results
            
        except Exception as e:
            self.logger.error(f"流水线执行异常: {e}")
            error_result = PipelineResult(
                stage=PipelineStage.ANALYSIS,
                success=False,
                errors=[f"Pipeline execution failed: {str(e)}"]
            )
            return {PipelineStage.ANALYSIS: error_result}
    
    def _execute_analysis_stage(self, context: AgentContext) -> PipelineResult:
        """执行分析师阶段（并行）"""
        stage_start = time.time()
        
        # 获取分析师角色
        analyst_roles = [
            AgentRole.FUNDAMENTAL,
            AgentRole.TECHNICAL, 
            AgentRole.SENTIMENT,
            AgentRole.NEWS
        ]
        
        enabled_analysts = [role for role in analyst_roles 
                           if self.registry.is_agent_enabled(role)]
        
        if not enabled_analysts:
            return PipelineResult(
                stage=PipelineStage.ANALYSIS,
                success=False,
                errors=["没有启用的分析师角色"]
            )
        
        self.logger.info(f"执行分析师阶段: {len(enabled_analysts)} 个角色并行")
        
        # 并行执行分析师
        futures = {}
        for role in enabled_analysts:
            try:
                agent = self.registry.get_agent(role)
                future = self.executor.submit(self._execute_single_agent, agent, context, role)
                futures[future] = role
            except Exception as e:
                self.logger.error(f"启动分析师 {role.value} 失败: {e}")
        
        # 收集结果
        outputs = {}
        errors = []
        
        for future in as_completed(futures, timeout=self.stage_timeout):
            role = futures[future]
            try:
                result = future.result()
                if result:
                    outputs[role] = result
                    self.logger.debug(f"分析师 {role.value} 执行完成")
                else:
                    errors.append(f"分析师 {role.value} 返回空结果")
            except Exception as e:
                errors.append(f"分析师 {role.value} 执行失败: {str(e)}")
                self.logger.error(f"分析师 {role.value} 执行异常: {e}")
        
        execution_time = (time.time() - stage_start) * 1000
        
        return PipelineResult(
            stage=PipelineStage.ANALYSIS,
            success=len(outputs) > 0,
            outputs=outputs,
            execution_time_ms=execution_time,
            errors=errors
        )
    
    def _execute_research_stage(self, context: AgentContext) -> PipelineResult:
        """执行研究员辩论阶段"""
        stage_start = time.time()
        
        # 检查是否有Bull/Bear研究员
        bull_enabled = self.registry.is_agent_enabled(AgentRole.BULL)
        bear_enabled = self.registry.is_agent_enabled(AgentRole.BEAR)
        
        if not bull_enabled or not bear_enabled:
            self.logger.warning("Bull/Bear研究员未启用，跳过辩论阶段")
            return PipelineResult(
                stage=PipelineStage.RESEARCH,
                success=True,
                outputs={},
                execution_time_ms=(time.time() - stage_start) * 1000
            )
        
        self.logger.info("执行研究员辩论阶段")
        
        # 执行辩论
        debate_result = self._conduct_debate(context)
        
        # 构造输出
        outputs = {}
        if debate_result:
            # 创建辩论结果的AgentOutput
            debate_output = AgentOutput(
                role=AgentRole.BULL,  # 使用Bull角色作为代表
                timestamp=datetime.now(),
                symbol=context.symbol,
                score=debate_result.consensus_score,
                confidence=debate_result.confidence,
                features={
                    'debate_rounds': debate_result.rounds,
                    'bull_score': debate_result.bull_score,
                    'bear_score': debate_result.bear_score,
                    'converged': debate_result.converged,
                    'final_stance': debate_result.get_final_stance()
                },
                rationale=debate_result.reasoning,
                metadata={
                    'agent_id': 'debate_consensus',
                    'version': '1.0.0',
                    'debate_result': True
                },
                tags=['research', 'debate', 'consensus']
            )
            outputs[AgentRole.BULL] = debate_output
        
        execution_time = (time.time() - stage_start) * 1000
        
        return PipelineResult(
            stage=PipelineStage.RESEARCH,
            success=debate_result is not None,
            outputs=outputs,
            execution_time_ms=execution_time,
            errors=[] if debate_result else ["辩论执行失败"]
        )
    
    def _execute_trading_stage(self, context: AgentContext) -> PipelineResult:
        """执行交易员决策阶段"""
        stage_start = time.time()
        
        if not self.registry.is_agent_enabled(AgentRole.TRADER):
            return PipelineResult(
                stage=PipelineStage.TRADING,
                success=False,
                errors=["交易员角色未启用"]
            )
        
        self.logger.info("执行交易员决策阶段")
        
        try:
            trader = self.registry.get_agent(AgentRole.TRADER)
            result = self._execute_single_agent(trader, context, AgentRole.TRADER)
            
            outputs = {AgentRole.TRADER: result} if result else {}
            
            return PipelineResult(
                stage=PipelineStage.TRADING,
                success=result is not None,
                outputs=outputs,
                execution_time_ms=(time.time() - stage_start) * 1000,
                errors=[] if result else ["交易员执行失败"]
            )
            
        except Exception as e:
            return PipelineResult(
                stage=PipelineStage.TRADING,
                success=False,
                errors=[f"交易员执行异常: {str(e)}"],
                execution_time_ms=(time.time() - stage_start) * 1000
            )
    
    def _execute_risk_management_stage(self, context: AgentContext) -> PipelineResult:
        """执行风险管理阶段（三视角并行）"""
        stage_start = time.time()
        
        # 三个风险管理角色
        risk_roles = [
            AgentRole.RISK_SEEKING,
            AgentRole.RISK_NEUTRAL,
            AgentRole.RISK_CONSERVATIVE
        ]
        
        enabled_risk_roles = [role for role in risk_roles 
                             if self.registry.is_agent_enabled(role)]
        
        if not enabled_risk_roles:
            return PipelineResult(
                stage=PipelineStage.RISK_MANAGEMENT,
                success=False,
                errors=["没有启用的风险管理角色"]
            )
        
        self.logger.info(f"执行风险管理阶段: {len(enabled_risk_roles)} 个视角并行")
        
        # 并行执行风险管理
        futures = {}
        for role in enabled_risk_roles:
            try:
                agent = self.registry.get_agent(role)
                future = self.executor.submit(self._execute_single_agent, agent, context, role)
                futures[future] = role
            except Exception as e:
                self.logger.error(f"启动风险管理 {role.value} 失败: {e}")
        
        # 收集结果
        outputs = {}
        errors = []
        
        for future in as_completed(futures, timeout=60):  # 风险管理较快
            role = futures[future]
            try:
                result = future.result()
                if result:
                    outputs[role] = result
                else:
                    errors.append(f"风险管理 {role.value} 返回空结果")
            except Exception as e:
                errors.append(f"风险管理 {role.value} 执行失败: {str(e)}")
        
        execution_time = (time.time() - stage_start) * 1000
        
        return PipelineResult(
            stage=PipelineStage.RISK_MANAGEMENT,
            success=len(outputs) > 0,
            outputs=outputs,
            execution_time_ms=execution_time,
            errors=errors
        )
    
    def _execute_portfolio_management_stage(self, context: AgentContext) -> PipelineResult:
        """执行投资组合管理阶段（最终决策）"""
        stage_start = time.time()
        
        if not self.registry.is_agent_enabled(AgentRole.PM):
            return PipelineResult(
                stage=PipelineStage.PORTFOLIO_MANAGEMENT,
                success=False,
                errors=["投资组合管理角色未启用"]
            )
        
        self.logger.info("执行投资组合管理阶段")
        
        try:
            pm = self.registry.get_agent(AgentRole.PM)
            result = self._execute_single_agent(pm, context, AgentRole.PM)
            
            outputs = {AgentRole.PM: result} if result else {}
            
            return PipelineResult(
                stage=PipelineStage.PORTFOLIO_MANAGEMENT,
                success=result is not None,
                outputs=outputs,
                execution_time_ms=(time.time() - stage_start) * 1000,
                errors=[] if result else ["PM执行失败"]
            )
            
        except Exception as e:
            return PipelineResult(
                stage=PipelineStage.PORTFOLIO_MANAGEMENT,
                success=False,
                errors=[f"PM执行异常: {str(e)}"],
                execution_time_ms=(time.time() - stage_start) * 1000
            )
    
    def _conduct_debate(self, context: AgentContext) -> Optional[DebateResult]:
        """执行Bull/Bear辩论"""
        try:
            bull_agent = self.registry.get_agent(AgentRole.BULL)
            bear_agent = self.registry.get_agent(AgentRole.BEAR)
            
            debate_config = self.registry.debate_config
            max_rounds = debate_config.max_rounds
            convergence_threshold = debate_config.convergence_threshold
            
            bull_scores = []
            bear_scores = []
            reasoning_history = []
            
            for round_num in range(max_rounds):
                self.logger.debug(f"辩论第 {round_num + 1} 轮")
                
                # Bull和Bear并行执行
                bull_future = self.executor.submit(
                    self._execute_single_agent, bull_agent, context, AgentRole.BULL
                )
                bear_future = self.executor.submit(
                    self._execute_single_agent, bear_agent, context, AgentRole.BEAR
                )
                
                bull_result = bull_future.result(timeout=60)
                bear_result = bear_future.result(timeout=60)
                
                if not bull_result or not bear_result:
                    break
                
                bull_scores.append(bull_result.score or 0.5)
                bear_scores.append(bear_result.score or 0.5)
                
                reasoning_history.append({
                    'round': round_num + 1,
                    'bull_reasoning': bull_result.rationale,
                    'bear_reasoning': bear_result.rationale,
                    'bull_score': bull_result.score,
                    'bear_score': bear_result.score
                })
                
                # 检查收敛
                if len(bull_scores) >= 2:
                    bull_variance = self._calculate_variance(bull_scores[-2:])
                    bear_variance = self._calculate_variance(bear_scores[-2:])
                    
                    if (bull_variance < convergence_threshold and 
                        bear_variance < convergence_threshold):
                        self.logger.info(f"辩论在第 {round_num + 1} 轮收敛")
                        break
                
                # 更新上下文，传递辩论历史
                context.previous_outputs = [bull_result, bear_result]
            
            if not bull_scores or not bear_scores:
                return None
            
            # 计算最终结果
            final_bull_score = sum(bull_scores) / len(bull_scores)
            final_bear_score = sum(bear_scores) / len(bear_scores)
            consensus_score = (final_bull_score + (1 - final_bear_score)) / 2
            
            # 计算置信度（基于收敛程度）
            bull_variance = self._calculate_variance(bull_scores)
            bear_variance = self._calculate_variance(bear_scores)
            confidence = max(0.1, min(0.9, 1.0 - (bull_variance + bear_variance) / 2))
            
            # 生成综合推理
            final_reasoning = self._generate_debate_summary(reasoning_history, consensus_score)
            
            return DebateResult(
                converged=len(reasoning_history) < max_rounds,
                rounds=len(reasoning_history),
                bull_score=final_bull_score,
                bear_score=final_bear_score,
                consensus_score=consensus_score,
                confidence=confidence,
                reasoning=final_reasoning
            )
            
        except Exception as e:
            self.logger.error(f"辩论执行失败: {e}")
            return None
    
    def _execute_single_agent(
        self, 
        agent: AgentInterface, 
        context: AgentContext, 
        role: AgentRole
    ) -> Optional[AgentOutput]:
        """执行单个Agent"""
        try:
            start_time = time.time()
            result = agent.run(context)
            execution_time = (time.time() - start_time) * 1000
            
            self.logger.debug(f"Agent {role.value} 执行完成，耗时: {execution_time:.1f}ms")
            return result
            
        except Exception as e:
            self.logger.error(f"Agent {role.value} 执行失败: {e}")
            return None
    
    def _calculate_variance(self, values: List[float]) -> float:
        """计算方差"""
        if len(values) < 2:
            return 1.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance
    
    def _generate_debate_summary(
        self, 
        history: List[Dict], 
        consensus_score: float
    ) -> str:
        """生成辩论摘要"""
        if not history:
            return "辩论历史为空"
        
        rounds = len(history)
        latest = history[-1]
        
        stance = "看多" if consensus_score > 0.6 else "看空" if consensus_score < 0.4 else "中性"
        
        summary_parts = [
            f"经过{rounds}轮辩论，最终达成{stance}共识",
            f"多方观点: {latest['bull_reasoning'][:100]}...",
            f"空方观点: {latest['bear_reasoning'][:100]}...",
            f"综合评分: {consensus_score:.2f}"
        ]
        
        return "；".join(summary_parts)
    
    def get_execution_statistics(self) -> Dict[str, Any]:
        """获取执行统计信息"""
        total = self.execution_stats['total_pipelines']
        success = self.execution_stats['successful_pipelines']
        
        return {
            'total_pipelines': total,
            'successful_pipelines': success,
            'success_rate': success / total if total > 0 else 0,
            'stage_timings': self.execution_stats['stage_timings'],
            'error_counts': self.execution_stats['error_counts'],
            'thread_pool_status': {
                'max_workers': self.executor._max_workers,
                'threads': len(self.executor._threads) if hasattr(self.executor, '_threads') else 0
            }
        }
    
    def shutdown(self):
        """关闭编排器"""
        self.logger.info("关闭智能体编排引擎")
        self.executor.shutdown(wait=True)


# 导出主要类型
__all__ = [
    'PipelineStage', 'PipelineResult', 'DebateResult', 'AgentOrchestrator'
]