#!/usr/bin/env python3
"""
测试双数据源的协同工作
验证Tushare和AKShare能同时提供数据并进行对比
"""

import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data.tushare_config import TushareDataProvider
from src.data.data_manager import DataManager
import json
from datetime import datetime

def test_dual_data_sources():
    """测试双数据源协同工作"""
    print("=== 双数据源协同测试 ===\n")
    
    # 初始化两个数据源
    tushare_provider = TushareDataProvider(token="2e6561572caa8a088167963e5c9fb5b5b5dbacc83ac714e9596bdc47")
    data_manager = DataManager(tushare_token="2e6561572caa8a088167963e5c9fb5b5b5dbacc83ac714e9596bdc47")
    
    print("1. 数据源状态对比:")
    status = data_manager.get_data_source_status()
    print(f"   Tushare: {'[可用]' if status['tushare']['available'] else '[不可用]'}")
    print(f"   AKShare: {'[可用]' if status['akshare']['available'] else '[不可用]'}")
    print()
    
    # 获取指数数据对比
    print("2. 指数数据源对比:")
    
    # 从Tushare直接获取
    print("   Tushare数据:")
    tushare_indices = {}
    index_codes = {
        '000001.SH': '上证指数',
        '399001.SZ': '深证成指',
        '399006.SZ': '创业板指'
    }
    
    for code, name in index_codes.items():
        df = tushare_provider.get_index_daily(code)
        if df is not None and not df.empty:
            latest = df.iloc[-1]
            tushare_indices[name] = {
                'source': 'Tushare',
                'price': float(latest['close']),
                'change_pct': float(latest.get('pct_chg', 0)),
                'date': latest['trade_date']
            }
            print(f"     {name}: {latest['close']:.2f} ({latest.get('pct_chg', 0):+.2f}%)")
    
    print("   综合管理器数据(包含AKShare):")
    combined_indices = data_manager.get_realtime_index_data()
    akshare_indices = {}
    for name, data in combined_indices.items():
        akshare_indices[name] = {
            'source': data['data_source'],
            'price': data['current_price'],
            'change_pct': data['change_pct'],
            'date': data.get('trade_date', data.get('update_time', ''))
        }
        print(f"     {name}: {data['current_price']:.2f} ({data['change_pct']:+.2f}%) [{data['data_source']}]")
    print()
    
    # 数据一致性检查
    print("3. 数据一致性检查:")
    for index_name in ['上证指数', '深证成指', '创业板指']:
        if index_name in tushare_indices and index_name in akshare_indices:
            ts_price = tushare_indices[index_name]['price']
            ak_price = akshare_indices[index_name]['price']
            price_diff = abs(ts_price - ak_price)
            price_diff_pct = price_diff / ts_price * 100 if ts_price > 0 else 0
            
            print(f"   {index_name}:")
            print(f"     Tushare: {ts_price:.2f}")
            print(f"     AKShare: {ak_price:.2f}")
            print(f"     差异: {price_diff:.2f} ({price_diff_pct:.3f}%)")
    print()
    
    # 强制测试Tushare备用机制
    print("4. 测试Tushare备用机制:")
    # 临时禁用AKShare来测试Tushare备用
    original_akshare_status = data_manager.akshare_available
    data_manager.akshare_available = False
    
    print("   禁用AKShare后的指数数据:")
    backup_indices = data_manager.get_realtime_index_data()
    for name, data in backup_indices.items():
        print(f"     {name}: {data['current_price']:.2f} ({data['change_pct']:+.2f}%) [{data['data_source']}]")
    
    # 恢复AKShare状态
    data_manager.akshare_available = original_akshare_status
    print()
    
    # 综合结果保存
    print("5. 保存对比结果:")
    comparison_results = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'tushare_indices': tushare_indices,
        'akshare_indices': akshare_indices,
        'data_sources_status': status,
        'test_type': 'dual_source_comparison'
    }
    
    try:
        with open('F:/myTrade/test/dual_source_comparison.json', 'w', encoding='utf-8') as f:
            json.dump(comparison_results, f, ensure_ascii=False, indent=2)
        print("   [成功] 双数据源对比结果已保存")
    except Exception as e:
        print(f"   [错误] {e}")
    
    print("\n=== 双数据源协同测试完成 ===")
    return True

if __name__ == "__main__":
    test_dual_data_sources()