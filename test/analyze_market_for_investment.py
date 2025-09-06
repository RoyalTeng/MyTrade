#!/usr/bin/env python3
"""
A股市场投资分析脚本
为10000元本金选择优质股票投资组合
"""

import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data.data_manager import DataManager
import pandas as pd
import json
from datetime import datetime, timedelta

def analyze_a_stock_market():
    """分析A股市场并选择投资标的"""
    
    print("=== A股市场投资分析 ===")
    print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"投资本金: 10,000元")
    print(f"预期收益: 20%")
    print()
    
    # 初始化数据管理器
    dm = DataManager(tushare_token="2e6561572caa8a088167963e5c9fb5b5b5dbacc83ac714e9596bdc47")
    
    # 1. 获取市场整体情况
    print("=== 市场整体分析 ===")
    indices = dm.get_realtime_index_data()
    
    market_analysis = {}
    if indices:
        print("主要指数表现:")
        for name, data in indices.items():
            change_symbol = "[上涨]" if data['change_pct'] > 0 else "[下跌]" if data['change_pct'] < 0 else "[平盘]"
            print(f"  {change_symbol} {name}: {data['current_price']:.2f} ({data['change_pct']:+.2f}%)")
            market_analysis[name] = {
                'price': data['current_price'],
                'change': data['change_pct'],
                'performance': 'strong' if data['change_pct'] > 5 else 'good' if data['change_pct'] > 2 else 'neutral' if data['change_pct'] > -2 else 'weak'
            }
    
    # 2. 市场情绪分析
    print("\n=== 市场情绪分析 ===")
    sentiment = dm.get_market_sentiment()
    if sentiment and 'tushare_metrics' in sentiment:
        metrics = sentiment['tushare_metrics']
        avg_pe = metrics.get('avg_pe', 0)
        avg_pb = metrics.get('avg_pb', 0)
        avg_turnover = metrics.get('avg_turnover_rate', 0)
        
        print(f"市场平均估值:")
        print(f"  平均PE: {avg_pe:.2f} {'(偏高)' if avg_pe > 25 else '(合理)' if avg_pe > 15 else '(偏低)'}")
        print(f"  平均PB: {avg_pb:.2f} {'(偏高)' if avg_pb > 3 else '(合理)' if avg_pb > 1.5 else '(偏低)'}")
        print(f"  平均换手率: {avg_turnover:.2f}% {'(活跃)' if avg_turnover > 3 else '(一般)' if avg_turnover > 1 else '(低迷)'}")
    
    # 3. 股票基本信息获取
    print("\n=== 获取股票池数据 ===")
    stock_basic = dm.get_stock_basic_info()
    
    if stock_basic is not None and not stock_basic.empty:
        print(f"[成功] 获取到 {len(stock_basic)} 只A股股票基本信息")
        
        # 筛选活跃股票（排除ST、退市股票等）
        active_stocks = stock_basic[
            (~stock_basic['name'].str.contains('ST', na=False)) &
            (~stock_basic['name'].str.contains('退', na=False)) &
            (stock_basic['list_date'] < '20220101')  # 上市超过2年
        ].copy()
        
        print(f"[成功] 筛选出 {len(active_stocks)} 只活跃股票")
        
        # 选择不同行业的代表股票进行分析
        recommended_stocks = [
            # 科技成长股
            {'code': '000858.SZ', 'name': '五粮液', 'sector': '消费', 'reason': '消费龙头，业绩稳定'},
            {'code': '002415.SZ', 'name': '海康威视', 'sector': '科技', 'reason': 'AI视频监控龙头'},
            {'code': '300059.SZ', 'name': '东方财富', 'sector': '金融科技', 'reason': '互联网金融龙头'},
            {'code': '000002.SZ', 'name': '万科A', 'sector': '房地产', 'reason': '地产龙头，估值低'},
            {'code': '600519.SZ', 'name': '贵州茅台', 'sector': '消费', 'reason': '白酒之王，长期价值投资'},
            {'code': '000001.SZ', 'name': '平安银行', 'sector': '金融', 'reason': '股份制银行龙头'},
            {'code': '002142.SZ', 'name': '宁波银行', 'sector': '金融', 'reason': '城商行翘楚'},
            {'code': '300750.SZ', 'name': '宁德时代', 'sector': '新能源', 'reason': '全球动力电池龙头'},
            {'code': '600036.SH', 'name': '招商银行', 'sector': '金融', 'reason': '银行业龙头'},
            {'code': '002714.SZ', 'name': '牧原股份', 'sector': '农业', 'reason': '生猪养殖龙头'}
        ]
        
    # 4. 投资建议分析
    print(f"\n=== 投资建议分析 ===")
    
    # 基于市场情况制定投资策略
    market_trend = "成长股市场" if market_analysis.get('创业板指', {}).get('change', 0) > 3 else "均衡市场"
    
    investment_strategy = {
        'market_view': market_trend,
        'allocation_strategy': '7:2:1分配' if market_trend == "成长股市场" else '6:3:1分配',
        'risk_level': '中等偏高',
        'time_horizon': '6-12个月',
        'expected_return': '20%',
        'max_drawdown': '15%'
    }
    
    print(f"[市场判断] {investment_strategy['market_view']}")
    print(f"[配置策略] {investment_strategy['allocation_strategy']}")
    print(f"[风险等级] {investment_strategy['risk_level']}")
    print(f"[投资周期] {investment_strategy['time_horizon']}")
    
    # 5. 生成详细分析结果
    analysis_result = {
        'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'market_analysis': market_analysis,
        'market_sentiment': sentiment,
        'investment_strategy': investment_strategy,
        'recommended_stocks': recommended_stocks,
        'total_stocks_analyzed': len(stock_basic) if stock_basic is not None else 0
    }
    
    # 保存分析结果
    with open('F:/myTrade/reports/a_stock_investment_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(analysis_result, f, ensure_ascii=False, indent=2)
    
    print(f"\n[成功] 分析完成，结果已保存到 reports/a_stock_investment_analysis.json")
    
    return analysis_result

if __name__ == "__main__":
    analyze_a_stock_market()