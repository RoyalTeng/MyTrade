"""
市场分析师Agent

专门负责宏观市场分析，包括大盘走势、行业轮动、资金流向、政策影响等
参考TradingAgents的市场分析实现，结合A股市场特点
"""

from typing import Dict, Any, List
from ..base_agent import BaseAgent, AgentResponse
import json
from datetime import datetime, timedelta


class MarketAnalyst(BaseAgent):
    """市场分析师"""
    
    def __init__(self, agent_id: str, llm_adapter, config: Dict[str, Any] = None):
        super().__init__(agent_id, "市场分析师", llm_adapter, config)
    
    def get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是一位专业的市场分析师，专门分析宏观市场环境和大盘走势。

你的职责包括：
1. 大盘走势分析 - 分析主要指数的技术走势和趋势
2. 行业轮动分析 - 识别热点行业和资金流向
3. 市场结构分析 - 分析市场广度、深度和参与度
4. 宏观环境分析 - 评估经济数据和政策对市场的影响
5. 风险评估 - 识别系统性风险和市场风险点
6. 市场情绪分析 - 评估整体市场情绪和投资者行为

分析要求：
- 结合A股市场特点和中国宏观经济环境
- 重点关注沪深300、中证500、创业板等主要指数
- 考虑政策导向和资金面因素
- 识别市场轮动和结构性机会
- 评估国际市场对A股的影响

