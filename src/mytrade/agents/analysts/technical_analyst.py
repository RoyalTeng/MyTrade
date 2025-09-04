"""
技术分析师Agent

专门负责技术指标分析和图表模式识别
参考TradingAgents的市场分析师实现，并结合中文本地化
"""

from typing import Dict, Any, List
from ..base_agent import BaseAgent, AgentResponse
import pandas as pd
import numpy as np


class TechnicalAnalyst(BaseAgent):
    """技术分析师"""
    
    def __init__(self, agent_id: str, llm_adapter, config: Dict[str, Any] = None):
        super().__init__(agent_id, "技术分析师", llm_adapter, config)
    
    def get_system_prompt(self) -> str:
        """获取技术分析师的系统提示词"""
        return """你是一位专业的技术分析师，具备以下专业能力：

核心职责：
1. 分析股票的技术指标和图表模式
2. 识别支撑位和阻力位
3. 评估价格趋势和动量
4. 提供技术面的买卖建议

分析维度：
- 移动平均线分析（MA5, MA10, MA20, MA60）
- 动量指标（RSI, MACD, KDJ）
- 成交量分析（量价关系）  
- 布林带和波动率分析
- 支撑阻力位识别
- 图表形态识别

输出要求：
1. 提供明确的技术面评级（强烈看多/看多/中性/看空/强烈看空）
2. 给出具体的买入/卖出/持有建议
3. 说明关键的支撑位和阻力位
4. 评估技术面的风险点
5. 提供置信度评分(0-1)

注意事项：
- 基于客观的技术指标数据进行分析
- 避免主观臆测，依据数据说话
- 考虑多个指标的综合信号
- 关注中国A股的技术特点
"""

    def get_role_responsibility(self) -> str:
        """获取角色职责描述"""
        return "股票技术指标分析、图表模式识别和技术面交易建议"
    
    def get_required_inputs(self) -> List[str]:
        """获取必需的输入参数"""
        return ['symbol', 'price_data', 'volume_data']
    
    def process(self, inputs: Dict[str, Any]) -> AgentResponse:
        """处理技术分析"""
        self.validate_inputs(inputs)
        
        symbol = inputs['symbol']
        price_data = inputs.get('price_data')
        volume_data = inputs.get('volume_data')
        
        # 更新状态
        self.update_state({
            'symbol': symbol,
            'analysis_time': self.state.timestamp,
            'data_points': len(price_data) if price_data else 0
        })
        
        # 计算技术指标
        technical_indicators = self._calculate_indicators(price_data, volume_data)
        
        # 构建分析消息
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": self._format_analysis_request(symbol, technical_indicators)}
        ]
        
        # 调用LLM进行分析
        analysis_content = self.call_llm(messages, temperature=0.3)
        
        # 解析分析结果
        confidence, reasoning = self._parse_analysis_result(analysis_content, technical_indicators)
        
        self.logger.info(f"技术分析师完成 {symbol} 的分析，置信度: {confidence}")
        
        return self.format_output(
            content=analysis_content,
            confidence=confidence,
            reasoning=reasoning,
            symbol=symbol,
            technical_indicators=technical_indicators
        )
    
    def _calculate_indicators(self, price_data, volume_data) -> Dict[str, Any]:
        """计算技术指标"""
        if not price_data:
            return {}
        
        try:
            # 转换为DataFrame方便计算
            if isinstance(price_data, dict):
                df = pd.DataFrame(price_data)
            elif isinstance(price_data, list):
                df = pd.DataFrame(price_data)
            else:
                df = price_data
            
            indicators = {}
            
            if 'close' in df.columns:
                close_prices = df['close']
                
                # 移动平均线
                for period in [5, 10, 20, 60]:
                    if len(close_prices) >= period:
                        ma_value = close_prices.rolling(period).mean().iloc[-1]
                        indicators[f'ma{period}'] = float(ma_value) if pd.notna(ma_value) else None
                    else:
                        indicators[f'ma{period}'] = None
                
                # RSI
                if len(close_prices) >= 14:
                    delta = close_prices.diff()
                    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                    # 避免除零错误
                    loss = loss.replace(0, float('inf'))  # 当loss为0时，RSI为100
                    rs = gain / loss
                    rsi_value = (100 - (100 / (1 + rs))).iloc[-1]
                    # 检查是否为有效数值
                    if pd.notna(rsi_value) and not pd.isinf(rsi_value):
                        indicators['rsi'] = float(rsi_value)
                    else:
                        indicators['rsi'] = None
                
                # MACD
                if len(close_prices) >= 26:
                    exp1 = close_prices.ewm(span=12).mean()
                    exp2 = close_prices.ewm(span=26).mean()
                    macd = exp1 - exp2
                    signal = macd.ewm(span=9).mean()
                    
                    macd_value = macd.iloc[-1]
                    signal_value = signal.iloc[-1] 
                    histogram_value = (macd - signal).iloc[-1]
                    
                    indicators['macd'] = float(macd_value) if pd.notna(macd_value) else None
                    indicators['macd_signal'] = float(signal_value) if pd.notna(signal_value) else None
                    indicators['macd_histogram'] = float(histogram_value) if pd.notna(histogram_value) else None
                
                # 布林带
                if len(close_prices) >= 20:
                    bb_middle = close_prices.rolling(20).mean()
                    bb_std = close_prices.rolling(20).std()
                    
                    bb_upper_value = (bb_middle + 2 * bb_std).iloc[-1]
                    bb_middle_value = bb_middle.iloc[-1]
                    bb_lower_value = (bb_middle - 2 * bb_std).iloc[-1]
                    
                    indicators['bb_upper'] = float(bb_upper_value) if pd.notna(bb_upper_value) else None
                    indicators['bb_middle'] = float(bb_middle_value) if pd.notna(bb_middle_value) else None
                    indicators['bb_lower'] = float(bb_lower_value) if pd.notna(bb_lower_value) else None
                
                # 当前价格
                current_price = close_prices.iloc[-1]
                indicators['current_price'] = float(current_price) if pd.notna(current_price) else None
                
                # 价格变化
                if len(close_prices) >= 2:
                    current_price = close_prices.iloc[-1]
                    prev_price = close_prices.iloc[-2]
                    if pd.notna(current_price) and pd.notna(prev_price) and prev_price != 0:
                        indicators['price_change'] = ((current_price - prev_price) / prev_price) * 100
                    else:
                        indicators['price_change'] = None
            
            # 成交量分析
            if volume_data and 'volume' in df.columns:
                volume = df['volume']
                if len(volume) >= 5:
                    volume_ma5 = volume.rolling(5).mean().iloc[-1]
                    indicators['volume_ma5'] = float(volume_ma5) if pd.notna(volume_ma5) else None
                    
                    current_volume = volume.iloc[-1]
                    if pd.notna(volume_ma5) and pd.notna(current_volume) and volume_ma5 > 0:
                        indicators['volume_ratio'] = float(current_volume / volume_ma5)
                    else:
                        indicators['volume_ratio'] = 1.0
            
            return indicators
            
        except Exception as e:
            self.logger.error(f"技术指标计算失败: {e}")
            return {}
    
    def _format_analysis_request(self, symbol: str, indicators: Dict[str, Any]) -> str:
        """格式化分析请求"""
        request = f"""请分析股票 {symbol} 的技术面情况：

技术指标数据：
"""
        
        if indicators:
            if indicators.get('current_price'):
                request += f"当前价格: {indicators['current_price']:.2f}元\n"
            
            if indicators.get('price_change'):
                request += f"价格变化: {indicators['price_change']:+.2f}%\n"
            
            # 移动平均线
            ma_data = []
            for period in [5, 10, 20, 60]:
                ma_key = f'ma{period}'
                ma_value = indicators.get(ma_key)
                if ma_value is not None:
                    ma_data.append(f"MA{period}: {ma_value:.2f}")
            if ma_data:
                request += f"移动平均线: {', '.join(ma_data)}\n"
            
            # 动量指标
            rsi_value = indicators.get('rsi')
            if rsi_value is not None:
                request += f"RSI(14): {rsi_value:.2f}\n"
            
            macd_value = indicators.get('macd')
            macd_signal_value = indicators.get('macd_signal')
            if macd_value is not None and macd_signal_value is not None:
                request += f"MACD: {macd_value:.4f}, 信号线: {macd_signal_value:.4f}\n"
            
            # 布林带
            bb_upper = indicators.get('bb_upper')
            bb_middle = indicators.get('bb_middle')
            bb_lower = indicators.get('bb_lower')
            if all(x is not None for x in [bb_upper, bb_middle, bb_lower]):
                request += f"布林带: 上轨 {bb_upper:.2f}, 中轨 {bb_middle:.2f}, 下轨 {bb_lower:.2f}\n"
            
            # 成交量
            volume_ratio = indicators.get('volume_ratio')
            if volume_ratio is not None:
                request += f"量比: {volume_ratio:.2f}\n"
        
        request += """
请基于以上技术指标，从以下几个方面进行分析：
1. 趋势方向判断（上升趋势/下降趋势/震荡整理）
2. 动量强弱评估
3. 超买超卖情况
4. 关键支撑阻力位
5. 成交量配合情况
6. 整体技术面评级和建议

请给出具体的分析结论和投资建议。
"""
        
        return request
    
    def _parse_analysis_result(self, analysis_content: str, indicators: Dict[str, Any]) -> tuple:
        """解析分析结果，提取置信度和推理过程"""
        reasoning = []
        confidence = 0.5  # 默认置信度
        
        # 基于技术指标计算基础置信度
        confidence_factors = []
        
        # RSI因子
        if indicators.get('rsi'):
            rsi = indicators['rsi']
            if rsi > 70:
                confidence_factors.append(-0.1)  # 超买降低置信度
                reasoning.append(f"RSI超买({rsi:.1f})")
            elif rsi < 30:
                confidence_factors.append(0.1)   # 超卖提高置信度
                reasoning.append(f"RSI超卖({rsi:.1f})")
        
        # MACD因子
        if indicators.get('macd') and indicators.get('macd_signal'):
            if indicators['macd'] > indicators['macd_signal']:
                confidence_factors.append(0.1)
                reasoning.append("MACD金叉")
            else:
                confidence_factors.append(-0.1)
                reasoning.append("MACD死叉")
        
        # 均线因子
        current_price = indicators.get('current_price')
        ma5 = indicators.get('ma5')
        ma20 = indicators.get('ma20')
        
        # 只有在所有价格都不为None时才进行比较
        if all(x is not None for x in [current_price, ma5, ma20]):
            if current_price > ma5 > ma20:
                confidence_factors.append(0.15)
                reasoning.append("多头排列")
            elif current_price < ma5 < ma20:
                confidence_factors.append(-0.15)
                reasoning.append("空头排列")
        
        # 成交量因子
        if indicators.get('volume_ratio', 1) > 1.5:
            confidence_factors.append(0.05)
            reasoning.append("成交量放大")
        
        # 计算最终置信度
        confidence = 0.5 + sum(confidence_factors)
        confidence = max(0.1, min(0.9, confidence))  # 限制在0.1-0.9之间
        
        return confidence, reasoning