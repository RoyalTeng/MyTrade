#!/usr/bin/env python3
"""
调试数据源接口

测试各种数据接口，找出能获取真实最新数据的方法
"""

import sys
from pathlib import Path
import warnings

# 添加src到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from test_encoding_fix import safe_print
warnings.filterwarnings('ignore')

def test_akshare_apis():
    """测试akshare各种API"""
    try:
        import akshare as ak
        safe_print("🔍 测试akshare数据接口...")
        
        # 测试1: 股票现价数据
        try:
            safe_print("1. 测试股票现价数据...")
            stock_current = ak.stock_zh_a_spot_em()
            if not stock_current.empty:
                # 显示前几只股票
                sample = stock_current.head(5)
                safe_print("   ✅ 成功获取股票现价数据")
                safe_print(f"   数据量: {len(stock_current)}只股票")
                for _, row in sample.iterrows():
                    safe_print(f"   {row.get('代码', 'N/A')} {row.get('名称', 'N/A')}: {row.get('最新价', 'N/A')}元 ({row.get('涨跌幅', 'N/A')}%)")
            else:
                safe_print("   ❌ 股票现价数据为空")
        except Exception as e:
            safe_print(f"   ❌ 股票现价数据获取失败: {e}")
        
        # 测试2: 大盘指数数据
        try:
            safe_print("2. 测试大盘指数数据...")
            # 尝试不同的指数获取方法
            methods = [
                ('stock_zh_index_spot_em', 'sh000001'),
                ('index_zh_a_hist', 'sh000001'),
            ]
            
            for method_name, symbol in methods:
                try:
                    if hasattr(ak, method_name):
                        method = getattr(ak, method_name)
                        if method_name == 'stock_zh_index_spot_em':
                            data = method(symbol=symbol)
                        else:
                            from datetime import datetime
                            today = datetime.now().strftime('%Y%m%d')
                            data = method(symbol=symbol, start_date=today, end_date=today)
                        
                        if not data.empty:
                            safe_print(f"   ✅ {method_name} 成功")
                            safe_print(f"   数据样本: {data.iloc[0].to_dict()}")
                            break
                        else:
                            safe_print(f"   ⚠️ {method_name} 数据为空")
                    else:
                        safe_print(f"   ❌ {method_name} 方法不存在")
                except Exception as e:
                    safe_print(f"   ❌ {method_name} 失败: {e}")
                    
        except Exception as e:
            safe_print(f"   ❌ 指数数据测试失败: {e}")
        
        # 测试3: 实时大盘数据
        try:
            safe_print("3. 测试实时大盘数据...")
            # 尝试获取实时大盘数据
            realtime_methods = ['stock_zh_index_spot', 'tool_trade_date_hist_sina']
            
            for method_name in realtime_methods:
                try:
                    if hasattr(ak, method_name):
                        method = getattr(ak, method_name)
                        data = method()
                        safe_print(f"   ✅ {method_name} 可用")
                        if hasattr(data, 'head'):
                            safe_print(f"   数据预览: {data.head(3)}")
                    else:
                        safe_print(f"   ❌ {method_name} 不存在")
                except Exception as e:
                    safe_print(f"   ❌ {method_name} 失败: {e}")
                    
        except Exception as e:
            safe_print(f"   ❌ 实时大盘数据测试失败: {e}")
        
        # 测试4: 板块数据
        try:
            safe_print("4. 测试板块数据...")
            sector_data = ak.stock_board_industry_name_em()
            if not sector_data.empty:
                safe_print(f"   ✅ 成功获取{len(sector_data)}个板块数据")
                # 显示前几个板块
                for _, row in sector_data.head(3).iterrows():
                    safe_print(f"   {row.get('板块名称', 'N/A')}: {row.get('涨跌幅', 'N/A')}%")
            else:
                safe_print("   ❌ 板块数据为空")
        except Exception as e:
            safe_print(f"   ❌ 板块数据获取失败: {e}")
        
        # 测试5: 市场统计数据
        try:
            safe_print("5. 测试市场统计数据...")
            stock_all = ak.stock_zh_a_spot_em()
            if not stock_all.empty:
                total = len(stock_all)
                up_count = len(stock_all[stock_all['涨跌幅'] > 0])
                down_count = len(stock_all[stock_all['涨跌幅'] < 0])
                flat_count = total - up_count - down_count
                
                safe_print(f"   ✅ 市场统计数据:")
                safe_print(f"   总股票: {total}只")
                safe_print(f"   上涨: {up_count}只 ({up_count/total:.1%})")
                safe_print(f"   下跌: {down_count}只 ({down_count/total:.1%})")
                safe_print(f"   平盘: {flat_count}只 ({flat_count/total:.1%})")
                
                # 涨跌停统计
                limit_up = len(stock_all[stock_all['涨跌幅'] >= 9.8])
                limit_down = len(stock_all[stock_all['涨跌幅'] <= -9.8])
                safe_print(f"   涨停: {limit_up}只")
                safe_print(f"   跌停: {limit_down}只")
                
            else:
                safe_print("   ❌ 无法获取股票统计数据")
                
        except Exception as e:
            safe_print(f"   ❌ 市场统计数据失败: {e}")
            
    except ImportError:
        safe_print("❌ akshare 未安装")
        return False
    
    return True