输出格式要求：
- 使用中文进行分析
- 提供具体的市场判断和操作建议
- 明确标注关键风险点和机会
- 给出明确的市场观点和时间窗口"""

    def get_role_responsibility(self) -> str:
        """获取角色职责描述"""
        return "大盘分析、行业轮动和宏观市场环境研究"
    
    def get_required_inputs(self) -> List[str]:
        """获取必需的输入参数"""
        return ["market_data", "symbol"]
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """验证输入参数"""
        required_fields = self.get_required_inputs()
        
        for field in required_fields:
            if field not in inputs:
                self.logger.error(f"缺少必需的输入参数: {field}")
                return False
        
        # 验证市场数据结构
        market_data = inputs.get('market_data', {})
        if not isinstance(market_data, dict):
            self.logger.error("market_data必须是字典类型")
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
        market_data = inputs.get('market_data', {})
        
        try:
            # 分析市场数据
            analysis_results = self._analyze_market(symbol, market_data)
            
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
            
            self.logger.info(f"市场分析师完成 {symbol} 的分析，置信度: {confidence}")
            
            return self.format_output(
                content=llm_response.content,
                confidence=confidence,
                reasoning=reasoning,
                market_analysis=analysis_results,
                llm_response=llm_response.content
            )
            
        except Exception as e:
            self.logger.error(f"市场分析失败: {e}")
            return self.format_output(
                content=f"市场分析遇到错误: {str(e)}",
                confidence=0.0,
                reasoning=[f"分析过程中出现错误: {str(e)}"]
            )
    
    def _analyze_market(self, symbol: str, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析市场数据"""
        analysis = {
            'symbol': symbol,
            'index_analysis': {},
            'sector_analysis': {},
            'market_structure': {},
            'macro_analysis': {},
            'international_impact': {},
            'risk_assessment': {}
        }
        
        try:
            # 大盘指数分析
            if 'indices' in market_data:
                analysis['index_analysis'] = self._analyze_indices(market_data['indices'])
            
            # 行业板块分析
            if 'sectors' in market_data:
                analysis['sector_analysis'] = self._analyze_sectors(market_data['sectors'])
            
            # 市场结构分析
            if 'market_structure' in market_data:
                analysis['market_structure'] = self._analyze_market_structure(market_data['market_structure'])
            
            # 宏观数据分析
            if 'macro_data' in market_data:
                analysis['macro_analysis'] = self._analyze_macro_data(market_data['macro_data'])
            
            # 国际市场影响
            if 'international' in market_data:
                analysis['international_impact'] = self._analyze_international_impact(market_data['international'])
            
            # 风险评估
            analysis['risk_assessment'] = self._assess_market_risks(analysis)
            
        except Exception as e:
            self.logger.error(f"市场数据分析失败: {e}")
        
        return analysis
    
    def _analyze_indices(self, indices_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析主要指数"""
        index_analysis = {}
        
        # 主要指数列表
        major_indices = ['sh000001', 'sh000300', 'sz399001', 'sz399006']  # 上证、沪深300、深证、创业板
        
        for index_code, index_data in indices_data.items():
            try:
                if not isinstance(index_data, dict):
                    continue
                
                analysis = {
                    'index_code': index_code,
                    'current_price': None,
                    'change_pct': None,
                    'volume_ratio': None,
                    'technical_trend': None,
                    'support_resistance': {},
                    'momentum_indicators': {}
                }
                
                # 当前价格和涨跌幅
                if 'close' in index_data and index_data['close'] is not None:
                    analysis['current_price'] = float(index_data['close'])
                
                if 'change_pct' in index_data and index_data['change_pct'] is not None:
                    change_pct = float(index_data['change_pct'])
                    analysis['change_pct'] = change_pct
                    analysis['daily_trend'] = self._evaluate_daily_trend(change_pct)
                
                # 成交量分析
                if 'volume' in index_data and 'avg_volume' in index_data:
                    current_vol = index_data['volume']
                    avg_vol = index_data['avg_volume']
                    if avg_vol and avg_vol > 0:
                        vol_ratio = current_vol / avg_vol
                        analysis['volume_ratio'] = vol_ratio
                        analysis['volume_level'] = self._evaluate_volume_level(vol_ratio)
                
                # 技术趋势分析
                if 'price_data' in index_data:
                    price_data = index_data['price_data']
                    analysis['technical_trend'] = self._analyze_index_trend(price_data)
                    analysis['support_resistance'] = self._calculate_support_resistance(price_data)
                
                # 动量指标
                if 'momentum' in index_data:
                    analysis['momentum_indicators'] = index_data['momentum']
                
                index_analysis[index_code] = analysis
                
            except Exception as e:
                self.logger.error(f"指数{index_code}分析错误: {e}")
                continue
        
        # 计算市场整体趋势
        if index_analysis:
            index_analysis['market_trend'] = self._calculate_market_trend(index_analysis)
        
        return index_analysis
    
    def _analyze_sectors(self, sectors_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析行业板块"""
        sector_analysis = {
            'top_performers': [],
            'worst_performers': [],
            'sector_rotation': {},
            'hot_sectors': [],
            'money_flow': {}
        }
        
        try:
            sector_performances = []
            
            for sector_name, sector_data in sectors_data.items():
                if not isinstance(sector_data, dict):
                    continue
                
                performance = {
                    'sector': sector_name,
                    'change_pct': sector_data.get('change_pct', 0),
                    'volume_ratio': sector_data.get('volume_ratio', 1),
                    'money_flow': sector_data.get('money_flow', 0),
                    'stock_count': sector_data.get('stock_count', 0),
                    'up_count': sector_data.get('up_count', 0),
                    'down_count': sector_data.get('down_count', 0)
                }
                
                # 计算板块强度
                performance['strength'] = self._calculate_sector_strength(performance)
                sector_performances.append(performance)
            
            # 排序找出表现最好和最差的板块
            sector_performances.sort(key=lambda x: x['change_pct'], reverse=True)
            
            sector_analysis['top_performers'] = sector_performances[:5]
            sector_analysis['worst_performers'] = sector_performances[-5:]
            
            # 识别热点板块（涨幅>1%且成交量放大）
            hot_sectors = [
                sector for sector in sector_performances
                if sector['change_pct'] > 1.0 and sector['volume_ratio'] > 1.5
            ]
            sector_analysis['hot_sectors'] = hot_sectors[:10]
            
            # 资金流向分析
            total_inflow = sum(s['money_flow'] for s in sector_performances if s['money_flow'] > 0)
            total_outflow = sum(abs(s['money_flow']) for s in sector_performances if s['money_flow'] < 0)
            
            sector_analysis['money_flow'] = {
                'total_inflow': total_inflow,
                'total_outflow': total_outflow,
                'net_flow': total_inflow - total_outflow,
                'flow_direction': 'inflow' if total_inflow > total_outflow else 'outflow'
            }
            
            # 板块轮动分析
            sector_analysis['sector_rotation'] = self._analyze_sector_rotation(sector_performances)
            
        except Exception as e:
            self.logger.error(f"行业板块分析错误: {e}")
        
        return sector_analysis
    
    def _analyze_market_structure(self, structure_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析市场结构"""
        structure_analysis = {}
        
        try:
            # 涨跌停统计
            if 'limit_up_count' in structure_data and 'limit_down_count' in structure_data:
                limit_up = structure_data['limit_up_count']
                limit_down = structure_data['limit_down_count']
                
                structure_analysis['limit_analysis'] = {
                    'limit_up_count': limit_up,
                    'limit_down_count': limit_down,
                    'limit_ratio': limit_up - limit_down,
                    'market_sentiment': self._evaluate_limit_sentiment(limit_up, limit_down)
                }
            
            # 涨跌家数
            if 'up_count' in structure_data and 'down_count' in structure_data:
                up_count = structure_data['up_count']
                down_count = structure_data['down_count']
                total_count = up_count + down_count + structure_data.get('unchanged_count', 0)
                
                structure_analysis['breadth'] = {
                    'up_count': up_count,
                    'down_count': down_count,
                    'total_count': total_count,
                    'advance_decline_ratio': up_count / max(down_count, 1),
                    'breadth_level': self._evaluate_market_breadth(up_count, down_count)
                }
            
            # 成交金额分布
            if 'turnover_distribution' in structure_data:
                turnover_dist = structure_data['turnover_distribution']
                structure_analysis['turnover_analysis'] = {
                    'large_cap_turnover': turnover_dist.get('large_cap', 0),
                    'mid_cap_turnover': turnover_dist.get('mid_cap', 0),
                    'small_cap_turnover': turnover_dist.get('small_cap', 0),
                    'structure_preference': self._analyze_turnover_preference(turnover_dist)
                }
            
            # 北向资金
            if 'northbound_flow' in structure_data:
                nb_flow = structure_data['northbound_flow']
                structure_analysis['northbound_analysis'] = {
                    'daily_flow': nb_flow.get('daily', 0),
                    'weekly_flow': nb_flow.get('weekly', 0),
                    'monthly_flow': nb_flow.get('monthly', 0),
                    'flow_trend': self._evaluate_northbound_trend(nb_flow)
                }
            
        except Exception as e:
            self.logger.error(f"市场结构分析错误: {e}")
        
        return structure_analysis
    
    def _analyze_macro_data(self, macro_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析宏观数据"""
        macro_analysis = {}
        
        try:
            # 经济增长指标
            if 'gdp_growth' in macro_data:
                gdp_growth = macro_data['gdp_growth']
                macro_analysis['economic_growth'] = {
                    'gdp_growth': gdp_growth,
                    'growth_level': self._evaluate_gdp_growth(gdp_growth)
                }
            
            # 通胀数据
            if 'cpi' in macro_data or 'ppi' in macro_data:
                macro_analysis['inflation'] = {}
                if 'cpi' in macro_data:
                    cpi = macro_data['cpi']
                    macro_analysis['inflation']['cpi'] = cpi
                    macro_analysis['inflation']['cpi_level'] = self._evaluate_inflation_level(cpi)
                
                if 'ppi' in macro_data:
                    ppi = macro_data['ppi']
                    macro_analysis['inflation']['ppi'] = ppi
                    macro_analysis['inflation']['ppi_level'] = self._evaluate_ppi_level(ppi)
            
            # 货币政策
            if 'interest_rate' in macro_data:
                interest_rate = macro_data['interest_rate']
                macro_analysis['monetary_policy'] = {
                    'current_rate': interest_rate,
                    'policy_stance': self._evaluate_monetary_stance(interest_rate),
                    'rate_trend': macro_data.get('rate_trend', 'neutral')
                }
            
            # PMI数据
            if 'pmi' in macro_data:
                pmi = macro_data['pmi']
                macro_analysis['business_cycle'] = {
                    'manufacturing_pmi': pmi,
                    'cycle_stage': self._evaluate_business_cycle(pmi)
                }
            
            # 汇率影响
            if 'usd_cny' in macro_data:
                usd_cny = macro_data['usd_cny']
                macro_analysis['currency'] = {
                    'usd_cny_rate': usd_cny,
                    'rmb_strength': self._evaluate_rmb_strength(usd_cny),
                    'fx_impact_on_market': self._evaluate_fx_market_impact(usd_cny)
                }
            
        except Exception as e:
            self.logger.error(f"宏观数据分析错误: {e}")
        
        return macro_analysis
    
    def _analyze_international_impact(self, international_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析国际市场影响"""
        international_analysis = {}
        
        try:
            # 美股表现
            if 'us_markets' in international_data:
                us_data = international_data['us_markets']
                international_analysis['us_market_impact'] = {
                    'sp500_change': us_data.get('sp500_change', 0),
                    'nasdaq_change': us_data.get('nasdaq_change', 0),
                    'dow_change': us_data.get('dow_change', 0),
                    'overnight_sentiment': self._evaluate_us_market_sentiment(us_data)
                }
            
            # 亚太市场
            if 'asia_markets' in international_data:
                asia_data = international_data['asia_markets']
                international_analysis['asia_market_impact'] = {
                    'nikkei_change': asia_data.get('nikkei_change', 0),
                    'kospi_change': asia_data.get('kospi_change', 0),
                    'hsi_change': asia_data.get('hsi_change', 0),
                    'regional_trend': self._evaluate_asia_trend(asia_data)
                }
            
            # 大宗商品
            if 'commodities' in international_data:
                commodities_data = international_data['commodities']
                international_analysis['commodities_impact'] = {
                    'oil_change': commodities_data.get('oil_change', 0),
                    'gold_change': commodities_data.get('gold_change', 0),
                    'copper_change': commodities_data.get('copper_change', 0),
                    'commodity_sentiment': self._evaluate_commodity_sentiment(commodities_data)
                }
            
        except Exception as e:
            self.logger.error(f"国际市场影响分析错误: {e}")
        
        return international_analysis
    
    def _assess_market_risks(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """评估市场风险"""
        risk_assessment = {
            'overall_risk_level': 'medium',
            'key_risks': [],
            'risk_factors': {},
            'risk_score': 0.5
        }
        
        try:
            risk_factors = []
            
            # 技术风险
            index_analysis = analysis.get('index_analysis', {})
            if index_analysis:
                market_trend = index_analysis.get('market_trend', {})
                if market_trend.get('trend') == 'bearish':
                    risk_factors.append(('技术面风险', 0.3, '大盘技术面走弱'))
            
            # 结构风险
            market_structure = analysis.get('market_structure', {})
            if 'breadth' in market_structure:
                breadth = market_structure['breadth']
                ad_ratio = breadth.get('advance_decline_ratio', 1)
                if ad_ratio < 0.5:
                    risk_factors.append(('市场广度风险', 0.2, '下跌股票数量过多'))
            
            # 宏观风险
            macro_analysis = analysis.get('macro_analysis', {})
            if 'inflation' in macro_analysis:
                inflation = macro_analysis['inflation']
                cpi = inflation.get('cpi', 2)
                if cpi > 4:
                    risk_factors.append(('通胀风险', 0.25, '通胀水平较高'))
            
            # 国际风险
            international_impact = analysis.get('international_impact', {})
            if 'us_market_impact' in international_impact:
                us_impact = international_impact['us_market_impact']
                sentiment = us_impact.get('overnight_sentiment', 'neutral')
                if sentiment == 'negative':
                    risk_factors.append(('国际市场风险', 0.15, '海外市场表现不佳'))
            
            # 计算综合风险得分
            total_risk_score = sum(score for _, score, _ in risk_factors)
            risk_assessment['risk_score'] = min(1.0, total_risk_score)
            
            # 风险等级评估
            if risk_assessment['risk_score'] > 0.7:
                risk_assessment['overall_risk_level'] = 'high'
            elif risk_assessment['risk_score'] > 0.4:
                risk_assessment['overall_risk_level'] = 'medium'
            else:
                risk_assessment['overall_risk_level'] = 'low'
            
            risk_assessment['key_risks'] = [desc for _, _, desc in risk_factors[:5]]
            risk_assessment['risk_factors'] = {
                name: {'score': score, 'description': desc}
                for name, score, desc in risk_factors
            }
            
        except Exception as e:
            self.logger.error(f"市场风险评估错误: {e}")
        
        return risk_assessment
    
    # 辅助评估函数
    def _evaluate_daily_trend(self, change_pct: float) -> str:
        """评估日内趋势"""
        if change_pct > 2:
            return '强势上涨'
        elif change_pct > 0.5:
            return '上涨'
        elif change_pct > -0.5:
            return '震荡'
        elif change_pct > -2:
            return '下跌'
        else:
            return '大跌'
    
    def _evaluate_volume_level(self, vol_ratio: float) -> str:
        """评估成交量水平"""
        if vol_ratio > 2.0:
            return '放量'
        elif vol_ratio > 1.5:
            return '温和放量'
        elif vol_ratio > 0.8:
            return '正常'
        else:
            return '缩量'
    
    def _analyze_index_trend(self, price_data: List[float]) -> str:
        """分析指数趋势"""
        if len(price_data) < 5:
            return '数据不足'
        
        # 简单的趋势判断：比较最近5天的均价和前5天的均价
        recent_avg = sum(price_data[-5:]) / 5
        previous_avg = sum(price_data[-10:-5]) / 5 if len(price_data) >= 10 else recent_avg
        
        if recent_avg > previous_avg * 1.02:
            return '上升趋势'
        elif recent_avg < previous_avg * 0.98:
            return '下降趋势'
        else:
            return '震荡趋势'
    
    def _calculate_support_resistance(self, price_data: List[float]) -> Dict[str, float]:
        """计算支撑阻力位"""
        if not price_data:
            return {}
        
        recent_prices = price_data[-20:] if len(price_data) >= 20 else price_data
        
        return {
            'support': min(recent_prices),
            'resistance': max(recent_prices),
            'current': recent_prices[-1] if recent_prices else 0
        }
    
    def _calculate_market_trend(self, index_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """计算市场整体趋势"""
        trend_scores = []
        
        for index_code, data in index_analysis.items():
            if index_code == 'market_trend':
                continue
            
            change_pct = data.get('change_pct', 0)
            if change_pct is not None:
                trend_scores.append(change_pct)
        
        if not trend_scores:
            return {'trend': 'neutral', 'strength': 0}
        
        avg_change = sum(trend_scores) / len(trend_scores)
        
        if avg_change > 1:
            trend = 'bullish'
            strength = min(1.0, avg_change / 3)
        elif avg_change < -1:
            trend = 'bearish'
            strength = min(1.0, abs(avg_change) / 3)
        else:
            trend = 'neutral'
            strength = abs(avg_change)
        
        return {
            'trend': trend,
            'strength': strength,
            'average_change': avg_change
        }
    
    def _calculate_sector_strength(self, sector_performance: Dict[str, Any]) -> float:
        """计算板块强度"""
        change_pct = sector_performance.get('change_pct', 0)
        volume_ratio = sector_performance.get('volume_ratio', 1)
        up_ratio = 0
        
        if sector_performance.get('stock_count', 0) > 0:
            up_ratio = sector_performance.get('up_count', 0) / sector_performance['stock_count']
        
        # 综合强度 = 涨跌幅 * 0.5 + 成交量放大系数 * 0.3 + 上涨股票比例 * 0.2
        strength = change_pct * 0.5 + (volume_ratio - 1) * 30 * 0.3 + up_ratio * 20 * 0.2
        
        return strength
    
    def _analyze_sector_rotation(self, sector_performances: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析板块轮动"""
        # 简化的板块轮动分析
        growth_sectors = [s for s in sector_performances if '成长' in s['sector'] or '科技' in s['sector']]
        value_sectors = [s for s in sector_performances if '银行' in s['sector'] or '地产' in s['sector']]
        cyclical_sectors = [s for s in sector_performances if '钢铁' in s['sector'] or '化工' in s['sector']]
        
        growth_avg = sum(s['change_pct'] for s in growth_sectors) / max(len(growth_sectors), 1)
        value_avg = sum(s['change_pct'] for s in value_sectors) / max(len(value_sectors), 1)
        cyclical_avg = sum(s['change_pct'] for s in cyclical_sectors) / max(len(cyclical_sectors), 1)
        
        max_avg = max(growth_avg, value_avg, cyclical_avg)
        
        if max_avg == growth_avg:
            rotation_direction = 'growth'
        elif max_avg == value_avg:
            rotation_direction = 'value'
        else:
            rotation_direction = 'cyclical'
        
        return {
            'rotation_direction': rotation_direction,
            'growth_performance': growth_avg,
            'value_performance': value_avg,
            'cyclical_performance': cyclical_avg
        }
    
    def _evaluate_limit_sentiment(self, limit_up: int, limit_down: int) -> str:
        """评估涨跌停情绪"""
        net_limit = limit_up - limit_down
        if net_limit > 50:
            return '极度乐观'
        elif net_limit > 20:
            return '乐观'
        elif net_limit > -20:
            return '中性'
        elif net_limit > -50:
            return '悲观'
        else:
            return '极度悲观'
    
    def _evaluate_market_breadth(self, up_count: int, down_count: int) -> str:
        """评估市场广度"""
        total = up_count + down_count
        if total == 0:
            return 'neutral'
        
        up_ratio = up_count / total
        if up_ratio > 0.7:
            return 'very_strong'
        elif up_ratio > 0.6:
            return 'strong'
        elif up_ratio > 0.4:
            return 'neutral'
        elif up_ratio > 0.3:
            return 'weak'
        else:
            return 'very_weak'
    
    def _analyze_turnover_preference(self, turnover_dist: Dict[str, float]) -> str:
        """分析成交偏好"""
        large_cap = turnover_dist.get('large_cap', 0)
        small_cap = turnover_dist.get('small_cap', 0)
        
        if large_cap > small_cap * 2:
            return 'large_cap_preference'
        elif small_cap > large_cap * 2:
            return 'small_cap_preference'
        else:
            return 'balanced'
    
    def _evaluate_northbound_trend(self, nb_flow: Dict[str, float]) -> str:
        """评估北向资金趋势"""
        daily = nb_flow.get('daily', 0)
        weekly = nb_flow.get('weekly', 0)
        
        if daily > 3000000000 and weekly > 10000000000:  # 30亿和100亿
            return 'strong_inflow'
        elif daily > 0 and weekly > 0:
            return 'inflow'
        elif daily < -3000000000 and weekly < -10000000000:
            return 'strong_outflow'
        elif daily < 0 and weekly < 0:
            return 'outflow'
        else:
            return 'neutral'
    
    # 宏观数据评估函数
    def _evaluate_gdp_growth(self, gdp_growth: float) -> str:
        """评估GDP增长水平"""
        if gdp_growth > 7:
            return 'high_growth'
        elif gdp_growth > 5:
            return 'moderate_growth'
        elif gdp_growth > 3:
            return 'slow_growth'
        else:
            return 'low_growth'
    
    def _evaluate_inflation_level(self, cpi: float) -> str:
        """评估通胀水平"""
        if cpi > 4:
            return 'high_inflation'
        elif cpi > 2.5:
            return 'moderate_inflation'
        elif cpi > 1:
            return 'low_inflation'
        else:
            return 'deflation_risk'
    
    def _evaluate_ppi_level(self, ppi: float) -> str:
        """评估PPI水平"""
        if ppi > 5:
            return 'high_ppi'
        elif ppi > 0:
            return 'positive_ppi'
        else:
            return 'negative_ppi'
    
    def _evaluate_monetary_stance(self, interest_rate: float) -> str:
        """评估货币政策立场"""
        if interest_rate < 2:
            return 'accommodative'
        elif interest_rate < 4:
            return 'neutral'
        else:
            return 'restrictive'
    
    def _evaluate_business_cycle(self, pmi: float) -> str:
        """评估经济周期阶段"""
        if pmi > 55:
            return 'expansion'
        elif pmi > 50:
            return 'growth'
        elif pmi > 45:
            return 'slowdown'
        else:
            return 'contraction'
    
    def _evaluate_rmb_strength(self, usd_cny: float) -> str:
        """评估人民币强度"""
        if usd_cny < 6.5:
            return 'strong_rmb'
        elif usd_cny < 7.0:
            return 'stable_rmb'
        elif usd_cny < 7.5:
            return 'weak_rmb'
        else:
            return 'very_weak_rmb'
    
    def _evaluate_fx_market_impact(self, usd_cny: float) -> str:
        """评估汇率对市场影响"""
        if usd_cny < 6.5:
            return 'positive_for_consumption'
        elif usd_cny > 7.2:
            return 'positive_for_exports'
        else:
            return 'neutral'
    
    # 国际市场评估函数
    def _evaluate_us_market_sentiment(self, us_data: Dict[str, float]) -> str:
        """评估美股市场情绪"""
        sp500 = us_data.get('sp500_change', 0)
        nasdaq = us_data.get('nasdaq_change', 0)
        
        avg_change = (sp500 + nasdaq) / 2
        
        if avg_change > 1:
            return 'positive'
        elif avg_change < -1:
            return 'negative'
        else:
            return 'neutral'
    
    def _evaluate_asia_trend(self, asia_data: Dict[str, float]) -> str:
        """评估亚洲市场趋势"""
        changes = [v for v in asia_data.values() if isinstance(v, (int, float))]
        if not changes:
            return 'neutral'
        
        avg_change = sum(changes) / len(changes)
        
        if avg_change > 0.5:
            return 'positive'
        elif avg_change < -0.5:
            return 'negative'
        else:
            return 'mixed'
    
    def _evaluate_commodity_sentiment(self, commodities_data: Dict[str, float]) -> str:
        """评估大宗商品情绪"""
        oil_change = commodities_data.get('oil_change', 0)
        copper_change = commodities_data.get('copper_change', 0)
        
        if oil_change > 2 or copper_change > 2:
            return 'inflationary'
        elif oil_change < -2 or copper_change < -2:
            return 'deflationary'
        else:
            return 'stable'
    
    def _format_analysis_request(self, symbol: str, analysis_results: Dict[str, Any]) -> str:
        """格式化分析请求"""
        request = f"""请分析股票 {symbol} 所处的市场环境：

市场分析数据：
"""
        
        # 大盘指数分析
        index_analysis = analysis_results.get('index_analysis', {})
        if 'market_trend' in index_analysis:
            market_trend = index_analysis['market_trend']
            request += f"大盘走势：\n"
            request += f"市场趋势: {market_trend.get('trend', 'N/A')}\n"
            request += f"趋势强度: {market_trend.get('strength', 0):.2f}\n"
            request += f"平均涨跌幅: {market_trend.get('average_change', 0):.2f}%\n"
        
        # 行业板块分析
        sector_analysis = analysis_results.get('sector_analysis', {})
        if sector_analysis:
            request += f"\n行业表现：\n"
            
            if 'top_performers' in sector_analysis:
                top_sectors = sector_analysis['top_performers'][:3]
                request += f"领涨板块: " + ", ".join([f"{s['sector']}({s['change_pct']:.1f}%)" for s in top_sectors]) + "\n"
            
            if 'hot_sectors' in sector_analysis:
                hot_count = len(sector_analysis['hot_sectors'])
                request += f"热点板块数量: {hot_count}个\n"
            
            if 'money_flow' in sector_analysis:
                money_flow = sector_analysis['money_flow']
                net_flow = money_flow.get('net_flow', 0) / 100000000
                request += f"资金净流向: {net_flow:.1f}亿 ({money_flow.get('flow_direction', 'N/A')})\n"
        
        # 市场结构
        market_structure = analysis_results.get('market_structure', {})
        if 'breadth' in market_structure:
            breadth = market_structure['breadth']
            request += f"\n市场结构：\n"
            request += f"涨跌比: {breadth.get('advance_decline_ratio', 0):.2f}\n"
            request += f"市场广度: {breadth.get('breadth_level', 'N/A')}\n"
        
        # 风险评估
        risk_assessment = analysis_results.get('risk_assessment', {})
        if risk_assessment:
            request += f"\n风险评估：\n"
            request += f"整体风险等级: {risk_assessment.get('overall_risk_level', 'N/A')}\n"
            request += f"风险得分: {risk_assessment.get('risk_score', 0):.2f}\n"
            
            if risk_assessment.get('key_risks'):
                request += f"主要风险: {', '.join(risk_assessment['key_risks'][:3])}\n"
        
        # 国际影响
        international_impact = analysis_results.get('international_impact', {})
        if 'us_market_impact' in international_impact:
            us_impact = international_impact['us_market_impact']
            request += f"\n国际市场：\n"
            request += f"美股情绪: {us_impact.get('overnight_sentiment', 'N/A')}\n"
            request += f"标普500: {us_impact.get('sp500_change', 0):.2f}%\n"
        
        request += f"""
请基于以上市场环境数据，从以下几个方面进行分析：
1. 整体市场环境判断（牛市/熊市/震荡市）
2. 当前市场阶段和周期位置
3. 主要市场驱动因素识别
4. 行业轮动和热点分析
5. 市场风险点和机会窗口
6. 对个股 {symbol} 的市场环境影响评估
7. 基于市场环境的操作建议

请给出具体的市场判断和投资策略建议。
"""
        
        return request
    
    def _parse_analysis_result(self, analysis_content: str, analysis_results: Dict[str, Any]) -> tuple:
        """解析分析结果，提取置信度和推理过程"""
        reasoning = []
        confidence = 0.5  # 默认置信度
        
        # 基于市场分析计算基础置信度
        confidence_factors = []
        
        # 市场趋势因子
        index_analysis = analysis_results.get('index_analysis', {})
        if 'market_trend' in index_analysis:
            market_trend = index_analysis['market_trend']
            trend = market_trend.get('trend', 'neutral')
            strength = market_trend.get('strength', 0)
            
            if trend in ['bullish', 'bearish'] and strength > 0.3:
                confidence_factors.append(0.15 * strength)
                reasoning.append(f"市场趋势明确({trend}, 强度{strength:.2f})")
        
        # 市场广度因子
        market_structure = analysis_results.get('market_structure', {})
        if 'breadth' in market_structure:
            breadth_level = market_structure['breadth'].get('breadth_level', 'neutral')
            if breadth_level in ['very_strong', 'very_weak']:
                confidence_factors.append(0.1)
                reasoning.append(f"市场广度{breadth_level}")
        
        # 行业热度因子
        sector_analysis = analysis_results.get('sector_analysis', {})
        if 'hot_sectors' in sector_analysis:
            hot_count = len(sector_analysis['hot_sectors'])
            if hot_count > 5:
                confidence_factors.append(0.1)
                reasoning.append(f"热点板块活跃({hot_count}个)")
        
        # 风险因子（负面）
        risk_assessment = analysis_results.get('risk_assessment', {})
        risk_score = risk_assessment.get('risk_score', 0.5)
        if risk_score > 0.7:
            confidence_factors.append(-0.15)
            reasoning.append("市场风险较高")
        elif risk_score < 0.3:
            confidence_factors.append(0.1)
            reasoning.append("市场风险可控")
        
        # 国际市场因子
        international_impact = analysis_results.get('international_impact', {})
        if 'us_market_impact' in international_impact:
            us_sentiment = international_impact['us_market_impact'].get('overnight_sentiment', 'neutral')
            if us_sentiment == 'positive':
                confidence_factors.append(0.05)
                reasoning.append("海外市场支撑")
            elif us_sentiment == 'negative':
                confidence_factors.append(-0.05)
                reasoning.append("海外市场拖累")
        
        # 计算最终置信度
        confidence = 0.5 + sum(confidence_factors)
        confidence = max(0.1, min(0.9, confidence))  # 限制在0.1-0.9之间
        
        return confidence, reasoning