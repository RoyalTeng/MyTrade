"""
基本面分析师 v2.0 - 符合统一Agent协议

基于TradingAgents架构重构，实现标准化输出协议
专门负责公司基本面分析，包括财务指标、行业分析、估值分析等
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import logging

from ..protocols import (
    AgentInterface, AgentOutput, AgentContext, AgentRole, 
    AgentMetadata
)


class FundamentalAnalyst(AgentInterface):
    """基本面分析师 - 符合统一协议"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # 分析配置
        self.focus_metrics = self.config.get('focus_metrics', [
            'pe', 'pb', 'roe', 'debt_ratio', 'current_ratio',
            'revenue_growth', 'profit_growth', 'gross_margin'
        ])
        self.analysis_depth = self.config.get('analysis_depth', 'standard')
        
    def run(self, context: AgentContext) -> AgentOutput:
        """
        执行基本面分析
        
        Args:
            context: 分析上下文，包含股票代码、财务数据等
            
        Returns:
            AgentOutput: 标准化的分析结果
        """
        start_time = datetime.now()
        
        try:
            # 1. 验证输入数据
            if not self._validate_context(context):
                raise ValueError("输入数据验证失败")
            
            # 2. 执行财务分析
            financial_analysis = self._analyze_financials(context)
            
            # 3. 执行估值分析
            valuation_analysis = self._analyze_valuation(context)
            
            # 4. 执行行业分析
            industry_analysis = self._analyze_industry(context)
            
            # 5. 综合评分
            overall_score = self._calculate_overall_score(
                financial_analysis,
                valuation_analysis, 
                industry_analysis
            )
            
            # 6. 生成分析结论
            rationale = self._generate_rationale(
                financial_analysis,
                valuation_analysis,
                industry_analysis,
                overall_score
            )
            
            # 7. 构造标准化输出
            execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            return AgentOutput(
                role=AgentRole.FUNDAMENTAL,
                timestamp=datetime.now(),
                symbol=context.symbol,
                score=overall_score,
                confidence=self._calculate_confidence(financial_analysis, valuation_analysis),
                features={
                    **financial_analysis.get('metrics', {}),
                    **valuation_analysis.get('metrics', {}),
                    'industry_rank': industry_analysis.get('rank'),
                    'growth_rate': financial_analysis.get('growth_rate'),
                    'safety_score': financial_analysis.get('safety_score')
                },
                rationale=rationale,
                metadata=AgentMetadata(
                    agent_id=f"fundamental_analyst_{context.symbol}",
                    version="2.0.0",
                    execution_time_ms=execution_time,
                    data_sources=['financial_reports', 'industry_data']
                ),
                tags=self._generate_tags(financial_analysis, valuation_analysis),
                alerts=self._generate_alerts(financial_analysis, valuation_analysis)
            )
            
        except Exception as e:
            self.logger.error(f"基本面分析失败: {e}")
            
            # 返回错误状态的输出
            return AgentOutput(
                role=AgentRole.FUNDAMENTAL,
                timestamp=datetime.now(),
                symbol=context.symbol,
                score=None,
                confidence=0.0,
                features={},
                rationale=f"分析失败: {str(e)}",
                metadata=AgentMetadata(
                    agent_id=f"fundamental_analyst_{context.symbol}",
                    version="2.0.0"
                ),
                alerts=[f"分析异常: {str(e)}"]
            )
    
    def _validate_context(self, context: AgentContext) -> bool:
        """验证输入上下文"""
        if not context.symbol:
            return False
        
        if not context.market_data:
            self.logger.warning("缺少市场数据，将使用基础分析")
        
        return True
    
    def _analyze_financials(self, context: AgentContext) -> Dict[str, Any]:
        """财务指标分析"""
        market_data = context.market_data or {}
        
        # 模拟财务分析 - 实际实现中应从数据源获取真实财务数据
        analysis = {
            'metrics': {
                'pe_ratio': 15.2,
                'pb_ratio': 1.8,  
                'roe': 0.12,
                'debt_ratio': 0.35,
                'current_ratio': 2.1,
                'revenue_growth': 0.08,
                'profit_margin': 0.15
            },
            'growth_rate': 0.08,
            'safety_score': 0.75,
            'profitability': 'good',
            'leverage': 'moderate'
        }
        
        # 财务健康度评估
        pe = analysis['metrics']['pe_ratio']
        roe = analysis['metrics']['roe']
        debt_ratio = analysis['metrics']['debt_ratio']
        
        health_score = 0.0
        if pe < 20:  # PE合理
            health_score += 0.3
        if roe > 0.10:  # ROE良好
            health_score += 0.4
        if debt_ratio < 0.5:  # 负债率合理
            health_score += 0.3
        
        analysis['health_score'] = min(health_score, 1.0)
        
        return analysis
    
    def _analyze_valuation(self, context: AgentContext) -> Dict[str, Any]:
        """估值分析"""
        # 模拟估值分析
        analysis = {
            'metrics': {
                'fair_value': 12.8,
                'current_price': 11.5,
                'upside_potential': 0.113,
                'dcf_value': 13.2,
                'pe_fair_value': 12.5
            },
            'valuation_level': 'undervalued',
            'confidence': 0.72
        }
        
        return analysis
    
    def _analyze_industry(self, context: AgentContext) -> Dict[str, Any]:
        """行业分析"""
        # 模拟行业分析
        analysis = {
            'rank': 'top_quartile',
            'industry_growth': 0.06,
            'competitive_position': 'strong',
            'market_share': 0.08,
            'industry_trend': 'positive'
        }
        
        return analysis
    
    def _calculate_overall_score(
        self, 
        financial: Dict[str, Any],
        valuation: Dict[str, Any],
        industry: Dict[str, Any]
    ) -> float:
        """计算综合评分 (0-1)"""
        
        # 财务评分 (40%)
        financial_score = financial.get('health_score', 0.5)
        
        # 估值评分 (35%)
        upside = valuation['metrics'].get('upside_potential', 0)
        valuation_score = min(max(upside, -0.3), 0.3) / 0.3 * 0.5 + 0.5
        
        # 行业评分 (25%) 
        industry_score = 0.7 if industry.get('rank') == 'top_quartile' else 0.5
        
        overall_score = (
            financial_score * 0.4 +
            valuation_score * 0.35 + 
            industry_score * 0.25
        )
        
        return round(min(max(overall_score, 0.0), 1.0), 3)
    
    def _calculate_confidence(
        self,
        financial: Dict[str, Any],
        valuation: Dict[str, Any]
    ) -> float:
        """计算置信度"""
        base_confidence = 0.6
        
        # 根据数据质量调整置信度
        if financial.get('health_score', 0) > 0.7:
            base_confidence += 0.1
        
        if valuation.get('confidence', 0) > 0.7:
            base_confidence += 0.15
            
        return round(min(base_confidence, 1.0), 3)
    
    def _generate_rationale(
        self,
        financial: Dict[str, Any],
        valuation: Dict[str, Any], 
        industry: Dict[str, Any],
        score: float
    ) -> str:
        """生成分析推理"""
        
        pe = financial['metrics']['pe_ratio']
        roe = financial['metrics']['roe']
        upside = valuation['metrics']['upside_potential']
        
        rationale_parts = []
        
        # 财务状况
        if financial.get('health_score', 0) > 0.7:
            rationale_parts.append(f"财务状况良好，ROE达{roe:.1%}")
        else:
            rationale_parts.append("财务状况一般")
        
        # 估值水平
        if upside > 0.1:
            rationale_parts.append(f"估值偏低，具有{upside:.1%}上涨空间")
        elif upside < -0.1:
            rationale_parts.append("估值偏高，存在下行风险")
        else:
            rationale_parts.append("估值合理")
        
        # 行业地位
        if industry.get('rank') == 'top_quartile':
            rationale_parts.append("行业地位领先")
        
        # 投资建议
        if score > 0.7:
            rationale_parts.append("建议买入")
        elif score < 0.3:
            rationale_parts.append("建议谨慎")
        else:
            rationale_parts.append("建议持有观望")
        
        return "；".join(rationale_parts)
    
    def _generate_tags(
        self,
        financial: Dict[str, Any],
        valuation: Dict[str, Any]
    ) -> List[str]:
        """生成标签"""
        tags = ['fundamental_analysis']
        
        if financial.get('health_score', 0) > 0.7:
            tags.append('healthy_financials')
        
        if valuation['metrics'].get('upside_potential', 0) > 0.1:
            tags.append('undervalued')
        elif valuation['metrics'].get('upside_potential', 0) < -0.1:
            tags.append('overvalued')
        
        if financial['metrics'].get('roe', 0) > 0.15:
            tags.append('high_roe')
        
        return tags
    
    def _generate_alerts(
        self,
        financial: Dict[str, Any],
        valuation: Dict[str, Any]
    ) -> List[str]:
        """生成告警信息"""
        alerts = []
        
        # 财务风险告警
        debt_ratio = financial['metrics'].get('debt_ratio', 0)
        if debt_ratio > 0.7:
            alerts.append(f"高负债率风险：{debt_ratio:.1%}")
        
        # 估值风险告警
        pe = financial['metrics'].get('pe_ratio', 0)
        if pe > 50:
            alerts.append(f"估值过高风险：PE={pe:.1f}")
        
        # 盈利能力告警
        roe = financial['metrics'].get('roe', 0)
        if roe < 0.05:
            alerts.append(f"盈利能力较弱：ROE={roe:.1%}")
        
        return alerts
    
    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        return {
            "status": "healthy",
            "agent_type": "FundamentalAnalyst",
            "version": "2.0.0",
            "timestamp": datetime.now().isoformat(),
            "config": {
                "focus_metrics_count": len(self.focus_metrics),
                "analysis_depth": self.analysis_depth
            }
        }