def test_alternative_sources():
    """测试其他数据源"""
    safe_print("🌐 测试其他数据源...")
    
    # 测试通过requests直接获取数据
    try:
        import requests
        import json
        
        # 测试新浪财经接口
        safe_print("1. 测试新浪财经接口...")
        urls = [
            "https://hq.sinajs.cn/list=s_sh000001,s_sz399001,s_sz399006",  # 指数
            "https://hq.sinajs.cn/list=sz000001",  # 个股
        ]
        
        for i, url in enumerate(urls):
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    content = response.text
                    safe_print(f"   ✅ 接口{i+1}响应正常")
                    safe_print(f"   数据样本: {content[:200]}...")
                else:
                    safe_print(f"   ❌ 接口{i+1}响应异常: {response.status_code}")
            except Exception as e:
                safe_print(f"   ❌ 接口{i+1}请求失败: {e}")
                
    except ImportError:
        safe_print("❌ requests 未安装")
    
    # 测试东方财富接口
    try:
        safe_print("2. 测试东方财富接口...")
        eastmoney_url = "https://push2.eastmoney.com/api/qt/clist/get"
        params = {
            'pn': '1',
            'pz': '50',
            'po': '1',
            'np': '1',
            'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
            'fltt': '2',
            'invt': '2',
            'fid': 'f3',
            'fs': 'm:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23',
            'fields': 'f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152'
        }
        
        response = requests.get(eastmoney_url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and 'diff' in data['data']:
                stocks = data['data']['diff']
                safe_print(f"   ✅ 东方财富接口正常，获取{len(stocks)}只股票数据")
                # 显示前3只股票
                for stock in stocks[:3]:
                    name = stock.get('f14', 'N/A')
                    code = stock.get('f12', 'N/A')
                    price = stock.get('f2', 'N/A')
                    change_pct = stock.get('f3', 'N/A')
                    safe_print(f"   {code} {name}: {price}元 ({change_pct}%)")
            else:
                safe_print("   ❌ 东方财富数据格式异常")
        else:
            safe_print(f"   ❌ 东方财富接口响应异常: {response.status_code}")
            
    except Exception as e:
        safe_print(f"   ❌ 东方财富接口测试失败: {e}")

def main():
    """主函数"""
    safe_print("=" * 80)
    safe_print("               数据源接口调试")
    safe_print("=" * 80)
    safe_print("")
    
    # 测试akshare
    akshare_ok = test_akshare_apis()
    safe_print("")
    
    # 测试其他数据源
    test_alternative_sources()
    safe_print("")
    
    safe_print("=" * 80)
    safe_print("               调试完成")
    safe_print("=" * 80)
    
    return akshare_ok

if __name__ == "__main__":
    main()