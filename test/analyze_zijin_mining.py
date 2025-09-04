#!/usr/bin/env python3
"""
紫金矿业(601899)详细分析系统

收集真实数据，全面分析紫金矿业股票
"""

import sys
import os
import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import warnings
import requests

# 添加src到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# 导入编码修复工具
from test_encoding_fix import safe_print

warnings.filterwarnings('ignore')


class ZijinMiningAnalyzer:
    """紫金矿业详细分析器"""
    
    def __init__(self):
        self.symbol = '601899'  # 紫金矿业股票代码
        self.name = '紫金矿业'
        self.analysis_date = datetime.now()
        
        # 创建输出目录
        self.output_dir = Path(__file__).parent
        self.output_dir.mkdir(exist_ok=True)
        
        safe_print(f"📊 紫金矿业({self.symbol})详细分析系统启动")
        safe_print(f"🕒 分析时间: {self.analysis_date.strftime('%Y年%m月%d日 %H:%M:%S')}")
        safe_print("")
        
        # 初始化数据源
        self.init_data_sources()
    
    def init_data_sources(self):
        """初始化数据源"""
        safe_print("🔍 初始化数据源...")
        
        try:
            import akshare as ak
            self.ak = ak
            safe_print("  ✅ akshare - 数据获取库")
        except ImportError:
            safe_print("  ❌ akshare 未安装")
            return False
        
        try:
            import requests
            self.requests = requests
            safe_print("  ✅ requests - API请求库")
        except ImportError:
            safe_print("  ❌ requests 未安装")
            return False
        
        safe_print("")
        return True
    
    def get_realtime_data(self):
        """获取实时行情数据"""
        safe_print("📈 获取紫金矿业实时行情数据...")
        
        try:
            # 获取实时行情
            stock_spot = self.ak.stock_zh_a_spot_em()
            stock_info = stock_spot[stock_spot['代码'] == self.symbol]
            
            if not stock_info.empty:
                row = stock_info.iloc[0]
                
                realtime_data = {
                    'symbol': self.symbol,
                    'name': str(row.get('名称', self.name)),
                    'current_price': float(row.get('最新价', 0)),
                    'change': float(row.get('涨跌额', 0)),
                    'change_pct': float(row.get('涨跌幅', 0)),
                    'open': float(row.get('今开', 0)),
                    'high': float(row.get('最高', 0)),
                    'low': float(row.get('最低', 0)),
                    'prev_close': float(row.get('昨收', 0)),
                    'volume': int(row.get('成交量', 0)),
                    'turnover': float(row.get('成交额', 0)),
                    'market_cap': float(row.get('总市值', 0)) if row.get('总市值') else 0,
                    'pe_ratio': float(row.get('市盈率-动态', 0)) if row.get('市盈率-动态') else 0,
                    'pb_ratio': float(row.get('市净率', 0)) if row.get('市净率') else 0,
                    'turnover_rate': float(row.get('换手率', 0)) if row.get('换手率') else 0,
                }
                
                safe_print(f"  ✅ {realtime_data['name']}: {realtime_data['current_price']:.2f}元")
                safe_print(f"      涨跌幅: {realtime_data['change_pct']:+.2f}% ({realtime_data['change']:+.2f}元)")
                safe_print(f"      成交量: {realtime_data['volume']:,}股")
                safe_print(f"      成交额: {realtime_data['turnover']/100000000:.2f}亿元")
                safe_print(f"      市值: {realtime_data['market_cap']/100000000:.0f}亿元")
                safe_print(f"      PE: {realtime_data['pe_ratio']:.2f}倍 PB: {realtime_data['pb_ratio']:.2f}倍")
                
                return realtime_data
            else:
                safe_print(f"  ❌ 未找到{self.symbol}的行情数据")
                return {}
                
        except Exception as e:
            safe_print(f"❌ 获取实时数据失败: {e}")
            return {}
    
    def get_historical_data(self, days=120):
        """获取历史行情数据"""
        safe_print(f"📊 获取紫金矿业近{days}天历史数据...")
        
        try:
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
            
            # 获取历史数据
            hist_data = self.ak.stock_zh_a_hist(
                symbol=self.symbol, 
                start_date=start_date, 
                end_date=end_date, 
                adjust="qfq"
            )
            
            if not hist_data.empty:
                safe_print(f"  ✅ 获取{len(hist_data)}天历史数据")
                
                # 计算技术指标
                closes = hist_data['收盘'].values
                volumes = hist_data['成交量'].values
                
                technical_indicators = {
                    'ma5': float(np.mean(closes[-5:])) if len(closes) >= 5 else 0,
                    'ma10': float(np.mean(closes[-10:])) if len(closes) >= 10 else 0,
                    'ma20': float(np.mean(closes[-20:])) if len(closes) >= 20 else 0,
                    'ma60': float(np.mean(closes[-60:])) if len(closes) >= 60 else 0,
                    'volatility': float(np.std(closes[-20:])) if len(closes) >= 20 else 0,
                    'highest_20d': float(np.max(closes[-20:])) if len(closes) >= 20 else 0,
                    'lowest_20d': float(np.min(closes[-20:])) if len(closes) >= 20 else 0,
                    'highest_60d': float(np.max(closes[-60:])) if len(closes) >= 60 else 0,
                    'lowest_60d': float(np.min(closes[-60:])) if len(closes) >= 60 else 0,
                    'avg_volume_20d': float(np.mean(volumes[-20:])) if len(volumes) >= 20 else 0,
                }
                
                safe_print(f"      MA5: {technical_indicators['ma5']:.2f}元")
                safe_print(f"      MA20: {technical_indicators['ma20']:.2f}元") 
                safe_print(f"      MA60: {technical_indicators['ma60']:.2f}元")
                safe_print(f"      60日最高/最低: {technical_indicators['highest_60d']:.2f} / {technical_indicators['lowest_60d']:.2f}元")
                
                return hist_data, technical_indicators
            else:
                safe_print("  ❌ 未获取到历史数据")
                return pd.DataFrame(), {}
                
        except Exception as e:
            safe_print(f"❌ 获取历史数据失败: {e}")
            return pd.DataFrame(), {}
    
    def get_financial_data(self):
        """获取财务数据"""
        safe_print("💰 获取紫金矿业财务数据...")
        
        financial_data = {}
        
        try:
            # 获取财务指标
            fin_indicator = self.ak.stock_financial_em(stock=self.symbol)
            if not fin_indicator.empty:
                latest_data = fin_indicator.iloc[0]  # 最新一期数据
                
                financial_data['basic_indicators'] = {
                    'revenue': float(latest_data.get('营业总收入', 0)) if latest_data.get('营业总收入') else 0,
                    'net_profit': float(latest_data.get('净利润', 0)) if latest_data.get('净利润') else 0,
                    'total_assets': float(latest_data.get('总资产', 0)) if latest_data.get('总资产') else 0,
                    'net_assets': float(latest_data.get('净资产', 0)) if latest_data.get('净资产') else 0,
                    'roe': float(latest_data.get('净资产收益率', 0)) if latest_data.get('净资产收益率') else 0,
                    'roa': float(latest_data.get('总资产收益率', 0)) if latest_data.get('总资产收益率') else 0,
                    'gross_margin': float(latest_data.get('销售毛利率', 0)) if latest_data.get('销售毛利率') else 0,
                    'debt_ratio': float(latest_data.get('资产负债率', 0)) if latest_data.get('资产负债率') else 0,
                }
                
                safe_print(f"  ✅ 营业收入: {financial_data['basic_indicators']['revenue']/100000000:.1f}亿元")
                safe_print(f"      净利润: {financial_data['basic_indicators']['net_profit']/100000000:.1f}亿元")
                safe_print(f"      ROE: {financial_data['basic_indicators']['roe']:.2f}%")
                safe_print(f"      负债率: {financial_data['basic_indicators']['debt_ratio']:.2f}%")
                
        except Exception as e:
            safe_print(f"  ⚠️ 获取财务指标失败: {e}")
        
        try:
            # 获取业绩预告
            performance_forecast = self.ak.stock_yjyg_em(symbol=self.symbol)
            if not performance_forecast.empty:
                financial_data['forecast'] = performance_forecast.to_dict('records')
                safe_print(f"  ✅ 获取{len(financial_data['forecast'])}条业绩预告")
        except Exception as e:
            safe_print(f"  ⚠️ 获取业绩预告失败: {e}")
        
        return financial_data
    
    def get_industry_data(self):
        """获取行业对比数据"""
        safe_print("🏭 获取有色金属行业对比数据...")
        
        try:
            # 获取有色金属板块数据
            industry_data = self.ak.stock_board_industry_name_em()
            colored_metal_data = industry_data[industry_data['板块名称'].str.contains('有色金属|金属')]
            
            if not colored_metal_data.empty:
                industry_info = {
                    'industry_name': '有色金属',
                    'industry_change_pct': float(colored_metal_data.iloc[0].get('涨跌幅', 0)),
                    'industry_up_count': int(colored_metal_data.iloc[0].get('上涨家数', 0)),
                    'industry_down_count': int(colored_metal_data.iloc[0].get('下跌家数', 0)),
                    'industry_total_count': int(colored_metal_data.iloc[0].get('公司家数', 0)),
                    'industry_turnover': float(colored_metal_data.iloc[0].get('成交额', 0)),
                    'leading_stock': str(colored_metal_data.iloc[0].get('领涨股票', '')),
                }
                
                safe_print(f"  ✅ {industry_info['industry_name']}板块:")
                safe_print(f"      板块涨跌幅: {industry_info['industry_change_pct']:+.2f}%")
                safe_print(f"      上涨/下跌: {industry_info['industry_up_count']}/{industry_info['industry_down_count']}只")
                safe_print(f"      领涨股: {industry_info['leading_stock']}")
                
                return industry_info
            else:
                safe_print("  ⚠️ 未找到有色金属板块数据")
                return {}
                
        except Exception as e:
            safe_print(f"❌ 获取行业数据失败: {e}")
            return {}
    
    def get_news_sentiment(self):
        """获取新闻和市场情绪"""
        safe_print("📰 获取紫金矿业相关新闻...")
        
        news_data = []
        
        try:
            # 获取个股新闻
            news = self.ak.stock_news_em(symbol=self.symbol)
            if not news.empty:
                # 取最新的5条新闻
                recent_news = news.head(5)
                for _, row in recent_news.iterrows():
                    news_item = {
                        'title': str(row.get('新闻标题', '')),
                        'content': str(row.get('新闻内容', ''))[:200] + '...',  # 截取前200字符
                        'publish_time': str(row.get('发布时间', '')),
                        'source': str(row.get('新闻来源', ''))
                    }
                    news_data.append(news_item)
                
                safe_print(f"  ✅ 获取{len(news_data)}条相关新闻")
                for i, news_item in enumerate(news_data[:3], 1):  # 显示前3条标题
                    safe_print(f"      {i}. {news_item['title'][:50]}...")
                    
        except Exception as e:
            safe_print(f"  ⚠️ 获取新闻失败: {e}")
        
        return news_data
    
    def analyze_technical_signals(self, current_price, technical_indicators):
        """分析技术信号"""
        safe_print("🔍 分析技术信号...")
        
        signals = []
        
        try:
            ma5 = technical_indicators.get('ma5', 0)
            ma20 = technical_indicators.get('ma20', 0)
            ma60 = technical_indicators.get('ma60', 0)
            highest_20d = technical_indicators.get('highest_20d', 0)
            lowest_20d = technical_indicators.get('lowest_20d', 0)
            
            # 均线分析
            if current_price > ma5 > ma20:
                signals.append("✅ 短期多头排列：股价站上5日线和20日线")
            elif current_price < ma5 < ma20:
                signals.append("❌ 短期空头排列：股价跌破5日线和20日线")
            elif current_price > ma20:
                signals.append("🟡 股价站上20日均线，短期偏强")
            else:
                signals.append("🔴 股价跌破20日均线，短期偏弱")
            
            # 位置分析
            price_position = (current_price - lowest_20d) / (highest_20d - lowest_20d) * 100 if highest_20d > lowest_20d else 50
            if price_position > 80:
                signals.append(f"⚠️ 价格位于20日高位区间({price_position:.1f}%)，注意回调风险")
            elif price_position < 20:
                signals.append(f"💪 价格位于20日低位区间({price_position:.1f}%)，具备反弹基础")
            else:
                signals.append(f"➡️ 价格位于20日中位区间({price_position:.1f}%)")
            
            # 趋势分析
            if ma5 > ma20 > ma60:
                signals.append("📈 中长期趋势向上：5日线>20日线>60日线")
            elif ma5 < ma20 < ma60:
                signals.append("📉 中长期趋势向下：5日线<20日线<60日线")
            else:
                signals.append("➡️ 中长期趋势不明确，处于震荡状态")
            
            safe_print("  ✅ 技术信号分析完成")
            for signal in signals:
                safe_print(f"      {signal}")
                
        except Exception as e:
            safe_print(f"❌ 技术分析失败: {e}")
        
        return signals
    
    def generate_comprehensive_analysis(self):
        """生成综合分析报告"""
        safe_print("=" * 80)
        safe_print("                 紫金矿业(601899)详细分析")
        safe_print("=" * 80)
        safe_print("")
        
        # 收集所有数据
        realtime_data = self.get_realtime_data()
        hist_data, technical_indicators = self.get_historical_data()
        financial_data = self.get_financial_data()
        industry_data = self.get_industry_data()
        news_data = self.get_news_sentiment()
        
        # 技术分析
        technical_signals = []
        if realtime_data and technical_indicators:
            technical_signals = self.analyze_technical_signals(
                realtime_data['current_price'], 
                technical_indicators
            )
        
        # 生成分析报告
        report_content = self.create_analysis_report(
            realtime_data, technical_indicators, financial_data, 
            industry_data, news_data, technical_signals
        )
        
        # 保存报告
        report_file = self.output_dir / 'zijin_mining_analysis.md'
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        # 保存数据
        analysis_data = {
            'analysis_time': self.analysis_date.isoformat(),
            'symbol': self.symbol,
            'name': self.name,
            'realtime_data': realtime_data,
            'technical_indicators': technical_indicators,
            'financial_data': financial_data,
            'industry_data': industry_data,
            'news_data': news_data,
            'technical_signals': technical_signals
        }
        
        json_file = self.output_dir / 'zijin_mining_data.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, ensure_ascii=False, indent=2, default=str)
        
        safe_print("")
        safe_print("✅ 紫金矿业详细分析完成！")
        safe_print(f"📄 分析报告: {report_file}")
        safe_print(f"📊 分析数据: {json_file}")
        
        return analysis_data
    
    def create_analysis_report(self, realtime, technical, financial, industry, news, signals):
        """创建分析报告"""
        current_time = self.analysis_date
        
        report = f"""# 紫金矿业(601899)详细分析报告

**分析时间**: {current_time.strftime('%Y年%m月%d日 %H:%M:%S')}  
**股票代码**: 601899  
**股票名称**: 紫金矿业  
**所属行业**: 有色金属 - 黄金开采  
**分析师**: MyTrade智能分析系统  

> 📊 **重要提示**: 本报告基于公开市场数据进行综合分析，仅供投资参考，不构成投资建议

---

## 📊 实时行情概览

"""
        
        if realtime:
            trend_icon = "📈" if realtime['change_pct'] > 0 else "📉" if realtime['change_pct'] < 0 else "➡️"
            report += f"""### 基本行情信息

- **最新价格**: **{realtime['current_price']:.2f}元**
- **涨跌幅**: {trend_icon} **{realtime['change_pct']:+.2f}%** ({realtime['change']:+.2f}元)
- **今日开盘**: {realtime['open']:.2f}元
- **最高价/最低价**: {realtime['high']:.2f}元 / {realtime['low']:.2f}元
- **昨日收盘**: {realtime['prev_close']:.2f}元

### 交易活跃度

- **成交量**: {realtime['volume']:,}股
- **成交额**: {realtime['turnover']/100000000:.2f}亿元
- **换手率**: {realtime['turnover_rate']:.2f}%

### 估值指标

- **总市值**: {realtime['market_cap']/100000000:.0f}亿元
- **市盈率(PE)**: {realtime['pe_ratio']:.2f}倍
- **市净率(PB)**: {realtime['pb_ratio']:.2f}倍

"""
        
        # 技术分析
        if technical:
            report += f"""---

## 🔍 技术分析

### 均线系统

- **5日均线**: {technical['ma5']:.2f}元
- **10日均线**: {technical['ma10']:.2f}元
- **20日均线**: {technical['ma20']:.2f}元
- **60日均线**: {technical['ma60']:.2f}元

### 价格区间

- **20日最高**: {technical['highest_20d']:.2f}元
- **20日最低**: {technical['lowest_20d']:.2f}元
- **60日最高**: {technical['highest_60d']:.2f}元
- **60日最低**: {technical['lowest_60d']:.2f}元
- **20日波动率**: {technical['volatility']:.2f}

### 技术信号

"""
            for signal in signals:
                report += f"- {signal}\n"
        
        # 财务分析
        if financial and financial.get('basic_indicators'):
            basic = financial['basic_indicators']
            report += f"""
---

## 💰 基本面分析

### 财务概况

- **营业收入**: {basic['revenue']/100000000:.1f}亿元
- **净利润**: {basic['net_profit']/100000000:.1f}亿元
- **总资产**: {basic['total_assets']/100000000:.0f}亿元
- **净资产**: {basic['net_assets']/100000000:.0f}亿元

### 盈利能力

- **净资产收益率(ROE)**: {basic['roe']:.2f}%
- **总资产收益率(ROA)**: {basic['roa']:.2f}%
- **销售毛利率**: {basic['gross_margin']:.2f}%

### 财务结构

- **资产负债率**: {basic['debt_ratio']:.2f}%

### 财务质量评价

"""
            
            # 财务质量评价
            if basic['roe'] > 15:
                report += "- ✅ **ROE表现优秀**: 净资产收益率超过15%，盈利能力强\n"
            elif basic['roe'] > 10:
                report += "- 🟡 **ROE表现良好**: 净资产收益率在10-15%之间\n"
            else:
                report += "- ⚠️ **ROE偏低**: 净资产收益率低于10%，需关注盈利能力\n"
            
            if basic['debt_ratio'] < 60:
                report += "- ✅ **负债率健康**: 资产负债率低于60%，财务结构稳健\n"
            elif basic['debt_ratio'] < 80:
                report += "- 🟡 **负债率适中**: 资产负债率在60-80%之间\n"
            else:
                report += "- ⚠️ **负债率偏高**: 资产负债率超过80%，需注意财务风险\n"
        
        # 行业对比
        if industry:
            report += f"""
---

## 🏭 行业对比分析

### {industry['industry_name']}板块表现

- **板块涨跌幅**: {industry['industry_change_pct']:+.2f}%
- **上涨股票**: {industry['industry_up_count']}只
- **下跌股票**: {industry['industry_down_count']}只
- **板块总数**: {industry['industry_total_count']}只
- **成交额**: {industry['industry_turnover']/100000000:.1f}亿元
- **板块领涨股**: {industry['leading_stock']}

### 行业地位分析

紫金矿业作为中国最大的黄金企业之一，在有色金属行业具有重要地位：

1. **规模优势**: 拥有完整的产业链，从勘探、开采到冶炼加工
2. **资源储量**: 黄金储量和产量均位居国内前列
3. **国际化程度**: 海外项目众多，具备全球化运营能力
4. **技术实力**: 在低品位矿石处理方面技术领先

"""
        
        # 新闻分析
        if news:
            report += f"""---

## 📰 最新资讯与市场情绪

### 近期重要新闻 (最新{len(news)}条)

"""
            for i, news_item in enumerate(news, 1):
                report += f"""**{i}. {news_item['title']}**
- 来源: {news_item['source']}
- 时间: {news_item['publish_time']}
- 摘要: {news_item['content']}

"""
        
        # 投资分析
        report += f"""---

## 🎯 投资分析与建议

### 投资亮点

1. **行业龙头地位**: 紫金矿业是中国黄金行业的龙头企业
2. **资源优势**: 拥有丰富的黄金、铜等有色金属资源
3. **成本控制**: 采用堆浸等先进技术，生产成本相对较低
4. **国际化布局**: 海外项目为公司提供增长动力

### 风险提示

1. **商品价格波动**: 黄金、铜等大宗商品价格波动直接影响业绩
2. **环保政策**: 矿业开采面临日益严格的环保要求
3. **地缘政治风险**: 海外项目可能面临政治和政策风险
4. **汇率风险**: 海外业务收入受汇率波动影响

### 技术面建议

"""
        
        # 技术面建议
        if realtime and technical:
            current_price = realtime['current_price']
            ma20 = technical.get('ma20', 0)
            
            if current_price > ma20:
                report += """- **短期策略**: 股价站上20日均线，可关注回踩确认的买入机会
- **支撑位**: 关注20日均线和前期重要低点支撑
- **压力位**: 关注前期高点和整数关口压力"""
            else:
                report += """- **短期策略**: 股价在20日均线下方，建议等待企稳信号
- **观察点**: 关注能否重新站上20日均线
- **风险控制**: 严格设置止损位，控制下跌风险"""
        
        # 评级建议
        report += f"""

### 综合评级

基于当前分析，给出以下评级：

"""
        
        # 简单的评级逻辑
        score = 0
        if realtime:
            if realtime['change_pct'] > 0:
                score += 1
            if realtime.get('pe_ratio', 0) < 20 and realtime.get('pe_ratio', 0) > 0:
                score += 1
        
        if technical:
            if technical.get('ma5', 0) > technical.get('ma20', 0):
                score += 1
        
        if financial and financial.get('basic_indicators', {}).get('roe', 0) > 10:
            score += 1
        
        if score >= 3:
            rating = "买入"
            rating_icon = "🟢"
        elif score >= 2:
            rating = "持有"
            rating_icon = "🟡"
        else:
            rating = "观望"
            rating_icon = "🔴"
        
        report += f"""**投资评级**: {rating_icon} **{rating}**

**目标价位**: 基于技术分析和基本面分析，建议关注{technical.get('ma20', realtime.get('current_price', 0)) * 1.1:.2f}元附近阻力位

---

## ⚠️ 重要声明

本分析报告基于公开信息和历史数据，采用多种分析方法得出结论，但不构成投资建议。

**风险提示**:
- 股市有风险，投资需谨慎
- 过往业绩不代表未来表现
- 请根据自身风险承受能力做出投资决策
- 建议分散投资，控制仓位

**数据来源**: akshare、东方财富等公开数据源
**分析时间**: {current_time.strftime('%Y-%m-%d %H:%M:%S')}
**报告生成**: MyTrade智能分析系统

---

*本报告仅供参考，投资者应结合自身情况独立判断*
"""
        
        return report


def main():
    """主函数"""
    analyzer = ZijinMiningAnalyzer()
    
    try:
        result = analyzer.generate_comprehensive_analysis()
        
        safe_print("")
        safe_print("=" * 80)
        safe_print("             紫金矿业分析完成")
        safe_print("=" * 80)
        safe_print("")
        
        if result.get('realtime_data'):
            rd = result['realtime_data']
            safe_print("📊 关键数据:")
            safe_print(f"   • 最新价格: {rd['current_price']:.2f}元 ({rd['change_pct']:+.2f}%)")
            safe_print(f"   • 市值: {rd['market_cap']/100000000:.0f}亿元")
            safe_print(f"   • PE/PB: {rd['pe_ratio']:.2f}/{rd['pb_ratio']:.2f}")
        
        safe_print("")
        safe_print("📄 分析报告已生成: test/zijin_mining_analysis.md")
        safe_print("📊 数据文件已保存: test/zijin_mining_data.json")
        
        return True
        
    except Exception as e:
        safe_print(f"❌ 分析失败: {e}")
        import traceback
        safe_print(traceback.format_exc())
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)