"""
多头研究员 - Bull Researcher

专门挖掘和放大股票的积极因素：
- 基于分析师报告寻找看多理由
- 挑战空头观点
- 构建乐观预期场景
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import logging

from ..protocols import (
    AgentInterface, AgentOutput, AgentContext, AgentRole, 
    AgentMetadata
)


class BullResearcher(AgentInterface):
    """多头研究员 - 专门寻找看多理由"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # 多头研究配置
        self.stance = self.config.get('stance', 'optimistic')
        self.focus_strengths = self.config.get('focus_strengths', True)
        self.debate_style = self.config.get('debate_style', 'aggressive')
        
        # 多头关注重点
        self.bull_factors = [
            'revenue_growth', 'market_expansion', 'technological_advantage',
            'management_quality', 'competitive_moat', 'industry_tailwinds',
            'valuation_discount', 'catalyst_events', 'policy_support'
        ]
    
    def run(self, context: AgentContext) -> AgentOutput:
        """执行多头研究分析
        
        Args:
            context: 分析上下文，包含分析师报告
            
        Returns:
            AgentOutput: 多头研究结果
        """
        start_time = datetime.now()
        
        try:
            # 1. 分析师报告解读（多头视角）
            analyst_insights = self._analyze_from_bull_perspective(context)
            
            # 2. 寻找积极催化剂
            catalysts = self._identify_positive_catalysts(context)
            
            # 3. 风险因素反驳
            risk_rebuttals = self._rebut_negative_factors(context)
            
            # 4. 构建乐观情景
            optimistic_scenario = self._build_optimistic_scenario(context)
            
            # 5. 计算多头评分
            bull_score = self._calculate_bull_score(
                analyst_insights, catalysts, risk_rebuttals, optimistic_scenario
            )
            
            # 6. 生成多头论据
            bull_reasoning = self._generate_bull_reasoning(
                analyst_insights, catalysts, risk_rebuttals, optimistic_scenario, bull_score
            )
            
            # 7. 构造标准化输出
            execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            return AgentOutput(
                role=AgentRole.BULL,
                timestamp=datetime.now(),
                symbol=context.symbol,
                score=bull_score,
                confidence=self._calculate_confidence(analyst_insights, catalysts),
                features={
                    'bull_factors_count': len([f for f in self.bull_factors if f in analyst_insights]),
                    'catalyst_strength': catalysts.get('strength', 0.5),
                    'rebuttal_effectiveness': risk_rebuttals.get('effectiveness', 0.5),
                    'scenario_upside': optimistic_scenario.get('upside_potential', 0.15),
                    'debate_aggression': 0.8 if self.debate_style == 'aggressive' else 0.5
                },
                rationale=bull_reasoning,
                metadata=AgentMetadata(
                    agent_id=f"bull_researcher_{context.symbol}",
                    version="2.0.0",
                    execution_time_ms=execution_time,
                    data_sources=['analyst_reports', 'market_catalysts']
                ),
                tags=self._generate_tags(analyst_insights, catalysts),
                alerts=self._generate_alerts(analyst_insights, bull_score)
            )
            
        except Exception as e:
            self.logger.error(f"多头研究失败: {e}")
            
            # 返回错误状态的输出
            return AgentOutput(
                role=AgentRole.BULL,
                timestamp=datetime.now(),
                symbol=context.symbol,
                score=None,
                confidence=0.0,
                features={},
                rationale=f"多头研究失败: {str(e)}",
                metadata=AgentMetadata(
                    agent_id=f"bull_researcher_{context.symbol}",
                    version="2.0.0"
                ),
                alerts=[f"研究异常: {str(e)}"]
            )
    
    def _analyze_from_bull_perspective(self, context: AgentContext) -> Dict[str, Any]:
        """从多头视角分析分析师报告"""
        insights = {}
        
        # 从previous_outputs中提取分析师观点
        for output in context.previous_outputs:
            if output.role in [AgentRole.FUNDAMENTAL.value, AgentRole.TECHNICAL.value, 
                             AgentRole.SENTIMENT.value, AgentRole.NEWS.value]:
                
                # 提取积极因素
                if output.score and output.score > 0.5:
                    insights[f"{output.role}_positive"] = {
                        'score': output.score,
                        'confidence': output.confidence,
                        'reasoning': output.rationale
                    }
                
                # 从特征中寻找多头因素
                for feature, value in output.features.items():
                    if any(bull_factor in feature.lower() for bull_factor in self.bull_factors):
                        insights[feature] = value
        
        # 模拟多头解读
        insights.update({
            'growth_momentum': 0.75,  # 成长动能
            'market_position': 0.8,   # 市场地位
            'management_execution': 0.7,  # 管理层执行力
            'industry_prospects': 0.85    # 行业前景
        })
        
        return insights
    
    def _identify_positive_catalysts(self, context: AgentContext) -> Dict[str, Any]:
        """识别积极催化剂"""
        catalysts = {
            'strength': 0.0,
            'events': [],
            'timeline': {}
        }
        
        # 从新闻和情绪分析中寻找催化剂
        news_positive = False
        sentiment_positive = False
        
        for output in context.previous_outputs:
            if output.role == AgentRole.NEWS.value and output.score and output.score > 0.6:
                news_positive = True
                catalysts['events'].append("正面新闻催化")
            
            if output.role == AgentRole.SENTIMENT.value and output.score and output.score > 0.6:
                sentiment_positive = True
                catalysts['events'].append("市场情绪转好")
        
        # 模拟催化剂分析
        potential_catalysts = [
            "新产品发布预期",
            "行业政策利好",
            "业绩超预期可能",
            "估值修复机会",
            "市场份额提升"
        ]
        
        if news_positive or sentiment_positive:
            catalysts['events'].extend(potential_catalysts[:3])
            catalysts['strength'] = 0.7
        else:
            catalysts['events'].extend(potential_catalysts[:2])
            catalysts['strength'] = 0.5
        
        return catalysts
    
    def _rebut_negative_factors(self, context: AgentContext) -> Dict[str, Any]:
        """反驳负面因素"""
        rebuttals = {
            'effectiveness': 0.6,
            'arguments': []
        }
        
        # 寻找需要反驳的负面观点
        negative_scores = []
        for output in context.previous_outputs:
            if output.score and output.score < 0.4:
                negative_scores.append(output.score)
                
                # 针对性反驳
                if output.role == AgentRole.FUNDAMENTAL.value:
                    rebuttals['arguments'].append("基本面担忧被过度放大，长期逻辑依然成立")
                elif output.role == AgentRole.TECHNICAL.value:
                    rebuttals['arguments'].append("技术指标短期波动，不改变中长期趋势")
        
        # 通用反驳论点
        generic_rebuttals = [
            "市场过度悲观，反应过度",
            "短期困难不改变长期价值",
            "当前估值已充分反映风险",
            "行业整体向好趋势明确"
        ]
        
        rebuttals['arguments'].extend(generic_rebuttals[:2])
        
        # 根据负面程度调整反驳有效性
        if negative_scores:
            avg_negative = sum(negative_scores) / len(negative_scores)
            rebuttals['effectiveness'] = max(0.3, 0.9 - avg_negative)
        
        return rebuttals
    
    def _build_optimistic_scenario(self, context: AgentContext) -> Dict[str, Any]:
        """构建乐观情景"""
        scenario = {
            'upside_potential': 0.15,
            'probability': 0.4,
            'key_assumptions': [],
            'target_metrics': {}
        }
        
        # 从分析师报告中提取基础数据
        fundamental_score = 0.5
        for output in context.previous_outputs:
            if output.role == AgentRole.FUNDAMENTAL.value and output.score:
                fundamental_score = output.score
                break
        
        # 乐观假设
        optimistic_assumptions = [
            "行业增长率超出预期2-3个百分点",
            "公司市场份额持续扩大",
            "成本控制措施见效显著", 
            "新业务拓展顺利推进",
            "估值水平向行业平均回归"
        ]
        
        scenario['key_assumptions'] = optimistic_assumptions[:3]
        
        # 基于基本面调整乐观程度
        if fundamental_score > 0.6:
            scenario['upside_potential'] = 0.25
            scenario['probability'] = 0.5
        elif fundamental_score > 0.4:
            scenario['upside_potential'] = 0.15
            scenario['probability'] = 0.4
        else:
            scenario['upside_potential'] = 0.08
            scenario['probability'] = 0.3
        
        # 目标指标
        scenario['target_metrics'] = {
            'revenue_growth': '15-20%',
            'margin_improvement': '2-3pp',
            'pe_target': '18-22x'
        }
        
        return scenario
    
    def _calculate_bull_score(
        self,
        analyst_insights: Dict[str, Any],
        catalysts: Dict[str, Any], 
        risk_rebuttals: Dict[str, Any],
        optimistic_scenario: Dict[str, Any]
    ) -> float:
        """计算多头评分"""
        
        # 基础评分（基于分析师报告的积极因素）
        base_score = 0.5
        positive_count = len([k for k in analyst_insights.keys() if 'positive' in k])
        if positive_count > 0:
            base_score = min(0.8, 0.5 + positive_count * 0.1)
        
        # 催化剂加分
        catalyst_boost = catalysts.get('strength', 0) * 0.2
        
        # 反驳有效性加分
        rebuttal_boost = risk_rebuttals.get('effectiveness', 0) * 0.15
        
        # 乐观情景概率加分
        scenario_boost = optimistic_scenario.get('probability', 0) * 0.15
        
        bull_score = base_score + catalyst_boost + rebuttal_boost + scenario_boost
        
        return round(min(max(bull_score, 0.2), 0.95), 3)  # 多头不会给出极端悲观分数
    
    def _calculate_confidence(
        self,
        analyst_insights: Dict[str, Any],
        catalysts: Dict[str, Any]
    ) -> float:
        """计算置信度"""
        base_confidence = 0.6
        
        # 根据支持证据数量调整
        evidence_count = len(analyst_insights) + len(catalysts.get('events', []))
        if evidence_count > 5:
            base_confidence += 0.2
        elif evidence_count > 3:
            base_confidence += 0.1
        
        # 多头研究员相对更自信
        return round(min(base_confidence + 0.1, 0.9), 3)
    
    def _generate_bull_reasoning(
        self,
        analyst_insights: Dict[str, Any],
        catalysts: Dict[str, Any],
        risk_rebuttals: Dict[str, Any],
        optimistic_scenario: Dict[str, Any],
        score: float
    ) -> str:
        """生成多头论证"""
        
        reasoning_parts = []
        
        # 基本面优势
        if any('positive' in k for k in analyst_insights.keys()):
            reasoning_parts.append("基本面数据显示积极信号")
        
        # 催化剂论证
        if catalysts.get('events'):
            catalyst_text = "、".join(catalysts['events'][:2])
            reasoning_parts.append(f"多重催化剂叠加：{catalyst_text}")
        
        # 风险回应
        if risk_rebuttals.get('arguments'):
            reasoning_parts.append("负面因素被过度担忧，实际影响有限")
        
        # 乐观情景
        upside = optimistic_scenario.get('upside_potential', 0.15)
        reasoning_parts.append(f"乐观情景下具备{upside:.0%}上涨空间")
        
        # 投资建议
        if score > 0.7:
            reasoning_parts.append("强烈建议增持")
        elif score > 0.6:
            reasoning_parts.append("建议适度加仓")
        else:
            reasoning_parts.append("维持乐观态度")
        
        return "；".join(reasoning_parts)
    
    def _generate_tags(
        self,
        analyst_insights: Dict[str, Any],
        catalysts: Dict[str, Any]
    ) -> List[str]:
        """生成标签"""
        tags = ['bull_research', 'optimistic']
        
        if len(catalysts.get('events', [])) > 2:
            tags.append('multiple_catalysts')
        
        if any('growth' in k for k in analyst_insights.keys()):
            tags.append('growth_story')
        
        if self.debate_style == 'aggressive':
            tags.append('aggressive_bull')
        
        return tags
    
    def _generate_alerts(
        self,
        analyst_insights: Dict[str, Any],
        bull_score: float
    ) -> List[str]:
        """生成告警信息"""
        alerts = []
        
        # 如果多头论据不足
        if len(analyst_insights) < 2:
            alerts.append("多头论据相对薄弱，需要更多支撑")
        
        # 如果过度乐观
        if bull_score > 0.9:
            alerts.append("评分过于乐观，注意风险")
        
        return alerts