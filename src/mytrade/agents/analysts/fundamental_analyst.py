"""
基本面分析师Agent

专门负责公司基本面分析，包括财务指标、行业分析、估值分析等
参考TradingAgents的基本面分析实现，结合A股市场特点
"""

from typing import Dict, Any, List
from ..base_agent import BaseAgent, AgentResponse
import json


class FundamentalAnalyst(BaseAgent):
    """基本面分析师"""
    
    def __init__(self, agent_id: str, llm_adapter, config: Dict[str, Any] = None):
        super().__init__(agent_id, "基本面分析师", llm_adapter, config)
    
    def get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是一位专业的基本面分析师，专门分析上市公司的基本面情况。

你的职责包括：
1. 财务指标分析 - 分析盈利能力、偿债能力、运营效率等
2. 估值分析 - 计算和评估合理估值水平
3. 行业分析 - 评估公司在行业中的竞争地位
4. 成长性分析 - 评估公司的成长潜力和可持续性
5. 风险评估 - 识别公司面临的主要风险因素

分析要求：
- 基于提供的财务数据进行客观分析
- 结合A股市场特点和中国宏观经济环境
- 重点关注ROE、PE、PB、净利润增长率等核心指标
- 考虑行业周期性和政策影响因素
- 提供明确的投资建议和风险提示

