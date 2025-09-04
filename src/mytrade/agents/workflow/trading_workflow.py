"""
交易工作流

协调多个Agent进行交易决策分析
参考TradingAgents的工作流设计，实现中文本地化
"""

import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import asyncio
import concurrent.futures

from .workflow_state import WorkflowState, WorkflowResult, WorkflowStage, AgentResult
from ..base_agent import BaseAgent


class TradingWorkflow:
    """交易工作流管理器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """初始化工作流
        
        Args:
            config: 工作流配置
        """
        self.config = config or {}
        self.agents: Dict[str, BaseAgent] = {}
        self.logger = logging.getLogger("workflow.trading")
        
        # 工作流配置
        self.max_execution_time = self.config.get('max_execution_time', 300)  # 5分钟
        self.enable_parallel = self.config.get('enable_parallel', True)
        self.enable_debate = self.config.get('enable_debate', True)
        
        self.logger.info("交易工作流管理器初始化完成")
    
    def register_agent(self, agent: BaseAgent):
        """注册Agent到工作流"""
        self.agents[agent.agent_id] = agent
        self.logger.info(f"Agent已注册: {agent.agent_id} ({agent.agent_type})")
    
    def register_agents(self, agents: List[BaseAgent]):
        """批量注册Agent"""
        for agent in agents:
            self.register_agent(agent)
    
    async def execute(self, symbol: str, input_data: Dict[str, Any]) -> WorkflowResult:
        """执行交易工作流
        
        Args:
            symbol: 股票代码
            input_data: 输入数据
            
        Returns:
            WorkflowResult: 工作流结果
        """
        workflow_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        # 创建工作流状态
        state = WorkflowState(
            workflow_id=workflow_id,
            symbol=symbol,
            input_data=input_data
        )
        
        try:
            self.logger.info(f"开始执行交易工作流: {symbol} (ID: {workflow_id})")
            
            # 第一阶段：分析师并行分析
            state.set_stage(WorkflowStage.ANALYZING)
            await self._execute_analysts(state)
            
            # 第二阶段：研究员辩论
            if self.enable_debate:
                state.set_stage(WorkflowStage.RESEARCHING)
                await self._execute_researchers(state)
            
            # 第三阶段：最终决策
            state.set_stage(WorkflowStage.DECIDING)
            result = await self._make_final_decision(state)
            
            state.set_stage(WorkflowStage.COMPLETED)
            
            # 计算执行时间
            execution_time = (datetime.now() - start_time).total_seconds()
            result.execution_time = execution_time
            
            self.logger.info(f"工作流执行完成: {symbol}, 决策: {result.action}, 耗时: {execution_time:.2f}s")
            
            return result
            
        except Exception as e:
            state.add_error(str(e))
            state.set_stage(WorkflowStage.FAILED)
            self.logger.error(f"工作流执行失败: {symbol}, 错误: {e}")
            raise
    
    async def _execute_analysts(self, state: WorkflowState):
        """执行分析师阶段"""
        analyst_types = ['技术分析师', '基本面分析师', '情感分析师', '市场分析师']
        analysts = [agent for agent in self.agents.values() 
                   if agent.agent_type in analyst_types]
        
        if not analysts:
            raise ValueError("未找到可用的分析师Agent")
        
        self.logger.info(f"开始分析师阶段，共 {len(analysts)} 个分析师")
        
        if self.enable_parallel:
            # 并行执行
            tasks = []
            for analyst in analysts:
                task = self._execute_agent_async(analyst, state.input_data)
                tasks.append(task)
            
            # 等待所有分析师完成
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 处理结果
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    self.logger.error(f"分析师 {analysts[i].agent_id} 执行失败: {result}")
                    state.add_error(f"分析师 {analysts[i].agent_id} 执行失败: {result}")
                else:
                    state.add_agent_result(result)
        else:
            # 串行执行
            for analyst in analysts:
                try:
                    result = await self._execute_agent_async(analyst, state.input_data)
                    state.add_agent_result(result)
                except Exception as e:
                    self.logger.error(f"分析师 {analyst.agent_id} 执行失败: {e}")
                    state.add_error(f"分析师 {analyst.agent_id} 执行失败: {e}")
    
    async def _execute_researchers(self, state: WorkflowState):
        """执行研究员阶段"""
        researcher_types = ['多头研究员', '空头研究员']
        researchers = [agent for agent in self.agents.values() 
                      if agent.agent_type in researcher_types]
        
        if len(researchers) < 2:
            self.logger.warning("研究员数量不足，跳过辩论阶段")
            return
        
        self.logger.info(f"开始研究员辩论阶段，共 {len(researchers)} 个研究员")
        
        # 准备辩论输入数据
        debate_input = {
            'symbol': state.symbol,
            'analyst_results': list(state.agent_results.values()),
            'original_data': state.input_data
        }
        
        # 执行研究员分析
        for researcher in researchers:
            try:
                result = await self._execute_agent_async(researcher, debate_input)
                state.add_agent_result(result)
            except Exception as e:
                self.logger.error(f"研究员 {researcher.agent_id} 执行失败: {e}")
                state.add_error(f"研究员 {researcher.agent_id} 执行失败: {e}")
    
    async def _make_final_decision(self, state: WorkflowState) -> WorkflowResult:
        """做最终决策"""
        self.logger.info("开始最终决策阶段")
        
        # 寻找决策管理器
        manager_types = ['研究经理', '风险经理', '交易经理']
        managers = [agent for agent in self.agents.values() 
                   if agent.agent_type in manager_types]
        
        if not managers:
            # 如果没有专门的管理器，使用内置决策逻辑
            return self._make_consensus_decision(state)
        
        # 准备决策输入数据
        decision_input = {
            'symbol': state.symbol,
            'all_results': list(state.agent_results.values()),
            'original_data': state.input_data
        }
        
        # 执行管理器决策
        final_result = None
        for manager in managers:
            try:
                result = await self._execute_agent_async(manager, decision_input)
                state.add_agent_result(result)
                
                # 使用最后一个管理器的结果作为最终结果
                final_result = result
                
            except Exception as e:
                self.logger.error(f"管理器 {manager.agent_id} 执行失败: {e}")
                state.add_error(f"管理器 {manager.agent_id} 执行失败: {e}")
        
        if final_result:
            return self._convert_to_workflow_result(state, final_result)
        else:
            return self._make_consensus_decision(state)
    
    async def _execute_agent_async(self, agent: BaseAgent, input_data: Dict[str, Any]) -> AgentResult:
        """异步执行单个Agent"""
        start_time = datetime.now()
        
        def _execute_sync():
            return agent.process(input_data)
        
        # 在线程池中执行同步方法
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            response = await loop.run_in_executor(executor, _execute_sync)
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return AgentResult(
            agent_id=agent.agent_id,
            agent_type=agent.agent_type,
            content=response.content,
            confidence=response.confidence,
            reasoning=response.reasoning,
            data=response.data,
            timestamp=response.timestamp,
            execution_time=execution_time
        )
    
    def _make_consensus_decision(self, state: WorkflowState) -> WorkflowResult:
        """基于共识的决策"""
        if not state.agent_results:
            raise ValueError("没有可用的分析结果进行决策")
        
        # 统计各种建议
        buy_votes = 0
        sell_votes = 0
        hold_votes = 0
        total_confidence = 0
        all_reasoning = []
        
        for result in state.agent_results.values():
            content_lower = result.content.lower()
            
            # 简单的关键词匹配来判断建议
            if 'buy' in content_lower or '买入' in content_lower or '看多' in content_lower:
                buy_votes += result.confidence
            elif 'sell' in content_lower or '卖出' in content_lower or '看空' in content_lower:
                sell_votes += result.confidence
            else:
                hold_votes += result.confidence
            
            total_confidence += result.confidence
            all_reasoning.extend(result.reasoning)
        
        # 决定最终行动
        if buy_votes > sell_votes and buy_votes > hold_votes:
            action = "BUY"
            confidence = buy_votes / len(state.agent_results)
        elif sell_votes > buy_votes and sell_votes > hold_votes:
            action = "SELL"
            confidence = sell_votes / len(state.agent_results)
        else:
            action = "HOLD"
            confidence = hold_votes / len(state.agent_results)
        
        # 平均置信度
        avg_confidence = total_confidence / len(state.agent_results)
        
        return WorkflowResult(
            workflow_id=state.workflow_id,
            symbol=state.symbol,
            action=action,
            confidence=min(confidence, avg_confidence),
            reasoning=list(set(all_reasoning)),  # 去重
            agents_used=[result.agent_id for result in state.agent_results.values()],
            metadata={'decision_method': 'consensus', 'votes': {'buy': buy_votes, 'sell': sell_votes, 'hold': hold_votes}}
        )
    
    def _convert_to_workflow_result(self, state: WorkflowState, final_result: AgentResult) -> WorkflowResult:
        """转换Agent结果为工作流结果"""
        # 解析最终决策
        action = self._extract_action_from_content(final_result.content)
        
        # 收集各类分析结果
        technical_analysis = {}
        fundamental_analysis = {}
        sentiment_analysis = {}
        risk_assessment = {}
        
        for result in state.agent_results.values():
            if result.agent_type == '技术分析师':
                technical_analysis.update(result.data)
            elif result.agent_type == '基本面分析师':
                fundamental_analysis.update(result.data)
            elif result.agent_type == '情感分析师':
                sentiment_analysis.update(result.data)
            elif result.agent_type in ['风险经理', '风险分析师']:
                risk_assessment.update(result.data)
        
        return WorkflowResult(
            workflow_id=state.workflow_id,
            symbol=state.symbol,
            action=action,
            confidence=final_result.confidence,
            reasoning=final_result.reasoning,
            technical_analysis=technical_analysis,
            fundamental_analysis=fundamental_analysis,
            sentiment_analysis=sentiment_analysis,
            risk_assessment=risk_assessment,
            agents_used=[result.agent_id for result in state.agent_results.values()]
        )
    
    def _extract_action_from_content(self, content: str) -> str:
        """从内容中提取行动建议"""
        content_lower = content.lower()
        
        # 优先级：卖出 > 买入 > 持有
        if any(word in content_lower for word in ['sell', '卖出', '减持', '看空']):
            return "SELL"
        elif any(word in content_lower for word in ['buy', '买入', '增持', '看多']):
            return "BUY"
        else:
            return "HOLD"