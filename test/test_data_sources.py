#!/usr/bin/env python3
"""
测试数据源综合能力
验证Tushare和AKShare数据源的集成效果
"""

import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data.data_manager import DataManager
import json

def test_data_sources():
    """测试数据源综合功能"""
    print("=== 数据源综合测试 ===\n")
    
    # 初始化数据管理器
    dm = DataManager(tushare_token="2e6561572caa8a088167963e5c9fb5b5b5dbacc83ac714e9596bdc47")
    
    # 1. 测试数据源状态
    print("1. 数据源状态检查:")
    status = dm.get_data_source_status()
    for source, info in status.items():
        if source != 'last_check':
            status_text = '[可用]' if info['available'] else '[不可用]'
            print(f"   {source}: {status_text}")
    print()
    
    # 2. 测试实时指数数据
    print("2. 实时指数数据测试:")
    indices = dm.get_realtime_index_data()
    if indices:
        for name, data in indices.items():
            print(f"   {name}: {data['current_price']:.2f} ({data['change_pct']:+.2f}%) [{data['data_source']}]")
    else:
        print("   [失败] 未获取到指数数据")
    print()
    
    # 3. 测试股票基本信息
    print("3. 股票基本信息测试:")
    stock_info = dm.get_stock_basic_info()
    if stock_info is not None and not stock_info.empty:
        print(f"   [成功] 获取到 {len(stock_info)} 只股票的基本信息")
        print(f"   样例: {stock_info.iloc[0]['name']} ({stock_info.iloc[0]['ts_code']})")
    else:
        print("   [失败] 未获取到股票基本信息")
    print()
    
    # 4. 测试市场情绪指标
    print("4. 市场情绪指标测试:")
    sentiment = dm.get_market_sentiment()
    if sentiment:
        if 'tushare_metrics' in sentiment:
            metrics = sentiment['tushare_metrics']
            print(f"   市场平均PE: {metrics.get('avg_pe', 'N/A')}")
            print(f"   市场平均PB: {metrics.get('avg_pb', 'N/A')}")
            print(f"   平均换手率: {metrics.get('avg_turnover_rate', 'N/A')}%")
        if 'northbound_flow' in sentiment:
            flow = sentiment['northbound_flow']
            print(f"   北向资金: {flow['today_flow']:.2f}亿 ({flow['recent_trend']})")
        if not sentiment:
            print("   [警告] 当日市场情绪数据不可用（可能是非交易日）")
    print()
    
    # 5. 测试综合市场数据
    print("5. 综合市场数据测试:")
    market_data = dm.get_comprehensive_market_data()
    if market_data:
        print(f"   [成功] 综合数据获取成功")
        print(f"   数据更新时间: {market_data['timestamp']}")
        print(f"   包含数据模块: {list(market_data.keys())}")
        
        # 保存测试结果到文件
        with open('F:/myTrade/test/test_results.json', 'w', encoding='utf-8') as f:
            # 转换为JSON兼容格式
            json_data = {}
            for key, value in market_data.items():
                if key != 'indices':
                    json_data[key] = value
                else:
                    # 转换indices数据
                    json_data[key] = {k: v for k, v in value.items()}
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        print("   [保存] 测试结果已保存到 test_results.json")
    else:
        print("   [失败] 综合数据获取失败")
    print()
    
    print("=== 测试完成 ===")
    return True

if __name__ == "__main__":
    test_data_sources()