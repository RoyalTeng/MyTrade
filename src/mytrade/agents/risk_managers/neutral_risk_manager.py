"""
中性风险管理 - Neutral Risk Manager

平衡风险收益的风险管理视角：
- 追求稳健的风险收益比
- 基于量化指标做决策
- 平衡进攻与防守
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from ..protocols import (
    AgentInterface, AgentOutput, AgentContext, AgentRole, 
    AgentDecision, DecisionAction, AgentMetadata
)


class NeutralRiskManager(AgentInterface):
    """中性风险管理 - 平衡风险偏好"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # 中性风控参数
        self.risk_appetite = self.config.get('risk_appetite', 'medium')
        self.max_drawdown = self.config.get('max_drawdown', 0.10)
        self.leverage_tolerance = self.config.get('leverage_tolerance', 1.5)
        self.target_sharpe = self.config.get('target_sharpe', 1.0)
        
        # 中性风控特征
        self.balance_focus = True
        self.volatility_tolerance = 0.15  # 15% 年化波动率
        self.diversification_preference = True
    
    def run(self, context: AgentContext) -> AgentOutput:
        """执行中性风险管理分析"""
        start_time = datetime.now()
        
        try:
            # 1. 提取交易员决策
            trader_decision = self._extract_trader_decision(context)
            
            # 2. 中性风险评估
            risk_assessment = self._assess_balanced_risks(context, trader_decision)
            
            # 3. 风险收益平衡分析
            balance_analysis = self._analyze_risk_return_balance(context, trader_decision)
            
            # 4. 做出中性风控决策
            risk_decision = self._make_neutral_decision(
                trader_decision, risk_assessment, balance_analysis
            )
            
            # 5. 生成中性风控推理
            reasoning = self._generate_neutral_reasoning(
                risk_assessment, balance_analysis, risk_decision
            )
            
            execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            return AgentOutput(
                role=AgentRole.RISK_NEUTRAL,
                timestamp=datetime.now(),
                symbol=context.symbol,
                score=self._calculate_neutral_score(risk_assessment, balance_analysis),
                confidence=self._calculate_confidence(risk_assessment),
                decision=risk_decision,
                features={
                    'risk_return_ratio': balance_analysis.get('sharpe_estimate', 1.0),
                    'volatility_score': risk_assessment.get('volatility_score', 0.5),
                    'balance_rating': balance_analysis.get('balance_score', 0.5),
                    'diversification_need': 0.7,
                    'optimal_weight': risk_decision.weight
                },
                rationale=reasoning,
                metadata=AgentMetadata(
                    agent_id=f"neutral_risk_mgr_{context.symbol}",
                    version="2.0.0",
                    execution_time_ms=execution_time
                ),
                tags=['neutral_risk', 'balanced_approach'],
                alerts=self._generate_alerts(risk_assessment, risk_decision)
            )
            
        except Exception as e:
            self.logger.error(f"中性风险管理失败: {e}")
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
    
    def _assess_balanced_risks(self, context: AgentContext, trader_decision: Optional[Dict]) -> Dict[str, Any]:
        """平衡风险评估"""
        assessment = {
            'volatility_score': 0.5,
            'max_acceptable_loss': self.max_drawdown,
            'concentration_risk': 0.5,
            'market_risk': 0.5,
            'liquidity_risk': 0.4
        }
        
        if trader_decision:
            expected_return = trader_decision.get('expected_return', 0.1)
            max_loss = trader_decision.get('max_loss', 0.1)
            
            # 风险收益评估
            if expected_return / max(max_loss, 0.01) > 1.5:
                assessment['volatility_score'] = 0.4  # 可接受更多波动
            elif expected_return / max(max_loss, 0.01) < 0.8:
                assessment['volatility_score'] = 0.7  # 需要降低风险
        
        return assessment
    
    def _analyze_risk_return_balance(self, context: AgentContext, trader_decision: Optional[Dict]) -> Dict[str, Any]:
        """风险收益平衡分析"""
        analysis = {
            'balance_score': 0.5,
            'sharpe_estimate': 1.0,
            'optimal_allocation': 0.1
        }
        
        if trader_decision:
            expected_return = trader_decision.get('expected_return', 0.1)
            max_loss = trader_decision.get('max_loss', 0.1)
            
            # 估算夏普比率
            estimated_volatility = max_loss * 2  # 简化估算
            sharpe_estimate = max(0.1, expected_return / max(estimated_volatility, 0.01))
            analysis['sharpe_estimate'] = sharpe_estimate
            
            # 基于夏普比率调整配置
            if sharpe_estimate > self.target_sharpe:
                analysis['balance_score'] = 0.7
                analysis['optimal_allocation'] = min(0.15, trader_decision.get('weight', 0.05) * 1.2)
            else:
                analysis['balance_score'] = 0.3
                analysis['optimal_allocation'] = max(0.02, trader_decision.get('weight', 0.05) * 0.8)
        
        return analysis
    
    def _make_neutral_decision(self, trader_decision: Optional[Dict], risk_assessment: Dict, balance_analysis: Dict) -> AgentDecision:
        """做出中性风控决策"""
        if not trader_decision:
            return AgentDecision(
                action=DecisionAction.HOLD,
                weight=0.0,
                confidence=0.5,
                reasoning="无交易决策，保持平衡",
                risk_level="medium",
                expected_return=0.0,
                max_loss=0.0
            )
        
        # 基于平衡分析调整
        base_weight = trader_decision.get('weight', 0.05)
        optimal_weight = balance_analysis.get('optimal_allocation', base_weight)
        
        # 风险调整
        if risk_assessment.get('volatility_score', 0.5) > 0.6:
            optimal_weight *= 0.8  # 降低仓位
        
        return AgentDecision(
            action=trader_decision.get('action', DecisionAction.HOLD),
            weight=min(0.12, optimal_weight),
            confidence=min(0.8, trader_decision.get('confidence', 0.5) * 1.1),
            reasoning="中性风控：平衡风险与收益",
            risk_level="medium",
            expected_return=trader_decision.get('expected_return', 0.1),
            max_loss=min(self.max_drawdown, trader_decision.get('max_loss', 0.1))
        )
    
    def _calculate_neutral_score(self, risk_assessment: Dict, balance_analysis: Dict) -> float:
        """计算中性评分"""
        balance_score = balance_analysis.get('balance_score', 0.5)
        volatility_score = 1 - risk_assessment.get('volatility_score', 0.5)  # 转换为正向分数
        return round((balance_score + volatility_score) / 2, 3)
    
    def _calculate_confidence(self, risk_assessment: Dict) -> float:
        """计算置信度"""
        return 0.7  # 中性风控置信度中等
    
    def _generate_neutral_reasoning(self, risk_assessment: Dict, balance_analysis: Dict, decision: AgentDecision) -> str:
        """生成推理"""
        parts = [
            f"风险收益平衡评分：{balance_analysis.get('balance_score', 0.5):.2f}",
            f"建议仓位：{decision.weight:.1%}",
            "采用中性风控策略"
        ]
        return "；".join(parts)
    
    def _generate_alerts(self, risk_assessment: Dict, decision: AgentDecision) -> List[str]:
        """生成告警"""
        alerts = []
        if decision.weight > 0.15:
            alerts.append("仓位可能过于集中")
        return alerts
    
    def _create_error_output(self, context: AgentContext, error_msg: str) -> AgentOutput:
        """创建错误输出"""
        return AgentOutput(
            role=AgentRole.RISK_NEUTRAL,
            timestamp=datetime.now(),
            symbol=context.symbol,
            score=None,
            confidence=0.0,
            features={},
            rationale=f"中性风险管理失败: {error_msg}",
            metadata=AgentMetadata(
                agent_id=f"neutral_risk_mgr_{context.symbol}",
                version="2.0.0"
            ),
            alerts=[f"风控异常: {error_msg}"]
        )