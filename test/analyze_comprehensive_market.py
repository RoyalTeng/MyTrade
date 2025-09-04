#!/usr/bin/env python3
"""
A股全面行情分析系统

使用MyTrade量化交易系统进行深度A股市场分析，
生成包含技术分析、基本面分析和投资建议的详细报告。
"""

import sys
import os
import json
import traceback
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd

# 添加src到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# 导入编码修复工具
from test_encoding_fix import safe_print

# 导入MyTrade核心模块
from mytrade.config import get_config_manager
from mytrade.data.market_data_fetcher import MarketDataFetcher, DataSourceConfig
from mytrade.trading import SignalGenerator
from mytrade.logging import InterpretableLogger
from mytrade.backtest import PortfolioManager

class ComprehensiveMarketAnalyzer:
    """全面的市场分析器"""
    
    def __init__(self):
        """初始化分析器"""
        self.analysis_data = {
            "timestamp": datetime.now(),
            "market_indices": {},
            "sector_analysis": {},
            "individual_stocks": {},
            "technical_indicators": {},
            "market_sentiment": {},
            "recommendations": []
        }
        
        # 初始化组件
        self.setup_components()
        
    def setup_components(self):
        """初始化分析组件"""
        try:
            # 数据获取器
            config = DataSourceConfig(
                source="akshare",
                cache_dir=Path("data/cache")
            )
            self.fetcher = MarketDataFetcher(config)
            
            # 信号生成器
            config_manager = get_config_manager("config.yaml")
            config = config_manager.get_config()
            self.signal_generator = SignalGenerator(config)
            
            # 投资组合管理器
            self.portfolio = PortfolioManager(initial_cash=100000)
            
            safe_print("✅ 分析组件初始化成功")
            
        except Exception as e:
            safe_print(f"❌ 组件初始化失败: {e}")
            
    def analyze_market_indices(self):
        """分析主要市场指数"""
        safe_print("\n📊 主要指数深度分析")
        safe_print("-" * 60)
        
        # 扩展的指数列表
        indices = {
            "上证指数": "000001",
            "深证成指": "399001",
            "创业板指": "399006", 
            "科创50": "000688",
            "中证500": "000905",
            "沪深300": "000300",
            "上证50": "000016",
            "中小板指": "399005"
        }
        
        for name, code in indices.items():
            try:
                # 获取近期数据
                end_date = datetime.now().strftime("%Y%m%d")
                start_date = (datetime.now() - timedelta(days=10)).strftime("%Y%m%d")
                
                data = self.fetcher.fetch_history(code, start_date, end_date)
                
                if not data.empty and len(data) >= 5:
                    # 计算技术指标
                    analysis = self.calculate_technical_indicators(data, name)
                    self.analysis_data["market_indices"][code] = analysis
                    
                    safe_print(f"\n{name} ({code}):")
                    safe_print(f"  当前点位: {analysis['current_price']:.2f}")
                    safe_print(f"  日涨跌幅: {analysis['daily_change']:+.2f}%")
                    safe_print(f"  5日涨跌幅: {analysis['week_change']:+.2f}%")
                    safe_print(f"  成交量变化: {analysis['volume_change']:+.2f}%")
                    safe_print(f"  技术趋势: {analysis['trend']}")
                    safe_print(f"  支撑位: {analysis['support']:.2f}")
                    safe_print(f"  阻力位: {analysis['resistance']:.2f}")
                else:
                    safe_print(f"\n{name}: 数据不足")
                    
            except Exception as e:
                safe_print(f"\n{name}: 分析失败 - {str(e)}")
        
        return True
        
    def calculate_technical_indicators(self, data, name):
        """计算技术指标"""
        if len(data) < 5:
            return None
            
        latest = data.iloc[-1]
        previous = data.iloc[-2]
        week_ago = data.iloc[-5] if len(data) >= 5 else data.iloc[0]
        
        # 基本价格变化
        daily_change = ((latest['close'] - previous['close']) / previous['close']) * 100
        week_change = ((latest['close'] - week_ago['close']) / week_ago['close']) * 100
        
        # 成交量变化
        volume_change = ((latest['volume'] - previous['volume']) / previous['volume']) * 100 if previous['volume'] > 0 else 0
        
        # 计算移动平均线
        data['ma5'] = data['close'].rolling(window=5).mean()
        data['ma10'] = data['close'].rolling(window=min(10, len(data))).mean()
        
        # 支撑阻力位计算
        recent_high = data['high'].tail(5).max()
        recent_low = data['low'].tail(5).min()
        
        # 趋势判断
        if latest['close'] > data['ma5'].iloc[-1] and daily_change > 0:
            trend = "📈 上升趋势"
        elif latest['close'] < data['ma5'].iloc[-1] and daily_change < 0:
            trend = "📉 下降趋势"
        else:
            trend = "➡️ 横盘整理"
            
        return {
            "name": name,
            "current_price": latest['close'],
            "daily_change": daily_change,
            "week_change": week_change,
            "volume_change": volume_change,
            "trend": trend,
            "support": recent_low,
            "resistance": recent_high,
            "ma5": data['ma5'].iloc[-1],
            "ma10": data['ma10'].iloc[-1],
            "volume": latest['volume'],
            "turnover": latest['volume'] * latest['close']
        }
    
    def analyze_sectors(self):
        """分析行业板块"""
        safe_print("\n🏭 行业板块分析")
        safe_print("-" * 60)
        
        # 代表性行业股票
        sectors = {
            "白酒": ["600519", "000858", "600809"],  # 茅台、五粮液、山西汾酒
            "银行": ["000001", "600036", "601318"],  # 平安、招行、工行
            "新能源汽车": ["300750", "002594", "300014"],  # 宁德时代、比亚迪、亿纬锂能
            "医药": ["000002", "600276", "300015"],  # 万科A、恒瑞医药、爱尔眼科
            "科技": ["000063", "002415", "300059"],  # 中兴通讯、海康威视、东方财富
            "房地产": ["000002", "001979", "600048"],  # 万科A、招商蛇口、保利发展
        }
        
        for sector_name, stock_codes in sectors.items():
            try:
                sector_signals = []
                sector_performance = []
                
                safe_print(f"\n🔍 {sector_name}板块:")
                
                for code in stock_codes:
                    try:
                        # 生成交易信号
                        signal_report = self.signal_generator.generate_signal(code)
                        
                        if signal_report:
                            signal = signal_report.signal
                            sector_signals.append({
                                "code": code,
                                "action": signal.action,
                                "confidence": signal.confidence
                            })
                            
                            # 获取价格数据计算表现
                            end_date = datetime.now().strftime("%Y%m%d")
                            start_date = (datetime.now() - timedelta(days=5)).strftime("%Y%m%d")
                            data = self.fetcher.fetch_history(code, start_date, end_date)
                            
                            if not data.empty and len(data) >= 2:
                                change = ((data.iloc[-1]['close'] - data.iloc[0]['close']) / data.iloc[0]['close']) * 100
                                sector_performance.append(change)
                    except:
                        continue
                
                # 板块汇总分析
                if sector_signals:
                    buy_count = sum(1 for s in sector_signals if s["action"] == "BUY")
                    sell_count = sum(1 for s in sector_signals if s["action"] == "SELL")
                    hold_count = len(sector_signals) - buy_count - sell_count
                    avg_confidence = sum(s["confidence"] for s in sector_signals) / len(sector_signals)
                    
                    safe_print(f"  信号分布: 买入{buy_count}个, 持有{hold_count}个, 卖出{sell_count}个")
                    safe_print(f"  平均置信度: {avg_confidence:.2f}")
                    
                    if sector_performance:
                        avg_performance = sum(sector_performance) / len(sector_performance)
                        safe_print(f"  板块表现: {avg_performance:+.2f}%")
                    
                    # 板块评级
                    if buy_count > sell_count and avg_confidence > 0.6:
                        rating = "🟢 看好"
                    elif sell_count > buy_count:
                        rating = "🔴 谨慎"
                    else:
                        rating = "🟡 中性"
                    
                    safe_print(f"  板块评级: {rating}")
                    
                    self.analysis_data["sector_analysis"][sector_name] = {
                        "buy_signals": buy_count,
                        "sell_signals": sell_count,
                        "hold_signals": hold_count,
                        "avg_confidence": avg_confidence,
                        "avg_performance": sum(sector_performance) / len(sector_performance) if sector_performance else 0,
                        "rating": rating
                    }
                    
            except Exception as e:
                safe_print(f"  {sector_name}板块分析失败: {str(e)}")
    
    def analyze_individual_stocks(self):
        """分析重点个股"""
        safe_print("\n🎯 重点个股深度分析")
        safe_print("-" * 60)
        
        # 重点关注股票
        focus_stocks = {
            "贵州茅台": "600519",
            "中国平安": "000001",
            "招商银行": "600036", 
            "宁德时代": "300750",
            "五粮液": "000858",
            "比亚迪": "002594",
            "恒瑞医药": "600276",
            "中兴通讯": "000063",
            "海康威视": "002415",
            "万科A": "000002"
        }
        
        detailed_analysis = []
        
        for name, code in focus_stocks.items():
            try:
                safe_print(f"\n📋 {name} ({code}) 详细分析:")
                
                # 生成交易信号
                signal_report = self.signal_generator.generate_signal(code)
                
                # 获取历史数据
                end_date = datetime.now().strftime("%Y%m%d")
                start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
                data = self.fetcher.fetch_history(code, start_date, end_date)
                
                stock_analysis = {
                    "name": name,
                    "code": code,
                    "signal": None,
                    "technical": None,
                    "recommendation": ""
                }
                
                if signal_report:
                    signal = signal_report.signal
                    action_icon = {"BUY": "📈", "SELL": "📉", "HOLD": "➡️"}.get(signal.action, "❓")
                    
                    safe_print(f"  交易信号: {action_icon} {signal.action}")
                    safe_print(f"  信号置信度: {signal.confidence:.2f}")
                    
                    stock_analysis["signal"] = {
                        "action": signal.action,
                        "confidence": signal.confidence
                    }
                
                if not data.empty and len(data) >= 10:
                    # 技术分析
                    tech_data = self.calculate_technical_indicators(data, name)
                    if tech_data:
                        safe_print(f"  当前价格: ¥{tech_data['current_price']:.2f}")
                        safe_print(f"  日涨跌幅: {tech_data['daily_change']:+.2f}%")
                        safe_print(f"  5日均线: ¥{tech_data['ma5']:.2f}")
                        safe_print(f"  技术趋势: {tech_data['trend']}")
                        safe_print(f"  支撑位: ¥{tech_data['support']:.2f}")
                        safe_print(f"  阻力位: ¥{tech_data['resistance']:.2f}")
                        
                        stock_analysis["technical"] = tech_data
                
                # 生成投资建议
                if signal_report and stock_analysis["technical"]:
                    recommendation = self.generate_stock_recommendation(signal_report.signal, stock_analysis["technical"])
                    safe_print(f"  投资建议: {recommendation}")
                    stock_analysis["recommendation"] = recommendation
                
                detailed_analysis.append(stock_analysis)
                self.analysis_data["individual_stocks"][code] = stock_analysis
                
            except Exception as e:
                safe_print(f"  {name}分析失败: {str(e)}")
        
        return detailed_analysis
    
    def generate_stock_recommendation(self, signal, technical):
        """生成个股投资建议"""
        recommendations = []
        
        # 基于交易信号
        if signal.action == "BUY" and signal.confidence > 0.7:
            recommendations.append("强烈推荐买入")
        elif signal.action == "BUY" and signal.confidence > 0.5:
            recommendations.append("建议分批买入")
        elif signal.action == "SELL" and signal.confidence > 0.7:
            recommendations.append("建议减持")
        elif signal.action == "SELL" and signal.confidence > 0.5:
            recommendations.append("谨慎观望")
        else:
            recommendations.append("维持观望")
        
        # 基于技术面
        if technical["daily_change"] > 3:
            recommendations.append("短期涨幅较大，注意回调风险")
        elif technical["daily_change"] < -3:
            recommendations.append("短期跌幅较大，可关注反弹机会")
        
        # 基于趋势
        if "上升" in technical["trend"]:
            recommendations.append("技术面呈上升态势")
        elif "下降" in technical["trend"]:
            recommendations.append("技术面偏弱")
        
        return "; ".join(recommendations)
    
    def generate_market_sentiment(self):
        """生成市场情绪分析"""
        safe_print("\n🌡️ 市场情绪温度计")
        safe_print("-" * 60)
        
        # 统计各项指标
        indices_up = 0
        indices_total = 0
        
        for code, data in self.analysis_data["market_indices"].items():
            indices_total += 1
            if data["daily_change"] > 0:
                indices_up += 1
        
        # 板块情况
        sector_positive = 0
        sector_total = 0
        
        for sector, data in self.analysis_data["sector_analysis"].items():
            sector_total += 1
            if data["buy_signals"] > data["sell_signals"]:
                sector_positive += 1
        
        # 个股情况  
        stock_buy = 0
        stock_total = 0
        
        for code, data in self.analysis_data["individual_stocks"].items():
            if data["signal"]:
                stock_total += 1
                if data["signal"]["action"] == "BUY":
                    stock_buy += 1
        
        # 计算情绪指数
        index_sentiment = (indices_up / indices_total) if indices_total > 0 else 0.5
        sector_sentiment = (sector_positive / sector_total) if sector_total > 0 else 0.5
        stock_sentiment = (stock_buy / stock_total) if stock_total > 0 else 0.5
        
        overall_sentiment = (index_sentiment + sector_sentiment + stock_sentiment) / 3
        
        safe_print(f"指数情绪: {index_sentiment:.2f} ({indices_up}/{indices_total}个指数上涨)")
        safe_print(f"板块情绪: {sector_sentiment:.2f} ({sector_positive}/{sector_total}个板块偏多)")
        safe_print(f"个股情绪: {stock_sentiment:.2f} ({stock_buy}/{stock_total}个股票买入信号)")
        safe_print(f"综合情绪指数: {overall_sentiment:.2f}")
        
        if overall_sentiment > 0.7:
            sentiment_level = "🔥 市场情绪高涨"
        elif overall_sentiment > 0.5:
            sentiment_level = "😊 市场情绪偏乐观"
        elif overall_sentiment > 0.3:
            sentiment_level = "😐 市场情绪中性"
        else:
            sentiment_level = "😨 市场情绪悲观"
        
        safe_print(f"情绪评级: {sentiment_level}")
        
        self.analysis_data["market_sentiment"] = {
            "index_sentiment": index_sentiment,
            "sector_sentiment": sector_sentiment, 
            "stock_sentiment": stock_sentiment,
            "overall_sentiment": overall_sentiment,
            "sentiment_level": sentiment_level
        }
        
        return overall_sentiment
    
    def generate_investment_strategy(self):
        """生成投资策略建议"""
        safe_print("\n💡 投资策略制定")
        safe_print("-" * 60)
        
        sentiment = self.analysis_data["market_sentiment"]["overall_sentiment"]
        
        # 仓位建议
        if sentiment > 0.7:
            position_advice = "建议仓位: 70-80% (积极型)"
            risk_level = "中高风险"
        elif sentiment > 0.5:
            position_advice = "建议仓位: 50-70% (稳健型)"
            risk_level = "中等风险"
        elif sentiment > 0.3:
            position_advice = "建议仓位: 30-50% (保守型)"
            risk_level = "中低风险"
        else:
            position_advice = "建议仓位: 20-30% (防御型)"
            risk_level = "低风险"
        
        safe_print(f"📊 {position_advice}")
        safe_print(f"⚖️ 风险等级: {risk_level}")
        
        # 推荐股票
        safe_print("\n🎯 重点推荐标的:")
        recommendations = []
        
        for code, data in self.analysis_data["individual_stocks"].items():
            if (data["signal"] and 
                data["signal"]["action"] == "BUY" and 
                data["signal"]["confidence"] > 0.6):
                recommendations.append(f"  • {data['name']} ({code}) - 置信度: {data['signal']['confidence']:.2f}")
        
        if recommendations:
            for rec in recommendations[:5]:  # 最多显示5个
                safe_print(rec)
        else:
            safe_print("  当前暂无强烈推荐标的")
        
        # 风险提示
        safe_print("\n⚠️ 风险管控:")
        safe_print("  • 严格控制单一标的仓位不超过20%")
        safe_print("  • 设置止损线为-8%，止盈线为+15%")
        safe_print("  • 关注市场突发事件和政策变化")
        safe_print("  • 保持适当的现金储备应对波动")
        
        self.analysis_data["recommendations"] = {
            "position_advice": position_advice,
            "risk_level": risk_level,
            "recommended_stocks": recommendations[:5]
        }
    
    def run_comprehensive_analysis(self):
        """运行完整的综合分析"""
        safe_print("="*80)
        safe_print("           MyTrade A股全面深度分析系统")
        safe_print("="*80)
        
        today = datetime.now()
        safe_print(f"\n📅 分析日期: {today.strftime('%Y年%m月%d日')}")
        safe_print(f"🕐 分析时间: {today.strftime('%H:%M:%S')}")
        safe_print(f"📊 分析版本: MyTrade v1.0")
        
        try:
            # 执行各项分析
            safe_print("\n🚀 开始全面市场分析...")
            
            self.analyze_market_indices()
            self.analyze_sectors() 
            self.analyze_individual_stocks()
            sentiment = self.generate_market_sentiment()
            self.generate_investment_strategy()
            
            safe_print("\n" + "="*80)
            safe_print("📈 分析完成概况")
            safe_print("="*80)
            
            safe_print(f"✅ 指数分析: {len(self.analysis_data['market_indices'])} 个")
            safe_print(f"✅ 板块分析: {len(self.analysis_data['sector_analysis'])} 个") 
            safe_print(f"✅ 个股分析: {len(self.analysis_data['individual_stocks'])} 只")
            safe_print(f"📊 市场情绪指数: {sentiment:.2f}")
            
            return True
            
        except Exception as e:
            safe_print(f"\n❌ 分析过程发生错误: {e}")
            traceback.print_exc()
            return False

