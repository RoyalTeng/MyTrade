"""
空头研究员 - Bear Researcher

专门挖掘和放大股票的风险因素：
- 质疑乐观假设
- 寻找潜在风险点
- 构建悲观预期场景
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import logging

from ..protocols import (
    AgentInterface, AgentOutput, AgentContext, AgentRole, 
    AgentMetadata
)


class BearResearcher(AgentInterface):
    """空头研究员 - 专门寻找看空理由"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # 空头研究配置
        self.stance = self.config.get('stance', 'pessimistic')
        self.focus_risks = self.config.get('focus_risks', True)
        self.debate_style = self.config.get('debate_style', 'conservative')
        
        # 空头关注重点
        self.bear_factors = [
            'revenue_decline', 'margin_pressure', 'competitive_threat',
            'regulatory_risk', 'debt_burden', 'industry_headwinds',
            'valuation_bubble', 'execution_risk', 'cyclical_peak'
        ]
    
    def run(self, context: AgentContext) -> AgentOutput:
        """执行空头研究分析
        
        Args:
            context: 分析上下文，包含分析师报告
            
        Returns:
            AgentOutput: 空头研究结果
        """
        start_time = datetime.now()
        
        try:
            # 1. 分析师报告解读（空头视角）
            analyst_concerns = self._analyze_from_bear_perspective(context)
            
            # 2. 寻找风险因素
            risk_factors = self._identify_risk_factors(context)
            
            # 3. 质疑乐观假设
            assumption_challenges = self._challenge_optimistic_assumptions(context)
            
            # 4. 构建悲观情景
            pessimistic_scenario = self._build_pessimistic_scenario(context)
            
            # 5. 计算空头评分
            bear_score = self._calculate_bear_score(
                analyst_concerns, risk_factors, assumption_challenges, pessimistic_scenario
            )
            
            # 6. 生成空头论据
            bear_reasoning = self._generate_bear_reasoning(
                analyst_concerns, risk_factors, assumption_challenges, pessimistic_scenario, bear_score
            )
            
            # 7. 构造标准化输出
            execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            return AgentOutput(
                role=AgentRole.BEAR,
                timestamp=datetime.now(),
                symbol=context.symbol,
                score=bear_score,
                confidence=self._calculate_confidence(analyst_concerns, risk_factors),
                features={
                    'bear_factors_count': len([f for f in self.bear_factors if f in analyst_concerns]),
                    'risk_severity': risk_factors.get('severity', 0.5),
                    'assumption_flaws': assumption_challenges.get('flaw_count', 0),
                    'scenario_downside': pessimistic_scenario.get('downside_risk', 0.15),
                    'debate_conservatism': 0.8 if self.debate_style == 'conservative' else 0.6
                },
                rationale=bear_reasoning,
                metadata=AgentMetadata(
                    agent_id=f"bear_researcher_{context.symbol}",
                    version="2.0.0",
                    execution_time_ms=execution_time,
                    data_sources=['risk_assessment', 'market_concerns']
                ),
                tags=self._generate_tags(analyst_concerns, risk_factors),
                alerts=self._generate_alerts(analyst_concerns, bear_score)
            )
            
        except Exception as e:
            self.logger.error(f"空头研究失败: {e}")
            
            # 返回错误状态的输出
            return AgentOutput(
                role=AgentRole.BEAR,
                timestamp=datetime.now(),
                symbol=context.symbol,
                score=None,
                confidence=0.0,
                features={},
                rationale=f"空头研究失败: {str(e)}",
                metadata=AgentMetadata(
                    agent_id=f"bear_researcher_{context.symbol}",
                    version="2.0.0"
                ),
                alerts=[f"研究异常: {str(e)}"]
            )
    
    def _analyze_from_bear_perspective(self, context: AgentContext) -> Dict[str, Any]:
        """从空头视角分析分析师报告"""
        concerns = {}
        
        # 从previous_outputs中提取分析师观点
        for output in context.previous_outputs:
            if output.role in [AgentRole.FUNDAMENTAL.value, AgentRole.TECHNICAL.value, 
                             AgentRole.SENTIMENT.value, AgentRole.NEWS.value]:
                
                # 提取负面因素
                if output.score and output.score < 0.5:
                    concerns[f"{output.role}_negative"] = {
                        'score': output.score,
                        'confidence': output.confidence,
                        'reasoning': output.rationale
                    }
                
                # 从特征中寻找空头因素
                for feature, value in output.features.items():
                    if any(bear_factor in feature.lower() for bear_factor in self.bear_factors):
                        concerns[feature] = value
                
                # 即使正面数据也要找问题
                if output.score and output.score > 0.7:
                    concerns[f"{output.role}_overoptimistic"] = {
                        'score': output.score,
                        'concern': '过度乐观，可能存在隐藏风险'
                    }
        
        # 模拟空头解读
        concerns.update({
            'valuation_stretch': 0.7,  # 估值过度拉伸
            'cyclical_risk': 0.6,     # 周期性风险
            'execution_uncertainty': 0.65,  # 执行不确定性
            'competitive_pressure': 0.75     # 竞争压力
        })
        
        return concerns
    
    def _identify_risk_factors(self, context: AgentContext) -> Dict[str, Any]:
        """识别风险因素"""
        risks = {
            'severity': 0.5,
            'factors': [],
            'probability': {}
        }
        
        # 从新闻和情绪分析中寻找风险
        news_negative = False
        sentiment_negative = False
        
        for output in context.previous_outputs:
            if output.role == AgentRole.NEWS.value and output.score and output.score < 0.4:
                news_negative = True
                risks['factors'].append("负面新闻影响")
            
            if output.role == AgentRole.SENTIMENT.value and output.score and output.score < 0.4:
                sentiment_negative = True
                risks['factors'].append("市场情绪转弱")
        
        # 系统性风险因素
        systematic_risks = [
            "宏观经济下行压力",
            "行业政策不确定性",
            "流动性收紧风险",
            "汇率波动影响",
            "地缘政治风险"
        ]
        
        # 个股特定风险
        idiosyncratic_risks = [
            "业绩不及预期风险", 
            "管理层变动风险",
            "竞争加剧威胁",
            "技术迭代风险",
            "客户集中度风险"
        ]
        
        if news_negative or sentiment_negative:
            risks['factors'].extend(systematic_risks[:2])
            risks['factors'].extend(idiosyncratic_risks[:3])
            risks['severity'] = 0.8
        else:
            risks['factors'].extend(systematic_risks[:1])
            risks['factors'].extend(idiosyncratic_risks[:2])
            risks['severity'] = 0.6
        
        # 风险概率评估
        for factor in risks['factors']:
            if '政策' in factor or '宏观' in factor:
                risks['probability'][factor] = 0.4
            else:
                risks['probability'][factor] = 0.3
        
        return risks
    
    def _challenge_optimistic_assumptions(self, context: AgentContext) -> Dict[str, Any]:
        """质疑乐观假设"""
        challenges = {
            'flaw_count': 0,
            'arguments': []
        }
        
        # 寻找过度乐观的观点
        optimistic_scores = []
        for output in context.previous_outputs:
            if output.score and output.score > 0.7:
                optimistic_scores.append(output.score)
                challenges['flaw_count'] += 1
                
                # 针对性质疑
                if output.role == AgentRole.FUNDAMENTAL.value:
                    challenges['arguments'].append("基本面改善可持续性存疑，历史数据可能失效")
                elif output.role == AgentRole.TECHNICAL.value:
                    challenges['arguments'].append("技术形态可能是假突破，市场操控痕迹明显")
                elif output.role == AgentRole.SENTIMENT.value:
                    challenges['arguments'].append("市场情绪过热，回调风险加大")
        
        # 通用质疑论点
        generic_challenges = [
            "预期过于乐观，现实执行难度被低估",
            "市场环境变化快，假设条件可能不成立",
            "竞争对手反应被忽视，护城河不如想象",
            "成本上升压力被低估，盈利改善不可持续"
        ]
        
        challenges['arguments'].extend(generic_challenges[:2])
        
        return challenges
    
    def _build_pessimistic_scenario(self, context: AgentContext) -> Dict[str, Any]:
        """构建悲观情景"""
        scenario = {
            'downside_risk': 0.2,
            'probability': 0.35,
            'key_risks': [],
            'impact_metrics': {}
        }
        
        # 从分析师报告中提取基础数据
        fundamental_score = 0.5
        for output in context.previous_outputs:
            if output.role == AgentRole.FUNDAMENTAL.value and output.score:
                fundamental_score = output.score
                break
        
        # 悲观假设
        pessimistic_risks = [
            "行业增长率大幅下滑",
            "主要客户流失或订单取消",
            "原材料成本大幅上涨",
            "新产品推出不及预期",
            "监管政策突然收紧"
        ]
        
        scenario['key_risks'] = pessimistic_risks[:3]
        
        # 基于基本面调整悲观程度
        if fundamental_score < 0.4:
            scenario['downside_risk'] = 0.3
            scenario['probability'] = 0.5
        elif fundamental_score < 0.6:
            scenario['downside_risk'] = 0.2
            scenario['probability'] = 0.35
        else:
            scenario['downside_risk'] = 0.12
            scenario['probability'] = 0.25
        
        # 影响指标
        scenario['impact_metrics'] = {
            'revenue_decline': '10-20%',
            'margin_compression': '3-5pp',
            'pe_contraction': '12-15x'
        }
        
        return scenario
    
    def _calculate_bear_score(
        self,
        analyst_concerns: Dict[str, Any],
        risk_factors: Dict[str, Any],
        assumption_challenges: Dict[str, Any],
        pessimistic_scenario: Dict[str, Any]
    ) -> float:
        """计算空头评分"""
        
        # 基础评分（基于分析师报告的负面因素）
        base_score = 0.5
        negative_count = len([k for k in analyst_concerns.keys() if 'negative' in k])
        if negative_count > 0:
            base_score = max(0.2, 0.5 - negative_count * 0.1)
        
        # 风险因素减分
        risk_penalty = risk_factors.get('severity', 0) * 0.25
        
        # 假设质疑减分
        challenge_penalty = min(assumption_challenges.get('flaw_count', 0) * 0.1, 0.2)
        
        # 悲观情景减分
        scenario_penalty = pessimistic_scenario.get('probability', 0) * 0.2
        
        bear_score = base_score - risk_penalty - challenge_penalty - scenario_penalty
        
        return round(min(max(bear_score, 0.05), 0.8), 3)  # 空头不会给出极端乐观分数
    
    def _calculate_confidence(
        self,
        analyst_concerns: Dict[str, Any],
        risk_factors: Dict[str, Any]
    ) -> float:
        """计算置信度"""
        base_confidence = 0.65  # 空头研究员相对更谨慎
        
        # 根据风险证据数量调整
        evidence_count = len(analyst_concerns) + len(risk_factors.get('factors', []))
        if evidence_count > 6:
            base_confidence += 0.15
        elif evidence_count > 4:
            base_confidence += 0.1
        
        return round(min(base_confidence, 0.85), 3)  # 空头更保守，置信度不会过高
    
    def _generate_bear_reasoning(
        self,
        analyst_concerns: Dict[str, Any],
        risk_factors: Dict[str, Any],
        assumption_challenges: Dict[str, Any],
        pessimistic_scenario: Dict[str, Any],
        score: float
    ) -> str:
        """生成空头论证"""
        
        reasoning_parts = []
        
        # 风险因素分析
        if risk_factors.get('factors'):
            risk_text = "、".join(risk_factors['factors'][:2])
            reasoning_parts.append(f"面临多重风险：{risk_text}")
        
        # 质疑乐观预期
        if assumption_challenges.get('flaw_count', 0) > 0:
            reasoning_parts.append("市场预期过于乐观，存在明显认知偏差")
        
        # 估值担忧
        if any('valuation' in k for k in analyst_concerns.keys()):
            reasoning_parts.append("当前估值水平难以持续，回调压力较大")
        
        # 悲观情景
        downside = pessimistic_scenario.get('downside_risk', 0.15)
        reasoning_parts.append(f"悲观情景下存在{downside:.0%}下跌风险")
        
        # 投资建议
        if score < 0.3:
            reasoning_parts.append("建议减持规避风险")
        elif score < 0.4:
            reasoning_parts.append("建议谨慎，等待更好时机")
        else:
            reasoning_parts.append("保持观望态度")
        
        return "；".join(reasoning_parts)
    
    def _generate_tags(
        self,
        analyst_concerns: Dict[str, Any],
        risk_factors: Dict[str, Any]
    ) -> List[str]:
        """生成标签"""
        tags = ['bear_research', 'pessimistic']
        
        if len(risk_factors.get('factors', [])) > 3:
            tags.append('high_risk')
        
        if any('valuation' in k for k in analyst_concerns.keys()):
            tags.append('overvaluation_concern')
        
        if self.debate_style == 'conservative':
            tags.append('conservative_bear')
        
        return tags
    
    def _generate_alerts(
        self,
        analyst_concerns: Dict[str, Any],
        bear_score: float
    ) -> List[str]:
        """生成告警信息"""
        alerts = []
        
        # 如果空头论据不足
        if len(analyst_concerns) < 2:
            alerts.append("空头论据相对薄弱，可能过度悲观")
        
        # 如果过度悲观
        if bear_score < 0.1:
            alerts.append("评分过于悲观，注意反弹风险")
        
        # 如果风险集中
        if len(set(k.split('_')[0] for k in analyst_concerns.keys())) < 2:
            alerts.append("风险来源过于集中，关注其他维度")
        
        return alerts