"""
激进风险管理 - Aggressive Risk Manager

高风险偏好的风险管理视角：
- 追求高收益，容忍更高波动
- 支持集中持仓和杠杆策略
- 关注机会成本而非绝对风险
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from ..protocols import (
    AgentInterface, AgentOutput, AgentContext, AgentRole, 
    AgentDecision, DecisionAction, AgentMetadata
)


class AggressiveRiskManager(AgentInterface):
    """激进风险管理 - 高风险偏好"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # 激进风控参数
        self.risk_appetite = self.config.get('risk_appetite', 'high')
        self.max_drawdown = self.config.get('max_drawdown', 0.15)
        self.leverage_tolerance = self.config.get('leverage_tolerance', 2.0)
        self.concentration_limit = self.config.get('concentration_limit', 0.3)
        
        # 激进风控特征
        self.opportunity_focus = True
        self.volatility_tolerance = 0.25  # 25% 年化波动率容忍度
        self.beta_preference = 1.5  # 偏好高Beta标的
    
    def run(self, context: AgentContext) -> AgentOutput:
        """执行激进风险管理分析
        
        Args:
            context: 分析上下文，包含交易员决策
            
        Returns:
            AgentOutput: 激进风险管理结果  
        """
        start_time = datetime.now()
        
        try:
            # 1. 提取交易员决策
            trader_decision = self._extract_trader_decision(context)
            
            # 2. 激进风险评估
            risk_assessment = self._assess_aggressive_risks(context, trader_decision)
            
            # 3. 机会成本分析
            opportunity_analysis = self._analyze_opportunity_cost(context, trader_decision)
            
            # 4. 杠杆与集中度建议
            leverage_advice = self._provide_leverage_advice(context, trader_decision)
            
            # 5. 做出激进风控决策
            risk_decision = self._make_aggressive_decision(
                trader_decision, risk_assessment, opportunity_analysis, leverage_advice
            )
            
            # 6. 生成激进风控推理
            reasoning = self._generate_aggressive_reasoning(
                risk_assessment, opportunity_analysis, leverage_advice, risk_decision
            )
            
            # 7. 构造标准化输出
            execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            return AgentOutput(
                role=AgentRole.RISK_SEEKING,
                timestamp=datetime.now(),
                symbol=context.symbol,
                score=self._calculate_aggressive_score(risk_assessment, opportunity_analysis),
                confidence=self._calculate_confidence(risk_assessment, opportunity_analysis),
                decision=risk_decision,
                features={
                    'risk_appetite_level': 0.8,
                    'volatility_tolerance': self.volatility_tolerance,
                    'leverage_recommendation': leverage_advice.get('recommended_leverage', 1.0),
                    'concentration_comfort': leverage_advice.get('position_size', 0.1),
                    'opportunity_score': opportunity_analysis.get('score', 0.5),
                    'downside_tolerance': risk_assessment.get('max_acceptable_loss', 0.15)
                },
                rationale=reasoning,
                metadata=AgentMetadata(
                    agent_id=f"aggressive_risk_mgr_{context.symbol}",
                    version="2.0.0",
                    execution_time_ms=execution_time,
                    data_sources=['trader_decision', 'market_volatility']
                ),
                tags=self._generate_tags(risk_assessment, opportunity_analysis),
                alerts=self._generate_alerts(risk_assessment, risk_decision)
            )
            
        except Exception as e:
            self.logger.error(f"激进风险管理失败: {e}")
            
            # 返回错误状态的输出
            return AgentOutput(
                role=AgentRole.RISK_SEEKING,
                timestamp=datetime.now(),
                symbol=context.symbol,
                score=None,
                confidence=0.0,
                features={},
                rationale=f"激进风险管理失败: {str(e)}",
                metadata=AgentMetadata(
                    agent_id=f"aggressive_risk_mgr_{context.symbol}",
                    version="2.0.0"
                ),
                alerts=[f"风控异常: {str(e)}"]
            )
    
    def _extract_trader_decision(self, context: AgentContext) -> Optional[Dict[str, Any]]:
        """提取交易员决策"""
        for output in context.previous_outputs:
            if output.role == AgentRole.TRADER.value and output.decision:
                return {
                    'action': output.decision.action,
                    'weight': output.decision.weight,
                    'confidence': output.decision.confidence,
                    'expected_return': output.decision.expected_return,
                    'max_loss': output.decision.max_loss,
                    'reasoning': output.decision.reasoning
                }
        
        # 如果没有交易员决策，基于综合评分推断
        consensus_scores = [o.score for o in context.previous_outputs if o.score is not None]
        if consensus_scores:
            avg_score = sum(consensus_scores) / len(consensus_scores)
            return {
                'action': DecisionAction.BUY if avg_score > 0.6 else DecisionAction.SELL if avg_score < 0.4 else DecisionAction.HOLD,
                'weight': min(0.15, avg_score * 0.2),  # 激进一点
                'confidence': 0.6,
                'expected_return': max(0.1, avg_score * 0.25),
                'max_loss': 0.12,
                'reasoning': "基于综合评分推断"
            }
        
        return None
    
    def _assess_aggressive_risks(
        self, 
        context: AgentContext, 
        trader_decision: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """激进风险评估"""
        assessment = {
            'max_acceptable_loss': self.max_drawdown,
            'volatility_score': 0.6,
            'concentration_risk': 0.4,
            'liquidity_risk': 0.3,
            'downside_protection': 0.2  # 激进风控不太关注下行保护
        }
        
        if not trader_decision:
            return assessment
        
        # 基于交易决策调整风险评估
        expected_return = trader_decision.get('expected_return', 0.1)
        max_loss = trader_decision.get('max_loss', 0.1)
        
        # 风险收益比分析
        risk_reward_ratio = expected_return / max(max_loss, 0.01)
        
        if risk_reward_ratio > 2.0:
            # 风险收益比好，可以接受更高风险
            assessment['max_acceptable_loss'] = min(0.2, max_loss * 1.5)
            assessment['volatility_score'] = 0.4  # 较低的风险分数意味着更能接受
            
        # 基于市场环境调整
        market_scores = []
        for output in context.previous_outputs:
            if output.role in [AgentRole.TECHNICAL.value, AgentRole.SENTIMENT.value] and output.score:
                market_scores.append(output.score)
        
        if market_scores and sum(market_scores) / len(market_scores) > 0.7:
            # 市场环境良好，降低风险担忧
            assessment['concentration_risk'] = 0.3
            assessment['liquidity_risk'] = 0.2
        
        return assessment
    
    def _analyze_opportunity_cost(
        self, 
        context: AgentContext, 
        trader_decision: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """分析机会成本"""
        analysis = {
            'score': 0.5,
            'missed_opportunities': [],
            'market_timing': 0.6,
            'sector_rotation': 0.5
        }
        
        if not trader_decision:
            return analysis
        
        action = trader_decision.get('action')
        expected_return = trader_decision.get('expected_return', 0.1)
        
        # HOLD动作的机会成本分析
        if action == DecisionAction.HOLD:
            if expected_return > 0.15:
                analysis['missed_opportunities'].append("错失高收益机会")
                analysis['score'] = 0.3  # 机会成本高
            
        # 保守仓位的机会成本
        weight = trader_decision.get('weight', 0.05)
        if weight < 0.08 and expected_return > 0.12:
            analysis['missed_opportunities'].append("仓位过于保守")
            analysis['score'] = 0.4
        
        # 市场趋势分析
        technical_score = None
        for output in context.previous_outputs:
            if output.role == AgentRole.TECHNICAL.value and output.score:
                technical_score = output.score
                break
        
        if technical_score and technical_score > 0.7:
            analysis['market_timing'] = 0.8  # 市场时机好
            if action in [DecisionAction.HOLD, DecisionAction.SELL]:
                analysis['missed_opportunities'].append("错失技术突破机会")
        
        return analysis
    
    def _provide_leverage_advice(
        self, 
        context: AgentContext, 
        trader_decision: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """提供杠杆建议"""
        advice = {
            'recommended_leverage': 1.0,
            'position_size': 0.1,
            'concentration_acceptable': True
        }
        
        if not trader_decision:
            return advice
        
        expected_return = trader_decision.get('expected_return', 0.1)
        confidence = trader_decision.get('confidence', 0.5)
        
        # 基于期望收益和置信度建议杠杆
        if expected_return > 0.2 and confidence > 0.8:
            advice['recommended_leverage'] = min(self.leverage_tolerance, 2.0)
            advice['position_size'] = min(self.concentration_limit, 0.25)
        elif expected_return > 0.15 and confidence > 0.7:
            advice['recommended_leverage'] = min(self.leverage_tolerance, 1.5)
            advice['position_size'] = min(self.concentration_limit, 0.15)
        
        # 基于市场环境调整
        sentiment_positive = False
        for output in context.previous_outputs:
            if output.role == AgentRole.SENTIMENT.value and output.score and output.score > 0.6:
                sentiment_positive = True
                break
        
        if sentiment_positive:
            advice['recommended_leverage'] *= 1.2
            advice['position_size'] *= 1.1
        
        # 确保不超过限制
        advice['recommended_leverage'] = min(advice['recommended_leverage'], self.leverage_tolerance)
        advice['position_size'] = min(advice['position_size'], self.concentration_limit)
        
        return advice
    
    def _make_aggressive_decision(
        self,
        trader_decision: Optional[Dict[str, Any]],
        risk_assessment: Dict[str, Any],
        opportunity_analysis: Dict[str, Any],
        leverage_advice: Dict[str, Any]
    ) -> AgentDecision:
        """做出激进风控决策"""
        
        if not trader_decision:
            # 没有交易决策时，保持观望
            return AgentDecision(
                action=DecisionAction.HOLD,
                weight=0.0,
                confidence=0.5,
                reasoning="无交易决策输入，保持观望",
                risk_level="low",
                expected_return=0.0,
                max_loss=0.0,
                time_horizon="1M"
            )
        
        # 基础决策信息
        base_action = trader_decision.get('action', DecisionAction.HOLD)
        base_weight = trader_decision.get('weight', 0.05)
        base_confidence = trader_decision.get('confidence', 0.5)
        
        # 激进调整
        aggressive_weight = base_weight
        aggressive_action = base_action
        
        # 增强仓位（如果机会成本高）
        if opportunity_analysis.get('score', 0.5) < 0.4:  # 机会成本高
            aggressive_weight = min(leverage_advice.get('position_size', 0.1), base_weight * 1.5)
            
        # 如果风险可接受，增强行动
        max_acceptable_loss = risk_assessment.get('max_acceptable_loss', 0.1)
        if base_action == DecisionAction.HOLD and opportunity_analysis.get('score', 0.5) < 0.3:
            if trader_decision.get('expected_return', 0.1) > max_acceptable_loss * 2:
                aggressive_action = DecisionAction.BUY
                aggressive_weight = leverage_advice.get('position_size', 0.1)
        
        # 提升置信度（激进风控更果断）
        aggressive_confidence = min(0.9, base_confidence + 0.1)
        
        return AgentDecision(
            action=aggressive_action,
            weight=aggressive_weight,
            confidence=aggressive_confidence,
            reasoning=f"激进风控：{base_action.value}→{aggressive_action.value}，仓位{base_weight:.2%}→{aggressive_weight:.2%}",
            risk_level="high",
            expected_return=trader_decision.get('expected_return', 0.1),
            max_loss=max_acceptable_loss,
            time_horizon="3M"
        )
    
    def _calculate_aggressive_score(
        self,
        risk_assessment: Dict[str, Any],
        opportunity_analysis: Dict[str, Any]
    ) -> float:
        """计算激进风控评分"""
        
        # 基础评分偏向乐观
        base_score = 0.6
        
        # 机会成本分析影响
        opportunity_score = opportunity_analysis.get('score', 0.5)
        if opportunity_score < 0.4:  # 机会成本高，更积极
            base_score += 0.2
        elif opportunity_score > 0.7:  # 机会成本低，相对保守
            base_score -= 0.1
        
        # 风险收益比影响
        max_loss = risk_assessment.get('max_acceptable_loss', 0.1)
        if max_loss > 0.12:  # 可接受损失较大，更激进
            base_score += 0.1
        
        return round(min(max(base_score, 0.3), 0.85), 3)
    
    def _calculate_confidence(
        self,
        risk_assessment: Dict[str, Any],
        opportunity_analysis: Dict[str, Any]
    ) -> float:
        """计算置信度"""
        base_confidence = 0.75  # 激进风控相对自信
        
        # 机会成本清晰度影响置信度
        if len(opportunity_analysis.get('missed_opportunities', [])) > 0:
            base_confidence += 0.1
        
        return round(min(base_confidence, 0.9), 3)
    
    def _generate_aggressive_reasoning(
        self,
        risk_assessment: Dict[str, Any],
        opportunity_analysis: Dict[str, Any],
        leverage_advice: Dict[str, Any],
        risk_decision: AgentDecision
    ) -> str:
        """生成激进风控推理"""
        
        reasoning_parts = []
        
        # 风险承受能力
        max_loss = risk_assessment.get('max_acceptable_loss', 0.1)
        reasoning_parts.append(f"可承受{max_loss:.1%}最大损失")
        
        # 机会成本分析
        missed_opps = opportunity_analysis.get('missed_opportunities', [])
        if missed_opps:
            reasoning_parts.append(f"识别到{len(missed_opps)}个机会成本")
        
        # 仓位建议
        position_size = leverage_advice.get('position_size', 0.1)
        if position_size > 0.1:
            reasoning_parts.append(f"建议仓位{position_size:.1%}")
        
        # 杠杆建议
        leverage = leverage_advice.get('recommended_leverage', 1.0)
        if leverage > 1.0:
            reasoning_parts.append(f"可考虑{leverage:.1f}倍杠杆")
        
        # 最终建议
        action = risk_decision.action
        if action == DecisionAction.BUY:
            reasoning_parts.append("激进建议：积极加仓")
        elif action == DecisionAction.INCREASE:
            reasoning_parts.append("激进建议：增加仓位")
        else:
            reasoning_parts.append("维持当前策略")
        
        return "；".join(reasoning_parts)
    
    def _generate_tags(
        self,
        risk_assessment: Dict[str, Any],
        opportunity_analysis: Dict[str, Any]
    ) -> List[str]:
        """生成标签"""
        tags = ['aggressive_risk', 'high_risk_appetite']
        
        if risk_assessment.get('max_acceptable_loss', 0.1) > 0.15:
            tags.append('high_loss_tolerance')
        
        if len(opportunity_analysis.get('missed_opportunities', [])) > 1:
            tags.append('opportunity_focused')
        
        return tags
    
    def _generate_alerts(
        self,
        risk_assessment: Dict[str, Any],
        risk_decision: AgentDecision
    ) -> List[str]:
        """生成告警"""
        alerts = []
        
        # 极端仓位告警
        if risk_decision.weight > 0.2:
            alerts.append(f"仓位{risk_decision.weight:.1%}超过常规建议")
        
        # 高风险告警
        if risk_assessment.get('max_acceptable_loss', 0.1) > 0.18:
            alerts.append("风险承受度接近极限")
        
        return alerts