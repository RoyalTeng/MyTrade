#!/usr/bin/env python3
"""
A股今日行情分析

使用MyTrade系统分析A股今日行情，生成投资建议。
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd

# 添加src到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, str(Path(__file__).parent / "test"))

# 导入编码修复工具
from test_encoding_fix import safe_print

# 导入MyTrade核心模块
from mytrade.config import get_config_manager
from mytrade.data.market_data_fetcher import MarketDataFetcher, DataSourceConfig
from mytrade.trading import SignalGenerator
from mytrade.logging import InterpretableLogger

def get_market_overview():
    """获取市场概况"""
    safe_print("="*80)
    safe_print("           MyTrade A股今日行情分析")
    safe_print("="*80)
    
    today = datetime.now()
    safe_print(f"\n📅 分析日期: {today.strftime('%Y年%m月%d日')}")
    safe_print(f"🕐 分析时间: {today.strftime('%H:%M:%S')}")

def analyze_major_indices():
    """分析主要指数"""
    safe_print("\n" + "-"*60)
    safe_print("📊 主要指数分析")
    safe_print("-"*60)
    
    try:
        # 配置数据源
        config = DataSourceConfig(
            source="akshare",
            cache_dir=Path("data/cache")
        )
        fetcher = MarketDataFetcher(config)
        
        # 主要指数代码
        major_indices = {
            "上证指数": "000001",
            "深证成指": "399001", 
            "创业板指": "399006",
            "沪深300": "000300"
        }
        
        safe_print("\n正在获取指数数据...")
        
        for name, code in major_indices.items():
            try:
                # 获取最近3天数据用于分析趋势
                end_date = datetime.now().strftime("%Y%m%d")
                start_date = (datetime.now() - timedelta(days=3)).strftime("%Y%m%d")
                
                data = fetcher.fetch_history(code, start_date, end_date)
                
                if not data.empty and len(data) >= 2:
                    latest = data.iloc[-1]
                    previous = data.iloc[-2]
                    
                    price_change = latest['close'] - previous['close'] 
                    change_percent = (price_change / previous['close']) * 100
                    
                    # 判断趋势
                    trend = "📈" if change_percent > 0 else "📉" if change_percent < 0 else "➡️"
                    
                    safe_print(f"\n{name} ({code}):")
                    safe_print(f"  当前点位: {latest['close']:.2f}")
                    safe_print(f"  涨跌幅: {trend} {change_percent:+.2f}%")
                    safe_print(f"  成交量: {latest['volume']:,.0f}")
                    safe_print(f"  成交额: {latest['volume'] * latest['close'] / 10000:.0f}万")
                else:
                    safe_print(f"\n{name}: 数据不足")
                    
            except Exception as e:
                safe_print(f"\n{name}: 获取数据失败 - {str(e)}")
        
        return True
        
    except Exception as e:
        safe_print(f"指数分析失败: {e}")
        return False

def analyze_hot_stocks():
    """分析热门股票"""
    safe_print("\n" + "-"*60)
    safe_print("🔥 热门股票分析")
    safe_print("-"*60)
    
    try:
        # 初始化信号生成器
        config_manager = get_config_manager("config.yaml")
        config = config_manager.get_config()
        generator = SignalGenerator(config)
        
        # 分析一些热门股票
        hot_stocks = {
            "贵州茅台": "600519",
            "中国平安": "000001", 
            "招商银行": "600036",
            "五粮液": "000858",
            "宁德时代": "300750"
        }
        
        safe_print(f"\n正在分析 {len(hot_stocks)} 只热门股票...")
        
        analysis_results = []
        
        for name, code in hot_stocks.items():
            try:
                safe_print(f"\n🔍 分析 {name} ({code})...")
                
                # 生成交易信号
                signal_report = generator.generate_signal(code)
                
                if signal_report:
                    signal = signal_report.signal
                    action_icon = {"BUY": "📈", "SELL": "📉", "HOLD": "➡️"}.get(signal.action, "❓")
                    
                    safe_print(f"  信号: {action_icon} {signal.action}")
                    safe_print(f"  置信度: {signal.confidence:.2f}")
                    
                    # 添加基础分析说明
                    if signal.action == "BUY":
                        safe_print(f"  建议: 建议关注，可考虑分批建仓")
                    elif signal.action == "SELL":
                        safe_print(f"  建议: 谨慎观望，如有持仓可考虑减持")
                    else:
                        safe_print(f"  建议: 维持观望，等待更明确信号")
                    
                    analysis_results.append({
                        "股票": f"{name}({code})",
                        "信号": signal.action,
                        "置信度": signal.confidence
                    })
                else:
                    safe_print(f"  ❌ 信号生成失败")
                    
            except Exception as e:
                safe_print(f"  ❌ 分析失败: {str(e)}")
        
        # 生成汇总表
        if analysis_results:
            safe_print("\n📋 分析结果汇总:")
            safe_print("-" * 60)
            for result in analysis_results:
                action_icon = {"BUY": "📈", "SELL": "📉", "HOLD": "➡️"}.get(result["信号"], "❓")
                safe_print(f"{result['股票']:<15} {action_icon} {result['信号']:<4} 置信度:{result['置信度']:.2f}")
        
        return len(analysis_results) > 0
        
    except Exception as e:
        safe_print(f"热门股票分析失败: {e}")
        return False

def generate_investment_advice():
    """生成投资建议"""
    safe_print("\n" + "-"*60)
    safe_print("💡 今日投资建议")
    safe_print("-"*60)
    
    safe_print("""
📌 基于以上分析，投资建议如下:

1. 🎯 短期策略
   • 关注高置信度BUY信号的股票
   • 避免低置信度或SELL信号的标的
   • 控制单一标的仓位不超过20%

2. ⚖️ 风险控制
   • 设定止损点位（建议-8%）
   • 分批建仓，避免一次性重仓
   • 关注市场整体趋势变化

3. ⏰ 操作时机
   • 开盘后观察30分钟再决定
   • 避免尾盘冲动交易
   • 重点关注量价配合情况

4. 📈 中长期布局
   • 重点关注基本面良好的龙头股
   • 适当配置成长性行业标的
   • 保持合理的现金储备

⚠️ 风险提示: 
• 本分析仅供参考，不构成投资建议
• 股市有风险，投资需谨慎
• 请根据自身风险承受能力进行投资决策
    """)

def main():
    """主分析流程"""
    try:
        # 获取市场概况
        get_market_overview()
        
        # 分析主要指数
        indices_success = analyze_major_indices()
        
        # 分析热门股票  
        stocks_success = analyze_hot_stocks()
        
        # 生成投资建议
        generate_investment_advice()
        
        # 输出分析结果
        safe_print("\n" + "="*80)
        safe_print("📊 分析完成情况")
        safe_print("="*80)
        
        safe_print(f"指数分析: {'✅ 完成' if indices_success else '❌ 失败'}")
        safe_print(f"个股分析: {'✅ 完成' if stocks_success else '❌ 失败'}")
        
        if indices_success or stocks_success:
            safe_print("\n🎉 A股今日行情分析完成！")
            safe_print(f"📄 分析报告已生成，请根据建议谨慎投资。")
            return True
        else:
            safe_print("\n❌ 分析过程中遇到问题，请检查网络连接和数据源。")
            return False
            
    except Exception as e:
        safe_print(f"\n❌ 分析过程发生错误: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)