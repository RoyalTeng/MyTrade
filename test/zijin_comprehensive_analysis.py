#!/usr/bin/env python3
"""
紫金矿业(601899)全面深度分析系统
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# 添加src到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# 导入编码修复工具和核心模块
from test_encoding_fix import safe_print
from mytrade.config import get_config_manager
from mytrade.data.market_data_fetcher import MarketDataFetcher, DataSourceConfig
from mytrade.trading import SignalGenerator
from mytrade.logging import InterpretableLogger
from mytrade.backtest import PortfolioManager

class ZijinAnalyzer:
    def __init__(self):
        self.stock_code = "601899"
        self.stock_name = "紫金矿业"
        self.analysis_results = {}
        
    def setup_components(self):
        """初始化分析组件"""
        try:
            config = DataSourceConfig(source="akshare", cache_dir=Path("data/cache"))
            self.fetcher = MarketDataFetcher(config)
            
            config_manager = get_config_manager("config.yaml")
            config = config_manager.get_config()
            self.signal_generator = SignalGenerator(config)
            
            self.portfolio = PortfolioManager(initial_cash=100000)
            
            self.logger = InterpretableLogger(
                log_dir="logs/zijin_analysis",
                enable_console_output=False
            )
            
            safe_print("分析组件初始化成功")
            return True
        except Exception as e:
            safe_print(f"组件初始化失败: {e}")
            return False
    
    def collect_data(self):
        """收集实时数据"""
        safe_print("\\n=== 数据收集阶段 ===")
        
        try:
            end_date = datetime.now().strftime("%Y%m%d")
            start_date = (datetime.now() - timedelta(days=60)).strftime("%Y%m%d")
            
            safe_print(f"获取数据范围: {start_date} 至 {end_date}")
            
            data = self.fetcher.fetch_history(self.stock_code, start_date, end_date)
            
            if not data.empty:
                latest = data.iloc[-1]
                prev = data.iloc[-2] if len(data) > 1 else latest
                
                daily_change = ((latest['close'] - prev['close']) / prev['close']) * 100 if len(data) > 1 else 0
                
                self.analysis_results['basic_info'] = {
                    'current_price': latest['close'],
                    'daily_change': daily_change,
                    'volume': latest['volume'],
                    'turnover': latest['volume'] * latest['close'],
                    'high': latest['high'],
                    'low': latest['low'],
                    'open': latest['open'],
                    'data_points': len(data)
                }
                
                safe_print(f"成功获取 {len(data)} 个交易日数据")
                safe_print(f"当前价格: {latest['close']:.2f}元")
                safe_print(f"日涨跌幅: {daily_change:+.2f}%")
                safe_print(f"成交量: {latest['volume']:,.0f}股")
                safe_print(f"成交额: {latest['volume'] * latest['close'] / 10000:.0f}万元")
                
                return data
            else:
                safe_print("数据获取失败")
                return None
                
        except Exception as e:
            safe_print(f"数据收集失败: {e}")
            return None
    
    def technical_analysis(self, data):
        """技术分析"""
        safe_print("\\n=== 技术分析阶段 ===")
        
        if data is None or data.empty:
            safe_print("数据不足，跳过技术分析")
            return None
        
        try:
            # 计算技术指标
            data['MA5'] = data['close'].rolling(window=5).mean()
            data['MA10'] = data['close'].rolling(window=10).mean()
            data['MA20'] = data['close'].rolling(window=20).mean()
            
            # RSI指标
            delta = data['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            data['RSI'] = 100 - (100 / (1 + rs))
            
            # MACD指标
            exp1 = data['close'].ewm(span=12).mean()
            exp2 = data['close'].ewm(span=26).mean()
            data['MACD'] = exp1 - exp2
            data['Signal'] = data['MACD'].ewm(span=9).mean()
            
            # 布林带
            data['BB_Middle'] = data['close'].rolling(window=20).mean()
            bb_std = data['close'].rolling(window=20).std()
            data['BB_Upper'] = data['BB_Middle'] + 2 * bb_std
            data['BB_Lower'] = data['BB_Middle'] - 2 * bb_std
            
            latest = data.iloc[-1]
            
            # 趋势判断
            trend_signals = []
            if latest['close'] > latest['MA5'] > latest['MA20']:
                trend_signals.append("多头排列")
            elif latest['close'] < latest['MA5'] < latest['MA20']:
                trend_signals.append("空头排列")
            else:
                trend_signals.append("震荡整理")
            
            if latest['RSI'] > 70:
                trend_signals.append("RSI超买")
            elif latest['RSI'] < 30:
                trend_signals.append("RSI超卖")
            
            if latest['MACD'] > latest['Signal']:
                trend_signals.append("MACD金叉")
            else:
                trend_signals.append("MACD死叉")
            
            # 支撑阻力位
            recent_high = data['high'].tail(20).max()
            recent_low = data['low'].tail(20).min()
            
            self.analysis_results['technical'] = {
                'current_price': latest['close'],
                'ma5': latest['MA5'],
                'ma10': latest['MA10'],
                'ma20': latest['MA20'],
                'rsi': latest['RSI'],
                'macd': latest['MACD'],
                'signal': latest['Signal'],
                'bb_upper': latest['BB_Upper'],
                'bb_middle': latest['BB_Middle'],
                'bb_lower': latest['BB_Lower'],
                'trend_signals': trend_signals,
                'support': recent_low,
                'resistance': recent_high
            }
            
            safe_print("技术指标计算完成:")
            safe_print(f"  5日均线: {latest['MA5']:.2f}元")
            safe_print(f"  20日均线: {latest['MA20']:.2f}元")
            safe_print(f"  RSI(14): {latest['RSI']:.1f}")
            safe_print(f"  趋势信号: {', '.join(trend_signals)}")
            safe_print(f"  支撑位: {recent_low:.2f}元")
            safe_print(f"  阻力位: {recent_high:.2f}元")
            
            return data
            
        except Exception as e:
            safe_print(f"技术分析失败: {e}")
            return data
    
    def generate_signals(self):
        """生成交易信号"""
        safe_print("\\n=== 信号生成阶段 ===")
        
        try:
            # 启动交易会话
            session_id = self.logger.start_trading_session(
                symbol=self.stock_code,
                date=datetime.now().strftime("%Y-%m-%d"),
                context={"analysis_type": "comprehensive", "stock_name": self.stock_name}
            )
            
            safe_print(f"交易分析会话启动: {session_id}")
            
            # 记录分析步骤
            self.logger.log_analysis_step(
                agent_type="TECHNICAL_ANALYST",
                input_data={"symbol": self.stock_code, "name": self.stock_name},
                analysis_process="综合技术指标分析",
                conclusion="基于多项技术指标进行综合评估",
                confidence=0.8,
                reasoning=["移动平均线分析", "RSI指标评估", "MACD信号判断", "布林带位置分析"]
            )
            
            # 生成AI信号
            safe_print("正在生成AI量化信号...")
            signal_report = self.signal_generator.generate_signal(self.stock_code)
            
            if signal_report:
                signal = signal_report.signal
                action_icon = {"BUY": "买入", "SELL": "卖出", "HOLD": "持有"}.get(signal.action, "未知")
                
                safe_print(f"AI信号生成成功:")
                safe_print(f"  信号类型: {action_icon}")
                safe_print(f"  置信度: {signal.confidence:.2f}")
                
                # 记录决策点
                self.logger.log_decision_point(
                    context=f"{self.stock_name}交易信号决策",
                    options=[
                        {"action": "BUY", "reason": "技术指标偏多"},
                        {"action": "HOLD", "reason": "保持观望"},
                        {"action": "SELL", "reason": "技术指标偏空"}
                    ],
                    chosen_option={"action": signal.action},
                    rationale=f"基于AI量化模型分析，置信度{signal.confidence:.2f}",
                    confidence=signal.confidence
                )
                
                self.analysis_results['signals'] = {
                    'ai_action': signal.action,
                    'ai_confidence': signal.confidence,
                    'timestamp': datetime.now().isoformat()
                }
                
                # 结束会话
                summary = self.logger.end_trading_session(
                    final_decision={"action": signal.action, "confidence": signal.confidence},
                    performance_data={"analysis_type": "comprehensive"}
                )
                
                safe_print(f"分析会话完成，记录 {summary['total_analysis_steps']} 个分析步骤")
                
                return True
            else:
                safe_print("AI信号生成失败")
                return False
                
        except Exception as e:
            safe_print(f"信号生成失败: {e}")
            return False
    
    def risk_assessment(self, data):
        """风险评估"""
        safe_print("\\n=== 风险评估阶段 ===")
        
        if data is None or data.empty:
            safe_print("数据不足，跳过风险评估")
            return
        
        try:
            # 计算波动率
            returns = data['close'].pct_change().dropna()
            volatility_20d = returns.rolling(window=20).std() * np.sqrt(252) * 100
            current_volatility = volatility_20d.iloc[-1]
            
            # 最大回撤
            peak = data['close'].expanding().max()
            drawdown = (data['close'] - peak) / peak * 100
            max_drawdown = drawdown.min()
            
            # VaR计算
            var_5 = np.percentile(returns, 5) * 100
            
            # 风险评分
            risk_score = 0
            risk_factors = []
            
            if current_volatility > 35:
                risk_score += 2
                risk_factors.append("高波动性")
            elif current_volatility > 25:
                risk_score += 1
                risk_factors.append("中等波动性")
            
            if max_drawdown < -20:
                risk_score += 2
                risk_factors.append("大幅回撤风险")
            elif max_drawdown < -10:
                risk_score += 1
                risk_factors.append("适度回撤风险")
            
            if abs(var_5) > 5:
                risk_score += 1
                risk_factors.append("日损失风险较大")
            
            # 风险等级
            if risk_score >= 4:
                risk_level = "高风险"
            elif risk_score >= 2:
                risk_level = "中等风险"
            else:
                risk_level = "低风险"
            
            self.analysis_results['risk'] = {
                'volatility_20d': current_volatility,
                'max_drawdown': max_drawdown,
                'var_5_percent': var_5,
                'risk_level': risk_level,
                'risk_score': risk_score,
                'risk_factors': risk_factors
            }
            
            safe_print("风险评估完成:")
            safe_print(f"  20日波动率: {current_volatility:.1f}%")
            safe_print(f"  最大回撤: {max_drawdown:.1f}%")
            safe_print(f"  VaR(5%): {var_5:.1f}%")
            safe_print(f"  风险等级: {risk_level}")
            if risk_factors:
                safe_print(f"  风险因子: {', '.join(risk_factors)}")
            
        except Exception as e:
            safe_print(f"风险评估失败: {e}")
    
    def sector_comparison(self):
        """行业对比"""
        safe_print("\\n=== 行业对比阶段 ===")
        
        peers = {
            "山东黄金": "600547",
            "中金黄金": "600489", 
            "赤峰黄金": "600988",
            "银泰黄金": "000975"
        }
        
        peer_results = {}
        
        for name, code in peers.items():
            try:
                signal_report = self.signal_generator.generate_signal(code)
                if signal_report:
                    signal = signal_report.signal
                    peer_results[code] = {
                        'name': name,
                        'action': signal.action,
                        'confidence': signal.confidence
                    }
                    safe_print(f"  {name}({code}): {signal.action} (置信度: {signal.confidence:.2f})")
            except Exception as e:
                safe_print(f"  {name}({code}): 分析失败")
        
        if peer_results:
            buy_count = sum(1 for p in peer_results.values() if p["action"] == "BUY")
            sell_count = sum(1 for p in peer_results.values() if p["action"] == "SELL")
            total_count = len(peer_results)
            
            safe_print(f"\\n行业信号统计:")
            safe_print(f"  买入信号: {buy_count}/{total_count}")
            safe_print(f"  卖出信号: {sell_count}/{total_count}")
            
            # 行业评级
            if buy_count > sell_count:
                industry_rating = "行业偏强"
            elif sell_count > buy_count:
                industry_rating = "行业偏弱"
            else:
                industry_rating = "行业中性"
            
            safe_print(f"  行业评级: {industry_rating}")
            
            self.analysis_results['sector'] = {
                'peers': peer_results,
                'industry_rating': industry_rating,
                'buy_ratio': buy_count / total_count,
                'sell_ratio': sell_count / total_count
            }
    
    def generate_recommendations(self):
        """生成投资建议"""
        safe_print("\\n=== 建议生成阶段 ===")
        
        try:
            recommendations = []
            risk_warnings = []
            
            # 基于AI信号
            signals = self.analysis_results.get('signals', {})
            if signals:
                action = signals.get('ai_action', '')
                confidence = signals.get('ai_confidence', 0)
                
                if action == "BUY" and confidence > 0.7:
                    recommendations.append("AI模型强烈推荐买入")
                elif action == "BUY" and confidence > 0.5:
                    recommendations.append("AI模型建议关注买入机会")
                elif action == "SELL" and confidence > 0.7:
                    recommendations.append("AI模型建议减持")
                else:
                    recommendations.append("AI模型建议保持观望")
            
            # 基于技术分析
            technical = self.analysis_results.get('technical', {})
            if technical:
                trend_signals = technical.get('trend_signals', [])
                if "多头排列" in trend_signals:
                    recommendations.append("技术面呈多头态势")
                elif "空头排列" in trend_signals:
                    recommendations.append("技术面偏弱")
                
                if "RSI超买" in trend_signals:
                    risk_warnings.append("RSI超买，注意回调风险")
                elif "RSI超卖" in trend_signals:
                    recommendations.append("RSI超卖，关注反弹机会")
            
            # 基于风险评估
            risk = self.analysis_results.get('risk', {})
            if risk:
                risk_level = risk.get('risk_level', '')
                risk_factors = risk.get('risk_factors', [])
                
                if "高风险" in risk_level:
                    risk_warnings.append("高风险警示，建议控制仓位")
                
                if risk_factors:
                    risk_warnings.append(f"主要风险: {', '.join(risk_factors)}")
            
            # 综合评分
            score = 0
            if signals.get('ai_action') == 'BUY':
                score += signals.get('ai_confidence', 0) * 40
            
            if "多头排列" in technical.get('trend_signals', []):
                score += 20
            
            sector = self.analysis_results.get('sector', {})
            if "行业偏强" in sector.get('industry_rating', ''):
                score += 15
            
            risk_penalty = risk.get('risk_score', 0) * 5
            score = max(0, score - risk_penalty)
            
            if score >= 70:
                final_rating = "强烈推荐"
            elif score >= 50:
                final_rating = "值得关注"
            elif score >= 30:
                final_rating = "中性观望"
            else:
                final_rating = "暂不推荐"
            
            self.analysis_results['recommendations'] = {
                'core_recommendations': recommendations,
                'risk_warnings': risk_warnings,
                'comprehensive_score': score,
                'final_rating': final_rating
            }
            
            safe_print("投资建议生成完成:")
            safe_print(f"  综合评分: {score:.0f}/100")
            safe_print(f"  最终评级: {final_rating}")
            
            safe_print("\\n核心建议:")
            for i, rec in enumerate(recommendations, 1):
                safe_print(f"  {i}. {rec}")
            
            if risk_warnings:
                safe_print("\\n风险提示:")
                for i, warning in enumerate(risk_warnings, 1):
                    safe_print(f"  {i}. {warning}")
            
        except Exception as e:
            safe_print(f"建议生成失败: {e}")
    
    def run_analysis(self):
        """运行完整分析"""
        safe_print("="*80)
        safe_print(f"           {self.stock_name}({self.stock_code}) 专项深度分析")
        safe_print("="*80)
        
        today = datetime.now()
        safe_print(f"分析日期: {today.strftime('%Y年%m月%d日')}")
        safe_print(f"分析时间: {today.strftime('%H:%M:%S')}")
        safe_print(f"分析系统: MyTrade v1.0")
        
        try:
            # 初始化组件
            if not self.setup_components():
                return False
            
            # 执行分析流程
            data = self.collect_data()
            if data is None:
                return False
            
            enhanced_data = self.technical_analysis(data)
            self.generate_signals()
            self.risk_assessment(enhanced_data)
            self.sector_comparison()
            self.generate_recommendations()
            
            safe_print("\\n" + "="*80)
            safe_print("分析完成概况")
            safe_print("="*80)
            safe_print("✓ 数据收集: 完成")
            safe_print("✓ 技术分析: 完成")
            safe_print("✓ 信号生成: 完成")
            safe_print("✓ 风险评估: 完成")
            safe_print("✓ 行业对比: 完成")
            safe_print("✓ 投资建议: 完成")
            
            return True
            
        except Exception as e:
            safe_print(f"分析过程发生错误: {e}")
            return False

def main():
    analyzer = ZijinAnalyzer()
    success = analyzer.run_analysis()
    
    if success:
        safe_print("\\n正在生成详细分析报告...")
        try:
            generate_report(analyzer.analysis_results)
            safe_print("✓ 详细报告已生成: test/紫金矿业分析报告.md")
        except Exception as e:
            safe_print(f"报告生成失败: {e}")
    
    return success

def generate_report(results):
    """生成分析报告"""
    timestamp = datetime.now()
    
    basic_info = results.get('basic_info', {})
    technical = results.get('technical', {})
    signals = results.get('signals', {})
    risk = results.get('risk', {})
    sector = results.get('sector', {})
    recommendations = results.get('recommendations', {})
    
    report = f'''# 紫金矿业(601899) 专项分析报告

**生成时间**: {timestamp.strftime('%Y年%m月%d日 %H:%M:%S')}  
**分析系统**: MyTrade量化交易系统 v1.0  
**标的代码**: 601899  
**标的名称**: 紫金矿业  
**所属行业**: 有色金属-黄金  

---

## 执行摘要

本报告对紫金矿业(601899)进行全面分析，运用MyTrade量化系统的多维度分析框架，为投资者提供专业投资建议。

**核心数据**:
- 当前价格: ¥{basic_info.get('current_price', 0):.2f}
- 日涨跌幅: {basic_info.get('daily_change', 0):+.2f}%
- AI交易信号: {signals.get('ai_action', 'N/A')} (置信度: {signals.get('ai_confidence', 0):.2f})
- 综合评分: {recommendations.get('comprehensive_score', 0):.0f}/100
- 最终评级: {recommendations.get('final_rating', 'N/A')}

---

## 实时数据概览

- **当前价格**: ¥{basic_info.get('current_price', 0):.2f}
- **日涨跌幅**: {basic_info.get('daily_change', 0):+.2f}%
- **今日开盘**: ¥{basic_info.get('open', 0):.2f}
- **今日最高**: ¥{basic_info.get('high', 0):.2f}
- **今日最低**: ¥{basic_info.get('low', 0):.2f}
- **成交量**: {basic_info.get('volume', 0):,.0f}股
- **成交额**: {basic_info.get('turnover', 0) / 10000:.0f}万元

**数据说明**: 基于最近{basic_info.get('data_points', 0)}个交易日数据分析

---

## 技术分析

### 移动平均线分析
- **5日均线**: ¥{technical.get('ma5', 0):.2f}
- **10日均线**: ¥{technical.get('ma10', 0):.2f}
- **20日均线**: ¥{technical.get('ma20', 0):.2f}

### 技术指标
- **RSI(14)**: {technical.get('rsi', 0):.1f}
- **MACD**: {technical.get('macd', 0):.4f}
- **MACD信号线**: {technical.get('signal', 0):.4f}

### 布林带分析
- **上轨**: ¥{technical.get('bb_upper', 0):.2f}
- **中轨**: ¥{technical.get('bb_middle', 0):.2f}
- **下轨**: ¥{technical.get('bb_lower', 0):.2f}

### 关键价位
- **支撑位**: ¥{technical.get('support', 0):.2f}
- **阻力位**: ¥{technical.get('resistance', 0):.2f}

**技术面评估**: {', '.join(technical.get('trend_signals', []))}

---

## AI量化交易信号

- **信号类型**: {signals.get('ai_action', 'N/A')}
- **置信度**: {signals.get('ai_confidence', 0):.2f}
- **生成时间**: {signals.get('timestamp', 'N/A')}

**信号解读**: '''
    
    ai_action = signals.get('ai_action', '')
    ai_confidence = signals.get('ai_confidence', 0)
    
    if ai_action == 'BUY':
        if ai_confidence > 0.8:
            report += "AI模型给出强烈买入建议，多项指标显示积极信号。"
        elif ai_confidence > 0.6:
            report += "AI模型倾向买入，建议谨慎分批建仓。"
        else:
            report += "AI模型偏向买入，建议小仓位试探。"
    elif ai_action == 'SELL':
        if ai_confidence > 0.8:
            report += "AI模型给出强烈卖出信号，建议及时减仓。"
        elif ai_confidence > 0.6:
            report += "AI模型倾向卖出，建议控制仓位。"
        else:
            report += "AI模型偏向卖出，建议谨慎观察。"
    else:
        report += "AI模型建议保持现有仓位，等待更明确信号。"
    
    report += f'''

---

## 行业对比分析

**行业评级**: {sector.get('industry_rating', 'N/A')}

**同行业对比**:'''
    
    peers = sector.get('peers', {})
    if peers:
        report += '''
| 股票名称 | 股票代码 | AI信号 | 置信度 |
|---------|---------|--------|--------|
'''
        for code, data in peers.items():
            name = data.get('name', '')
            action = data.get('action', '')
            confidence = data.get('confidence', 0)
            report += f"| {name} | {code} | {action} | {confidence:.2f} |\n"
    
    buy_ratio = sector.get('buy_ratio', 0)
    report += f'''

**行业分析**: 买入信号比例 {buy_ratio*100:.0f}%'''
    
    if buy_ratio > 0.6:
        report += "，行业整体偏强。"
    elif sector.get('sell_ratio', 0) > 0.6:
        report += "，行业整体偏弱。"
    else:
        report += "，行业表现分化。"
    
    report += f'''

---

## 风险评估

- **20日波动率**: {risk.get('volatility_20d', 0):.1f}%
- **最大回撤**: {risk.get('max_drawdown', 0):.1f}%
- **VaR(5%)**: {risk.get('var_5_percent', 0):.1f}%
- **风险等级**: {risk.get('risk_level', 'N/A')}

**风险因素**: {', '.join(risk.get('risk_factors', []))}

**风险管控建议**:
1. 仓位控制: 单一标的仓位不超过总资产20%
2. 止损设置: 建议设置-8%止损线
3. 分批操作: 避免一次性重仓
4. 关注大盘: 结合市场整体走势

---

## 最终投资建议

**投资评分**: {recommendations.get('comprehensive_score', 0):.0f}/100  
**最终评级**: {recommendations.get('final_rating', 'N/A')}

**核心建议**:'''
    
    core_recs = recommendations.get('core_recommendations', [])
    for i, rec in enumerate(core_recs, 1):
        report += f"\n{i}. {rec}"
    
    risk_warnings = recommendations.get('risk_warnings', [])
    if risk_warnings:
        report += "\n\n**风险提示**:"
        for i, warning in enumerate(risk_warnings, 1):
            report += f"\n{i}. {warning}"
    
    score = recommendations.get('comprehensive_score', 0)
    
    report += f'''

**操作指导**: '''
    
    if score >= 70:
        report += "该股票获得高分评价，建议重点关注。可考虑在技术面确认后分批建仓。"
    elif score >= 50:
        report += "该股票具有一定投资价值，建议适度配置。"
    elif score >= 30:
        report += "该股票表现平平，建议保持观望。"
    else:
        report += "该股票当前风险较大，不建议新增投资。"
    
    report += f'''

---

## 免责声明

本报告仅供投资参考，不构成投资建议。投资有风险，入市需谨慎。
建议投资者根据自身风险承受能力进行决策，并在专业投资顾问指导下操作。

---

**报告生成**: MyTrade量化交易系统  
**生成时间**: {timestamp.strftime('%Y年%m月%d日 %H:%M:%S')}
'''
    
    # 保存报告
    report_file = Path(__file__).parent / "紫金矿业分析报告.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)