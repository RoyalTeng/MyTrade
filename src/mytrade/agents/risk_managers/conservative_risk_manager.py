"""
保守风险管理 - Conservative Risk Manager

低风险偏好的风险管理视角：
- 优先保本，严控回撤
- 重视流动性和分散化
- 对不确定性保持谨慎
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from ..protocols import (
    AgentInterface, AgentOutput, AgentContext, AgentRole, 
    AgentDecision, DecisionAction, AgentMetadata
)


class ConservativeRiskManager(AgentInterface):
    """保守风险管理 - 低风险偏好"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # 保守风控参数
        self.risk_appetite = self.config.get('risk_appetite', 'low')
        self.max_drawdown = self.config.get('max_drawdown', 0.05)
        self.leverage_tolerance = self.config.get('leverage_tolerance', 1.0)
        self.min_confidence = self.config.get('min_confidence', 0.8)
        
        # 保守风控特征
        self.capital_preservation = True
        self.volatility_tolerance = 0.08  # 8% 年化波动率
        self.liquidity_focus = True
    
    def run(self, context: AgentContext) -> AgentOutput:
        """执行保守风险管理分析"""
        start_time = datetime.now()
        
        try:
            # 1. 提取交易员决策
            trader_decision = self._extract_trader_decision(context)
            
            # 2. 保守风险评估
            risk_assessment = self._assess_conservative_risks(context, trader_decision)
            
            # 3. 资本保全分析
            preservation_analysis = self._analyze_capital_preservation(context, trader_decision)
            
            # 4. 做出保守风控决策
            risk_decision = self._make_conservative_decision(
                trader_decision, risk_assessment, preservation_analysis
            )
            
            # 5. 生成保守风控推理
            reasoning = self._generate_conservative_reasoning(
                risk_assessment, preservation_analysis, risk_decision
            )
            
            execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            return AgentOutput(
                role=AgentRole.RISK_CONSERVATIVE,
                timestamp=datetime.now(),
                symbol=context.symbol,
                score=self._calculate_conservative_score(risk_assessment, preservation_analysis),
                confidence=self._calculate_confidence(risk_assessment, preservation_analysis),
                decision=risk_decision,
                features={
                    'capital_safety_score': preservation_analysis.get('safety_score', 0.8),
                    'max_tolerable_loss': self.max_drawdown,
                    'confidence_threshold': self.min_confidence,
                    'liquidity_priority': 0.9,
                    'conservative_weight': risk_decision.weight
                },
                rationale=reasoning,
                metadata=AgentMetadata(
                    agent_id=f"conservative_risk_mgr_{context.symbol}",
                    version="2.0.0",
                    execution_time_ms=execution_time
                ),
                tags=['conservative_risk', 'capital_preservation'],
                alerts=self._generate_alerts(risk_assessment, risk_decision)
            )
            
        except Exception as e:
            self.logger.error(f"保守风险管理失败: {e}")
            return self._create_error_output(context, str(e))
    
    def _extract_trader_decision(self, context: AgentContext) -> Optional[Dict[str, Any]]:
        """提取交易员决策"""
        for output in context.previous_outputs:
            if output.role == AgentRole.TRADER.value and output.decision:
                return {
                    'action': output.decision.action,
                    'weight': output.decision.weight,
                    'confidence': output.decision.confidence,
                    'expected_return': output.decision.expected_return,
                    'max_loss': output.decision.max_loss
                }
        return None
    
    def _assess_conservative_risks(self, context: AgentContext, trader_decision: Optional[Dict]) -> Dict[str, Any]:
        """保守风险评估"""
        assessment = {
            'downside_risk': 0.8,  # 高度关注下行风险
            'volatility_concern': 0.7,
            'uncertainty_level': 0.6,
            'liquidity_concern': 0.5,
            'max_acceptable_loss': self.max_drawdown
        }
        
        if trader_decision:
            confidence = trader_decision.get('confidence', 0.5)
            max_loss = trader_decision.get('max_loss', 0.1)
            
            # 低置信度增加担忧
            if confidence < self.min_confidence:
                assessment['uncertainty_level'] = 0.8
                assessment['downside_risk'] = 0.9
            
            # 损失超出承受范围
            if max_loss > self.max_drawdown:
                assessment['volatility_concern'] = 0.9
                assessment['max_acceptable_loss'] = self.max_drawdown * 0.8  # 更加保守
        
        return assessment
    
    def _analyze_capital_preservation(self, context: AgentContext, trader_decision: Optional[Dict]) -> Dict[str, Any]:
        """资本保全分析"""
        analysis = {
            'safety_score': 0.8,
            'preservation_priority': 0.9,
            'acceptable_exposure': 0.03  # 最大3%仓位
        }
        
        if trader_decision:
            expected_return = trader_decision.get('expected_return', 0.1)
            max_loss = trader_decision.get('max_loss', 0.1)
            confidence = trader_decision.get('confidence', 0.5)
            
            # 风险收益不匹配时降低安全分数
            if max_loss > expected_return * 0.5:  # 损失超过预期收益50%
                analysis['safety_score'] = 0.5
                analysis['acceptable_exposure'] = 0.02
            
            # 高置信度可以适当增加仓位
            if confidence > 0.8 and max_loss <= self.max_drawdown:
                analysis['acceptable_exposure'] = 0.05
        
        return analysis
    
    def _make_conservative_decision(self, trader_decision: Optional[Dict], risk_assessment: Dict, preservation_analysis: Dict) -> AgentDecision:
        """做出保守风控决策"""
        if not trader_decision:
            return AgentDecision(
                action=DecisionAction.HOLD,
                weight=0.0,
                confidence=0.6,
                reasoning="无交易决策，保守观望",
                risk_level="low",
                expected_return=0.0,
                max_loss=0.0
            )
        
        base_action = trader_decision.get('action', DecisionAction.HOLD)
        base_weight = trader_decision.get('weight', 0.05)
        base_confidence = trader_decision.get('confidence', 0.5)
        
        # 保守调整
        conservative_weight = min(
            preservation_analysis.get('acceptable_exposure', 0.03),
            base_weight * 0.6  # 大幅削减仓位
        )
        
        # 低置信度时更加保守
        if base_confidence < self.min_confidence:
            conservative_weight *= 0.5
            if base_action == DecisionAction.BUY:
                base_action = DecisionAction.HOLD  # 降级为观望
        
        # 高风险时拒绝执行
        if trader_decision.get('max_loss', 0.1) > self.max_drawdown * 1.2:
            base_action = DecisionAction.HOLD
            conservative_weight = 0.0
        
        return AgentDecision(
            action=base_action,
            weight=conservative_weight,
            confidence=min(0.7, base_confidence),  # 保守风控不会过度自信
            reasoning="保守风控：严控风险，优先保本",
            risk_level="low",
            expected_return=max(0.02, trader_decision.get('expected_return', 0.1) * 0.7),  # 降低预期
            max_loss=min(self.max_drawdown, trader_decision.get('max_loss', 0.1)),
            time_horizon="6M"  # 更长时间窗口
        )
    
    def _calculate_conservative_score(self, risk_assessment: Dict, preservation_analysis: Dict) -> float:
        """计算保守评分"""
        # 保守风控偏向较低评分
        safety_score = preservation_analysis.get('safety_score', 0.8)
        downside_concern = 1 - risk_assessment.get('downside_risk', 0.5)
        
        conservative_score = (safety_score * 0.7 + downside_concern * 0.3) * 0.8  # 整体偏保守
        return round(min(max(conservative_score, 0.1), 0.7), 3)  # 不会给出极端乐观分数
    
    def _calculate_confidence(self, risk_assessment: Dict, preservation_analysis: Dict) -> float:
        """计算置信度"""
        base_confidence = 0.65
        
        # 安全分数高时置信度提升
        if preservation_analysis.get('safety_score', 0.8) > 0.8:
            base_confidence += 0.1
        
        # 不确定性高时置信度降低
        if risk_assessment.get('uncertainty_level', 0.5) > 0.7:
            base_confidence -= 0.15
        
        return round(min(max(base_confidence, 0.3), 0.8), 3)  # 保守风控不会过度自信
    
    def _generate_conservative_reasoning(self, risk_assessment: Dict, preservation_analysis: Dict, decision: AgentDecision) -> str:
        """生成保守推理"""
        parts = []
        
        # 风险关注
        downside_risk = risk_assessment.get('downside_risk', 0.5)
        if downside_risk > 0.7:
            parts.append("下行风险较高，需要谨慎")
        
        # 资本保护
        parts.append(f"资本安全评分：{preservation_analysis.get('safety_score', 0.8):.2f}")
        
        # 仓位控制
        if decision.weight < 0.03:
            parts.append("采用最小仓位策略")
        elif decision.weight < 0.05:
            parts.append("保守仓位控制")
        
        # 最终建议
        if decision.action == DecisionAction.HOLD:
            parts.append("建议保持观望")
        else:
            parts.append(f"谨慎{decision.action.value.lower()}")
        
        return "；".join(parts)
    
    def _generate_alerts(self, risk_assessment: Dict, decision: AgentDecision) -> List[str]:
        """生成告警"""
        alerts = []
        
        # 仓位告警
        if decision.weight > 0.05:
            alerts.append(f"保守策略建议仓位不超过5%，当前{decision.weight:.1%}")
        
        # 风险告警
        if risk_assessment.get('uncertainty_level', 0.5) > 0.8:
            alerts.append("市场不确定性过高，建议暂缓投资")
        
        # 置信度告警
        if decision.confidence < 0.4:
            alerts.append("决策置信度过低，建议重新评估")
        
        return alerts
    
    def _create_error_output(self, context: AgentContext, error_msg: str) -> AgentOutput:
        """创建错误输出"""
        return AgentOutput(
            role=AgentRole.RISK_CONSERVATIVE,
            timestamp=datetime.now(),
            symbol=context.symbol,
            score=None,
            confidence=0.0,
            features={},
            rationale=f"保守风险管理失败: {error_msg}",
            metadata=AgentMetadata(
                agent_id=f"conservative_risk_mgr_{context.symbol}",
                version="2.0.0"
            ),
            alerts=[f"风控异常: {error_msg}"]
        )