输出格式要求：
- 使用中文进行分析
- 结构化输出分析结果
- 明确标注关键财务指标和结论"""

    def get_role_responsibility(self) -> str:
        """获取角色职责描述"""
        return "公司财务分析、估值分析和行业研究"
    
    def get_required_inputs(self) -> List[str]:
        """获取必需的输入参数"""
        return ["fundamental_data", "symbol"]
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """验证输入参数"""
        required_fields = self.get_required_inputs()
        
        for field in required_fields:
            if field not in inputs:
                self.logger.error(f"缺少必需的输入参数: {field}")
                return False
        
        # 验证基本面数据结构
        fundamental_data = inputs.get('fundamental_data', {})
        if not isinstance(fundamental_data, dict):
            self.logger.error("fundamental_data必须是字典类型")
            return False
        
        return True
    
    def process(self, inputs: Dict[str, Any]) -> AgentResponse:
        """处理分析请求"""
        if not self.validate_inputs(inputs):
            return self.format_output(
                content="输入参数验证失败",
                confidence=0.0,
                reasoning=["输入参数不完整或格式错误"]
            )
        
        symbol = inputs.get('symbol', '')
        fundamental_data = inputs.get('fundamental_data', {})
        
        try:
            # 分析基本面数据
            analysis_results = self._analyze_fundamentals(symbol, fundamental_data)
            
            # 生成分析请求
            analysis_request = self._format_analysis_request(symbol, analysis_results)
            
            # 调用LLM进行分析
            llm_response = self.llm_adapter.chat([
                {"role": "system", "content": self.get_system_prompt()},
                {"role": "user", "content": analysis_request}
            ])
            
            # 解析分析结果
            confidence, reasoning = self._parse_analysis_result(
                llm_response.content, analysis_results
            )
            
            self.logger.info(f"基本面分析师完成 {symbol} 的分析，置信度: {confidence}")
            
            return self.format_output(
                content=llm_response.content,
                confidence=confidence,
                reasoning=reasoning,
                fundamental_analysis=analysis_results,
                llm_response=llm_response.content
            )
            
        except Exception as e:
            self.logger.error(f"基本面分析失败: {e}")
            return self.format_output(
                content=f"基本面分析遇到错误: {str(e)}",
                confidence=0.0,
                reasoning=[f"分析过程中出现错误: {str(e)}"]
            )
    
    def _analyze_fundamentals(self, symbol: str, fundamental_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析基本面数据"""
        analysis = {
            'symbol': symbol,
            'financial_metrics': {},
            'valuation_metrics': {},
            'growth_metrics': {},
            'risk_metrics': {},
            'industry_metrics': {}
        }
        
        try:
            # 财务指标分析
            analysis['financial_metrics'] = self._calculate_financial_metrics(fundamental_data)
            
            # 估值指标分析
            analysis['valuation_metrics'] = self._calculate_valuation_metrics(fundamental_data)
            
            # 成长性指标分析
            analysis['growth_metrics'] = self._calculate_growth_metrics(fundamental_data)
            
            # 风险指标分析
            analysis['risk_metrics'] = self._calculate_risk_metrics(fundamental_data)
            
            # 行业指标分析
            analysis['industry_metrics'] = self._calculate_industry_metrics(fundamental_data)
            
        except Exception as e:
            self.logger.error(f"基本面指标计算失败: {e}")
        
        return analysis
    
    def _calculate_financial_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """计算财务指标"""
        metrics = {}
        
        try:
            # ROE - 净资产收益率
            if 'roe' in data and data['roe'] is not None:
                roe = float(data['roe'])
                metrics['roe'] = roe
                metrics['roe_level'] = self._evaluate_roe(roe)
            
            # ROA - 总资产收益率
            if 'roa' in data and data['roa'] is not None:
                roa = float(data['roa'])
                metrics['roa'] = roa
                metrics['roa_level'] = self._evaluate_roa(roa)
            
            # 毛利率
            if 'gross_margin' in data and data['gross_margin'] is not None:
                gross_margin = float(data['gross_margin'])
                metrics['gross_margin'] = gross_margin
                metrics['gross_margin_level'] = self._evaluate_gross_margin(gross_margin)
            
            # 净利率
            if 'net_margin' in data and data['net_margin'] is not None:
                net_margin = float(data['net_margin'])
                metrics['net_margin'] = net_margin
                metrics['net_margin_level'] = self._evaluate_net_margin(net_margin)
            
            # 资产负债率
            if 'debt_ratio' in data and data['debt_ratio'] is not None:
                debt_ratio = float(data['debt_ratio'])
                metrics['debt_ratio'] = debt_ratio
                metrics['debt_level'] = self._evaluate_debt_ratio(debt_ratio)
            
        except Exception as e:
            self.logger.error(f"财务指标计算错误: {e}")
        
        return metrics
    
    def _calculate_valuation_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """计算估值指标"""
        metrics = {}
        
        try:
            # PE比率
            if 'pe_ratio' in data and data['pe_ratio'] is not None:
                pe_ratio = float(data['pe_ratio'])
                metrics['pe_ratio'] = pe_ratio
                metrics['pe_level'] = self._evaluate_pe(pe_ratio)
            
            # PB比率
            if 'pb_ratio' in data and data['pb_ratio'] is not None:
                pb_ratio = float(data['pb_ratio'])
                metrics['pb_ratio'] = pb_ratio
                metrics['pb_level'] = self._evaluate_pb(pb_ratio)
            
            # PS比率
            if 'ps_ratio' in data and data['ps_ratio'] is not None:
                ps_ratio = float(data['ps_ratio'])
                metrics['ps_ratio'] = ps_ratio
                metrics['ps_level'] = self._evaluate_ps(ps_ratio)
            
            # PEG比率
            if all(k in data and data[k] is not None for k in ['pe_ratio', 'revenue_growth']):
                pe_ratio = float(data['pe_ratio'])
                growth_rate = float(data['revenue_growth']) * 100  # 转换为百分比
                if growth_rate > 0:
                    peg_ratio = pe_ratio / growth_rate
                    metrics['peg_ratio'] = peg_ratio
                    metrics['peg_level'] = self._evaluate_peg(peg_ratio)
            
        except Exception as e:
            self.logger.error(f"估值指标计算错误: {e}")
        
        return metrics
    
    def _calculate_growth_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """计算成长性指标"""
        metrics = {}
        
        try:
            # 营收增长率
            if 'revenue_growth' in data and data['revenue_growth'] is not None:
                revenue_growth = float(data['revenue_growth']) * 100
                metrics['revenue_growth'] = revenue_growth
                metrics['revenue_growth_level'] = self._evaluate_growth_rate(revenue_growth)
            
            # 净利润增长率
            if 'profit_growth' in data and data['profit_growth'] is not None:
                profit_growth = float(data['profit_growth']) * 100
                metrics['profit_growth'] = profit_growth
                metrics['profit_growth_level'] = self._evaluate_growth_rate(profit_growth)
            
            # EPS增长率
            if 'eps_growth' in data and data['eps_growth'] is not None:
                eps_growth = float(data['eps_growth']) * 100
                metrics['eps_growth'] = eps_growth
                metrics['eps_growth_level'] = self._evaluate_growth_rate(eps_growth)
            
        except Exception as e:
            self.logger.error(f"成长性指标计算错误: {e}")
        
        return metrics
    
    def _calculate_risk_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """计算风险指标"""
        metrics = {}
        
        try:
            # 流动比率
            if 'current_ratio' in data and data['current_ratio'] is not None:
                current_ratio = float(data['current_ratio'])
                metrics['current_ratio'] = current_ratio
                metrics['liquidity_level'] = self._evaluate_current_ratio(current_ratio)
            
            # 速动比率
            if 'quick_ratio' in data and data['quick_ratio'] is not None:
                quick_ratio = float(data['quick_ratio'])
                metrics['quick_ratio'] = quick_ratio
                metrics['quick_liquidity_level'] = self._evaluate_quick_ratio(quick_ratio)
            
            # 利息覆盖倍数
            if 'interest_coverage' in data and data['interest_coverage'] is not None:
                interest_coverage = float(data['interest_coverage'])
                metrics['interest_coverage'] = interest_coverage
                metrics['interest_coverage_level'] = self._evaluate_interest_coverage(interest_coverage)
            
        except Exception as e:
            self.logger.error(f"风险指标计算错误: {e}")
        
        return metrics
    
    def _calculate_industry_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """计算行业指标"""
        metrics = {}
        
        try:
            # 行业排名
            if 'industry_rank' in data and data['industry_rank'] is not None:
                metrics['industry_rank'] = data['industry_rank']
            
            # 行业平均PE
            if 'industry_avg_pe' in data and data['industry_avg_pe'] is not None:
                metrics['industry_avg_pe'] = float(data['industry_avg_pe'])
            
            # 市场占有率
            if 'market_share' in data and data['market_share'] is not None:
                metrics['market_share'] = float(data['market_share'])
            
        except Exception as e:
            self.logger.error(f"行业指标计算错误: {e}")
        
        return metrics
    
    def _evaluate_roe(self, roe: float) -> str:
        """评估ROE水平"""
        if roe >= 0.20:
            return "优秀"
        elif roe >= 0.15:
            return "良好"
        elif roe >= 0.10:
            return "一般"
        else:
            return "较差"
    
    def _evaluate_roa(self, roa: float) -> str:
        """评估ROA水平"""
        if roa >= 0.10:
            return "优秀"
        elif roa >= 0.06:
            return "良好"
        elif roa >= 0.03:
            return "一般"
        else:
            return "较差"
    
    def _evaluate_gross_margin(self, margin: float) -> str:
        """评估毛利率水平"""
        if margin >= 0.50:
            return "很高"
        elif margin >= 0.30:
            return "较高"
        elif margin >= 0.20:
            return "一般"
        else:
            return "较低"
    
    def _evaluate_net_margin(self, margin: float) -> str:
        """评估净利率水平"""
        if margin >= 0.15:
            return "很高"
        elif margin >= 0.10:
            return "较高"
        elif margin >= 0.05:
            return "一般"
        else:
            return "较低"
    
    def _evaluate_debt_ratio(self, ratio: float) -> str:
        """评估负债水平"""
        if ratio <= 0.30:
            return "低风险"
        elif ratio <= 0.50:
            return "中等风险"
        elif ratio <= 0.70:
            return "较高风险"
        else:
            return "高风险"
    
    def _evaluate_pe(self, pe: float) -> str:
        """评估PE水平"""
        if pe <= 0:
            return "亏损"
        elif pe <= 15:
            return "低估"
        elif pe <= 25:
            return "合理"
        elif pe <= 40:
            return "偏高"
        else:
            return "高估"
    
    def _evaluate_pb(self, pb: float) -> str:
        """评估PB水平"""
        if pb <= 1.0:
            return "破净"
        elif pb <= 2.0:
            return "低估"
        elif pb <= 3.0:
            return "合理"
        elif pb <= 5.0:
            return "偏高"
        else:
            return "高估"
    
    def _evaluate_ps(self, ps: float) -> str:
        """评估PS水平"""
        if ps <= 2.0:
            return "低估"
        elif ps <= 5.0:
            return "合理"
        elif ps <= 10.0:
            return "偏高"
        else:
            return "高估"
    
    def _evaluate_peg(self, peg: float) -> str:
        """评估PEG水平"""
        if peg <= 0.5:
            return "严重低估"
        elif peg <= 1.0:
            return "低估"
        elif peg <= 1.5:
            return "合理"
        elif peg <= 2.0:
            return "偏高"
        else:
            return "高估"
    
    def _evaluate_growth_rate(self, growth: float) -> str:
        """评估增长率水平"""
        if growth >= 30:
            return "高速增长"
        elif growth >= 15:
            return "快速增长"
        elif growth >= 5:
            return "稳定增长"
        elif growth >= 0:
            return "缓慢增长"
        else:
            return "负增长"
    
    def _evaluate_current_ratio(self, ratio: float) -> str:
        """评估流动比率"""
        if ratio >= 2.0:
            return "流动性充足"
        elif ratio >= 1.5:
            return "流动性良好"
        elif ratio >= 1.0:
            return "流动性一般"
        else:
            return "流动性不足"
    
    def _evaluate_quick_ratio(self, ratio: float) -> str:
        """评估速动比率"""
        if ratio >= 1.5:
            return "速动性充足"
        elif ratio >= 1.0:
            return "速动性良好"
        elif ratio >= 0.8:
            return "速动性一般"
        else:
            return "速动性不足"
    
    def _evaluate_interest_coverage(self, coverage: float) -> str:
        """评估利息覆盖倍数"""
        if coverage >= 10:
            return "偿息能力很强"
        elif coverage >= 5:
            return "偿息能力较强"
        elif coverage >= 2.5:
            return "偿息能力一般"
        else:
            return "偿息风险较高"
    
    def _format_analysis_request(self, symbol: str, analysis_results: Dict[str, Any]) -> str:
        """格式化分析请求"""
        request = f"""请分析股票 {symbol} 的基本面情况：

基本面数据：
"""
        
        # 财务指标
        financial = analysis_results.get('financial_metrics', {})
        if financial:
            request += "财务指标：\n"
            if 'roe' in financial:
                request += f"净资产收益率(ROE): {financial['roe']:.2%} ({financial.get('roe_level', 'N/A')})\n"
            if 'roa' in financial:
                request += f"总资产收益率(ROA): {financial['roa']:.2%} ({financial.get('roa_level', 'N/A')})\n"
            if 'gross_margin' in financial:
                request += f"毛利率: {financial['gross_margin']:.2%} ({financial.get('gross_margin_level', 'N/A')})\n"
            if 'net_margin' in financial:
                request += f"净利率: {financial['net_margin']:.2%} ({financial.get('net_margin_level', 'N/A')})\n"
            if 'debt_ratio' in financial:
                request += f"资产负债率: {financial['debt_ratio']:.2%} ({financial.get('debt_level', 'N/A')})\n"
        
        # 估值指标
        valuation = analysis_results.get('valuation_metrics', {})
        if valuation:
            request += "\n估值指标：\n"
            if 'pe_ratio' in valuation:
                request += f"市盈率(PE): {valuation['pe_ratio']:.2f} ({valuation.get('pe_level', 'N/A')})\n"
            if 'pb_ratio' in valuation:
                request += f"市净率(PB): {valuation['pb_ratio']:.2f} ({valuation.get('pb_level', 'N/A')})\n"
            if 'ps_ratio' in valuation:
                request += f"市销率(PS): {valuation['ps_ratio']:.2f} ({valuation.get('ps_level', 'N/A')})\n"
            if 'peg_ratio' in valuation:
                request += f"PEG比率: {valuation['peg_ratio']:.2f} ({valuation.get('peg_level', 'N/A')})\n"
        
        # 成长性指标
        growth = analysis_results.get('growth_metrics', {})
        if growth:
            request += "\n成长性指标：\n"
            if 'revenue_growth' in growth:
                request += f"营收增长率: {growth['revenue_growth']:.1f}% ({growth.get('revenue_growth_level', 'N/A')})\n"
            if 'profit_growth' in growth:
                request += f"净利润增长率: {growth['profit_growth']:.1f}% ({growth.get('profit_growth_level', 'N/A')})\n"
            if 'eps_growth' in growth:
                request += f"EPS增长率: {growth['eps_growth']:.1f}% ({growth.get('eps_growth_level', 'N/A')})\n"
        
        # 风险指标
        risk = analysis_results.get('risk_metrics', {})
        if risk:
            request += "\n风险指标：\n"
            if 'current_ratio' in risk:
                request += f"流动比率: {risk['current_ratio']:.2f} ({risk.get('liquidity_level', 'N/A')})\n"
            if 'quick_ratio' in risk:
                request += f"速动比率: {risk['quick_ratio']:.2f} ({risk.get('quick_liquidity_level', 'N/A')})\n"
            if 'interest_coverage' in risk:
                request += f"利息覆盖倍数: {risk['interest_coverage']:.2f} ({risk.get('interest_coverage_level', 'N/A')})\n"
        
        request += """
请基于以上基本面数据，从以下几个方面进行分析：
1. 财务健康状况评估（盈利能力、偿债能力、运营效率）
2. 估值水平判断（是否低估、合理或高估）
3. 成长性评估（增长质量和可持续性）
4. 投资风险识别（财务风险、行业风险等）
5. 行业地位和竞争优势分析
6. 综合投资建议和目标价位

请给出具体的分析结论和投资建议。
"""
        
        return request
    
    def _parse_analysis_result(self, analysis_content: str, analysis_results: Dict[str, Any]) -> tuple:
        """解析分析结果，提取置信度和推理过程"""
        reasoning = []
        confidence = 0.5  # 默认置信度
        
        # 基于基本面指标计算基础置信度
        confidence_factors = []
        
        # 财务指标因子
        financial = analysis_results.get('financial_metrics', {})
        if 'roe' in financial:
            roe = financial['roe']
            if roe >= 0.15:
                confidence_factors.append(0.1)
                reasoning.append(f"ROE优秀({roe:.1%})")
            elif roe < 0.05:
                confidence_factors.append(-0.1)
                reasoning.append(f"ROE较低({roe:.1%})")
        
        # 估值因子
        valuation = analysis_results.get('valuation_metrics', {})
        if 'pe_ratio' in valuation:
            pe = valuation['pe_ratio']
            if pe <= 15 and pe > 0:
                confidence_factors.append(0.15)
                reasoning.append(f"PE估值偏低({pe:.1f})")
            elif pe > 40:
                confidence_factors.append(-0.1)
                reasoning.append(f"PE估值偏高({pe:.1f})")
        
        # 成长性因子
        growth = analysis_results.get('growth_metrics', {})
        if 'revenue_growth' in growth:
            growth_rate = growth['revenue_growth']
            if growth_rate >= 15:
                confidence_factors.append(0.1)
                reasoning.append(f"高营收增长({growth_rate:.1f}%)")
            elif growth_rate < 0:
                confidence_factors.append(-0.15)
                reasoning.append(f"营收负增长({growth_rate:.1f}%)")
        
        # 风险因子
        risk = analysis_results.get('risk_metrics', {})
        if 'debt_ratio' in analysis_results.get('financial_metrics', {}):
            debt_ratio = analysis_results['financial_metrics']['debt_ratio']
            if debt_ratio <= 0.3:
                confidence_factors.append(0.05)
                reasoning.append("低负债风险")
            elif debt_ratio > 0.7:
                confidence_factors.append(-0.1)
                reasoning.append("高负债风险")
        
        # 计算最终置信度
        confidence = 0.5 + sum(confidence_factors)
        confidence = max(0.1, min(0.9, confidence))  # 限制在0.1-0.9之间
        
        return confidence, reasoning