def main():
    """主函数"""
    analyzer = ComprehensiveMarketAnalyzer()
    
    # 运行分析
    success = analyzer.run_comprehensive_analysis()
    
    if success:
        # 生成详细报告
        safe_print("\n📄 正在生成详细分析报告...")
        
        try:
            generate_detailed_report(analyzer.analysis_data)
            safe_print("✅ 详细报告已生成: test/A股深度分析报告.md")
        except Exception as e:
            safe_print(f"❌ 报告生成失败: {e}")
        
        return True
    else:
        safe_print("\n❌ 分析失败，请检查系统配置")
        return False

def generate_detailed_report(analysis_data):
    """生成详细的Markdown报告"""
    
    report_content = f"""# A股市场深度分析报告

**生成时间**: {analysis_data['timestamp'].strftime('%Y年%m月%d日 %H:%M:%S')}  
**分析系统**: MyTrade量化交易系统 v1.0  
**报告类型**: 全市场综合分析  

---

## 📊 执行摘要

本报告基于MyTrade量化交易系统的全面分析，涵盖了主要市场指数、行业板块、重点个股的深度解析。通过技术分析、基本面研究和量化信号生成，为投资者提供全方位的市场洞察和投资建议。

**核心发现**:
- 市场情绪指数: {analysis_data.get('market_sentiment', {}).get('overall_sentiment', 0):.2f}
- 情绪水平: {analysis_data.get('market_sentiment', {}).get('sentiment_level', '数据缺失')}
- 分析覆盖: {len(analysis_data.get('market_indices', {}))}个指数, {len(analysis_data.get('sector_analysis', {}))}个板块, {len(analysis_data.get('individual_stocks', {}))}只个股

---

## 📈 市场指数分析

### 主要指数表现

"""
    
    # 指数分析部分
    if analysis_data.get('market_indices'):
        for code, data in analysis_data['market_indices'].items():
            report_content += f"""
#### {data['name']} ({code})

- **当前点位**: {data['current_price']:.2f}
- **日涨跌幅**: {data['daily_change']:+.2f}%
- **5日涨跌幅**: {data['week_change']:+.2f}%
- **技术趋势**: {data['trend']}
- **5日均线**: {data['ma5']:.2f}
- **支撑位**: {data['support']:.2f}
- **阻力位**: {data['resistance']:.2f}
- **成交量变化**: {data['volume_change']:+.2f}%

"""
    
    # 板块分析部分
    report_content += """
---

## 🏭 行业板块分析

### 板块轮动与热点分析

"""
    
    if analysis_data.get('sector_analysis'):
        for sector, data in analysis_data['sector_analysis'].items():
            report_content += f"""
#### {sector}板块

- **板块评级**: {data['rating']}
- **信号分布**: 买入{data['buy_signals']}个, 持有{data['hold_signals']}个, 卖出{data['sell_signals']}个
- **平均置信度**: {data['avg_confidence']:.2f}
- **板块表现**: {data['avg_performance']:+.2f}%

**投资建议**: {"该板块当前呈现积极信号，建议重点关注" if data['buy_signals'] > data['sell_signals'] else "该板块信号偏弱，建议谨慎观望" if data['sell_signals'] > data['buy_signals'] else "该板块表现中性，建议保持现有配置"}

"""
    
    # 个股分析部分
    report_content += """
---

## 🎯 重点个股深度剖析

### 核心标的投资价值分析

"""
    
    if analysis_data.get('individual_stocks'):
        for code, data in analysis_data['individual_stocks'].items():
            if data['signal'] and data['technical']:
                report_content += f"""
#### {data['name']} ({code})

**交易信号分析**:
- 信号类型: {data['signal']['action']}
- 信号置信度: {data['signal']['confidence']:.2f}

**技术面分析**:
- 当前价格: ¥{data['technical']['current_price']:.2f}
- 日涨跌幅: {data['technical']['daily_change']:+.2f}%
- 技术趋势: {data['technical']['trend']}
- 5日均线: ¥{data['technical']['ma5']:.2f}
- 支撑位: ¥{data['technical']['support']:.2f}
- 阻力位: ¥{data['technical']['resistance']:.2f}

**投资建议**: {data['recommendation']}

**风险提示**: {'该股票获得买入信号，但仍需关注市场整体走势和个股基本面变化' if data['signal']['action'] == 'BUY' else '该股票信号偏弱，建议控制仓位或观望' if data['signal']['action'] == 'SELL' else '该股票信号中性，建议根据个人风险偏好决策'}

"""
    
    # 市场情绪分析
    report_content += """
---

## 🌡️ 市场情绪与资金流向

### 综合情绪指数分析

"""
    
    if analysis_data.get('market_sentiment'):
        sentiment = analysis_data['market_sentiment']
        report_content += f"""
**市场情绪构成**:
- 指数情绪: {sentiment['index_sentiment']:.2f}
- 板块情绪: {sentiment['sector_sentiment']:.2f}  
- 个股情绪: {sentiment['stock_sentiment']:.2f}
- **综合情绪指数**: {sentiment['overall_sentiment']:.2f}

**情绪解读**: {sentiment['sentiment_level']}

**市场特征分析**:
"""
        
        if sentiment['overall_sentiment'] > 0.7:
            report_content += """
- 市场呈现明显的风险偏好上升态势
- 投资者情绪相对乐观，追涨意愿较强
- 建议适当提高权益资产配置比例
- 关注题材股和成长股的投资机会
"""
        elif sentiment['overall_sentiment'] > 0.5:
            report_content += """
- 市场情绪保持相对平衡状态
- 投资者对后市走势存在一定分歧
- 建议保持均衡配置策略
- 重点关注业绩确定性较强的标的
"""
        elif sentiment['overall_sentiment'] > 0.3:
            report_content += """
- 市场情绪偏向谨慎，观望情绪较浓
- 投资者风险偏好有所下降
- 建议适当降低仓位，关注防御性品种
- 等待更明确的方向性信号
"""
        else:
            report_content += """
- 市场情绪明显悲观，恐慌情绪蔓延
- 建议采取防御性策略，控制风险
- 关注高股息、低估值的价值股
- 保持充足现金储备等待机会
"""
    
    # 投资策略建议
    report_content += """
---

## 💡 投资策略与配置建议

### 基于量化分析的投资策略

"""
    
    if analysis_data.get('recommendations'):
        rec = analysis_data['recommendations']
        report_content += f"""
**仓位配置建议**:
{rec['position_advice']}

**风险等级评估**:
{rec['risk_level']}

**重点推荐标的**:
"""
        
        if rec['recommended_stocks']:
            for stock in rec['recommended_stocks']:
                report_content += f"{stock}\n"
        else:
            report_content += "当前市场环境下暂无强烈推荐标的，建议保持观望\n"
    
    # 风险管控与操作纪律
    report_content += """
### 风险管控与操作纪律

**仓位管控**:
- 严格控制单一标的仓位不超过总资产的20%
- 同一行业配置比例不超过总资产的30%  
- 保持10-20%的现金储备以应对突发情况

**止损止盈策略**:
- 个股止损线设置在-8%，严格执行
- 盈利标的止盈线设置在+15%，分批减持
- 根据市场环境动态调整止损止盈比例

**操作节奏**:
- 分批建仓，避免一次性重仓
- 开盘后观察30分钟再进行交易决策
- 避免尾盘最后30分钟的冲动交易
- 重要时间窗口前减仓观望

---

## 📋 数据说明与免责声明

### 数据来源与处理方法

**数据来源**:
- 市场行情数据来源于AkShare数据接口
- 技术指标基于标准算法计算生成
- 交易信号由MyTrade量化系统生成

**分析方法**:
- 技术分析: 移动平均线、支撑阻力位、趋势判断
- 情绪分析: 基于多维度指标综合评估
- 量化信号: 机器学习算法生成交易建议

**数据局限性**:
- 历史数据分析不能完全预测未来走势
- 量化模型可能在极端市场条件下失效
- 建议结合基本面分析进行综合判断

### 免责声明

**重要提示**:
1. 本报告仅供投资参考，不构成具体投资建议
2. 投资者应根据自身风险承受能力进行决策
3. 股市投资存在风险，入市需谨慎
4. 历史业绩不代表未来表现
5. 建议在专业投资顾问指导下进行投资

**风险警示**:
- 市场存在系统性风险，可能导致重大损失
- 个股投资存在特定风险，需要分散配置
- 宏观经济和政策变化可能影响市场走势
- 投资者应建立正确的投资理念和风险意识

---

**报告生成**: MyTrade量化交易系统  
**技术支持**: Claude Code Assistant  
**更新频率**: 根据市场情况动态更新  

---

*本报告版权归MyTrade系统所有，仅供内部投资参考使用*
"""
    
    # 保存报告
    report_file = Path(__file__).parent / "A股深度分析报告.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_content)

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)