#!/usr/bin/env python3
"""
专门测试Tushare数据获取功能
验证Tushare API是否能正常接收数据
"""

import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data.tushare_config import TushareDataProvider
import json
from datetime import datetime, timedelta

def test_tushare_data():
    """专门测试Tushare数据获取"""
    print("=== Tushare数据源专项测试 ===\n")
    
    # 初始化Tushare数据提供者
    provider = TushareDataProvider(token="2e6561572caa8a088167963e5c9fb5b5b5dbacc83ac714e9596bdc47")
    
    # 1. 测试连接
    print("1. 连接测试:")
    success, message = provider.test_connection()
    print(f"   结果: {'[成功]' if success else '[失败]'} {message}")
    print()
    
    if not success:
        print("Tushare连接失败，无法继续测试")
        return False
    
    # 2. 测试股票基本信息
    print("2. 股票基本信息测试:")
    try:
        stock_basic = provider.get_stock_basic()
        if stock_basic is not None and not stock_basic.empty:
            print(f"   [成功] 获取到 {len(stock_basic)} 只股票信息")
            print(f"   样例数据:")
            for i in range(min(3, len(stock_basic))):
                stock = stock_basic.iloc[i]
                print(f"     {stock['name']} ({stock['ts_code']}) - {stock.get('industry', 'N/A')}")
        else:
            print("   [失败] 未获取到股票基本信息")
    except Exception as e:
        print(f"   [错误] {e}")
    print()
    
    # 3. 测试指数日线数据
    print("3. 指数日线数据测试:")
    index_codes = {
        '000001.SH': '上证指数',
        '399001.SZ': '深证成指', 
        '399006.SZ': '创业板指'
    }
    
    index_data = {}
    for code, name in index_codes.items():
        try:
            df = provider.get_index_daily(code)
            if df is not None and not df.empty:
                latest = df.iloc[-1]
                index_data[name] = {
                    'code': code,
                    'name': name,
                    'date': latest['trade_date'],
                    'close': float(latest['close']),
                    'change_pct': float(latest.get('pct_chg', 0)),
                    'volume': float(latest.get('vol', 0)),
                    'amount': float(latest.get('amount', 0))
                }
                print(f"   [成功] {name}: {latest['close']:.2f} ({latest.get('pct_chg', 0):+.2f}%) 日期:{latest['trade_date']}")
            else:
                print(f"   [失败] {name}: 无数据")
        except Exception as e:
            print(f"   [错误] {name}: {e}")
    print()
    
    # 4. 测试个股日线数据
    print("4. 个股日线数据测试:")
    test_stocks = ['000001.SZ', '000002.SZ', '600000.SH']  # 平安银行、万科、浦发银行
    
    stock_data = {}
    for ts_code in test_stocks:
        try:
            df = provider.get_daily_data(ts_code)
            if df is not None and not df.empty:
                latest = df.iloc[-1]
                stock_data[ts_code] = {
                    'ts_code': ts_code,
                    'date': latest['trade_date'],
                    'close': float(latest['close']),
                    'change_pct': float(latest.get('pct_chg', 0)),
                    'volume': float(latest.get('vol', 0))
                }
                print(f"   [成功] {ts_code}: {latest['close']:.2f} ({latest.get('pct_chg', 0):+.2f}%) 日期:{latest['trade_date']}")
            else:
                print(f"   [失败] {ts_code}: 无数据")
        except Exception as e:
            print(f"   [错误] {ts_code}: {e}")
    print()
    
    # 5. 测试基金数据
    print("5. 基金基本信息测试:")
    try:
        fund_basic = provider.get_fund_basic()
        if fund_basic is not None and not fund_basic.empty:
            print(f"   [成功] 获取到 {len(fund_basic)} 只基金信息")
            print(f"   样例数据:")
            for i in range(min(3, len(fund_basic))):
                fund = fund_basic.iloc[i]
                print(f"     {fund['name']} ({fund['ts_code']}) - {fund.get('fund_type', 'N/A')}")
        else:
            print("   [失败] 未获取到基金基本信息")
    except Exception as e:
        print(f"   [错误] {e}")
    print()
    
    # 6. 测试市场情绪数据
    print("6. 市场情绪数据测试:")
    try:
        # 尝试获取最近几天的数据
        for days_back in range(5):
            test_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y%m%d')
            sentiment = provider.get_market_sentiment(test_date)
            if sentiment is not None and not sentiment.empty:
                print(f"   [成功] {test_date}: 获取到 {len(sentiment)} 只股票的市场数据")
                # 计算平均值
                avg_pe = sentiment['pe'].median()
                avg_pb = sentiment['pb'].median() 
                avg_turnover = sentiment['turnover_rate'].median()
                print(f"     平均PE: {avg_pe:.2f}, 平均PB: {avg_pb:.2f}, 平均换手率: {avg_turnover:.2f}%")
                break
            else:
                print(f"   [无数据] {test_date}: 可能非交易日")
        else:
            print("   [失败] 最近5天都无市场情绪数据")
    except Exception as e:
        print(f"   [错误] {e}")
    print()
    
    # 7. 保存Tushare测试结果
    print("7. 保存测试结果:")
    tushare_results = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'connection_test': {'success': success, 'message': message},
        'index_data': index_data,
        'stock_data': stock_data,
        'data_source': 'Tushare Pro'
    }
    
    try:
        with open('F:/myTrade/test/tushare_test_results.json', 'w', encoding='utf-8') as f:
            json.dump(tushare_results, f, ensure_ascii=False, indent=2)
        print("   [成功] Tushare测试结果已保存到 tushare_test_results.json")
    except Exception as e:
        print(f"   [错误] 保存失败: {e}")
    
    print("\n=== Tushare专项测试完成 ===")
    return True

if __name__ == "__main__":
    test_tushare_data()