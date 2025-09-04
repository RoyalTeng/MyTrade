#!/usr/bin/env python3
"""
修复指数数据获取

尝试多种方法获取真实的A股指数数据
"""

import sys
from pathlib import Path
import warnings
import requests
import json

# 添加src到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from test_encoding_fix import safe_print
warnings.filterwarnings('ignore')

def test_eastmoney_index_api():
    """测试东方财富指数API - 方法1"""
    safe_print("🔍 测试东方财富指数API (方法1)...")
    
    try:
        # 直接获取指数列表
        url = "http://push2.eastmoney.com/api/qt/clist/get"
        params = {
            'pn': 1,
            'pz': 20,
            'po': 1,
            'np': 1,
            'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
            'fltt': 2,
            'invt': 2,
            'fid': 'f3',
            'fs': 'm:1+s:2',  # 上证指数
            'fields': 'f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152'
        }
        
        response = requests.get(url, params=params, timeout=15)
        if response.status_code == 200:
            data = response.json()
            safe_print(f"  ✅ API响应正常")
            if 'data' in data and data['data'] and 'diff' in data['data']:
                items = data['data']['diff']
                safe_print(f"  获取到{len(items)}个数据项")
                
                for item in items[:3]:  # 显示前3个
                    code = item.get('f12', 'N/A')
                    name = item.get('f14', 'N/A') 
                    price = item.get('f2', 0)
                    change_pct = item.get('f3', 0)
                    safe_print(f"    {code} {name}: {price} ({change_pct}%)")
                
                return items
            else:
                safe_print(f"  ❌ 数据格式异常: {data}")
        else:
            safe_print(f"  ❌ API响应错误: {response.status_code}")
            
    except Exception as e:
        safe_print(f"  ❌ 方法1失败: {e}")
    
    return None

def test_eastmoney_index_api_v2():
    """测试东方财富指数API - 方法2"""
    safe_print("🔍 测试东方财富指数API (方法2)...")
    
    index_codes = {
        '000001': '上证综指',
        '399001': '深证成指', 
        '399006': '创业板指'
    }
    
    results = {}
    
    for code, name in index_codes.items():
        try:
            # 直接通过代码获取指数数据
            url = f"http://push2.eastmoney.com/api/qt/stock/get"
            params = {
                'ut': 'fa5fd1943c7b386f172d6893dbfba10b',
                'invt': 2,
                'fltt': 2,
                'fields': 'f43,f57,f58,f169,f170,f46,f60,f44,f51,f168,f47,f164,f163,f116,f60,f45,f52',
                'secid': f"{'1' if code.startswith('0') else '0'}.{code}"
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and data['data']:
                    item = data['data']
                    results[code] = {
                        'name': name,
                        'code': code,
                        'close': item.get('f43', 0) / 100,  # 最新价
                        'change': item.get('f169', 0) / 100,  # 涨跌额
                        'change_pct': item.get('f170', 0) / 100,  # 涨跌幅
                        'open': item.get('f46', 0) / 100,  # 开盘价
                        'high': item.get('f44', 0) / 100,  # 最高价
                        'low': item.get('f45', 0) / 100,   # 最低价
                    }
                    safe_print(f"  ✅ {name}: {results[code]['close']:.2f} ({results[code]['change_pct']:+.2f}%)")
                else:
                    safe_print(f"  ❌ {name}: 无数据")
            else:
                safe_print(f"  ❌ {name}: HTTP {response.status_code}")
                
        except Exception as e:
            safe_print(f"  ❌ {name}: {e}")
    
    return results

def test_sina_index_api():
    """测试新浪财经指数API"""
    safe_print("🔍 测试新浪财经指数API...")
    
    try:
        # 新浪财经指数接口
        url = "http://hq.sinajs.cn/list=s_sh000001,s_sz399001,s_sz399006"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'http://finance.sina.com.cn/'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            content = response.text
            safe_print(f"  ✅ 新浪接口响应正常")
            safe_print(f"  数据内容: {content[:200]}...")
            
            # 解析数据
            lines = content.strip().split('\n')
            results = {}
            
            index_map = {
                's_sh000001': ('000001', '上证综指'),
                's_sz399001': ('399001', '深证成指'),
                's_sz399006': ('399006', '创业板指')
            }
            
            for line in lines:
                if '=' in line and '"' in line:
                    parts = line.split('=')
                    if len(parts) >= 2:
                        var_name = parts[0].split('_')[-1] if '_' in parts[0] else parts[0]
                        data_str = parts[1].strip().strip('"').rstrip('";')
                        
                        if data_str and ',' in data_str:
                            data_parts = data_str.split(',')
                            if len(data_parts) >= 4:
                                for key, (code, name) in index_map.items():
                                    if key in parts[0]:
                                        try:
                                            results[code] = {
                                                'name': name,
                                                'code': code,
                                                'close': float(data_parts[1]),
                                                'change': float(data_parts[2]),
                                                'change_pct': float(data_parts[3]),
                                            }
                                            safe_print(f"    ✅ {name}: {results[code]['close']:.2f} ({results[code]['change_pct']:+.2f}%)")
                                        except (ValueError, IndexError) as e:
                                            safe_print(f"    ❌ {name}: 数据解析失败 {e}")
                                        break
            
            return results
            
        else:
            safe_print(f"  ❌ 新浪接口响应异常: {response.status_code}")
            
    except Exception as e:
        safe_print(f"  ❌ 新浪接口失败: {e}")
    
    return None

def test_akshare_alternative():
    """测试akshare的其他接口"""
    safe_print("🔍 测试akshare其他接口...")
    
    try:
        import akshare as ak
        
        # 方法1: 尝试其他指数接口
        methods_to_try = [
            ('stock_zh_index_daily_em', '上证综指daily'),
            ('stock_zh_index_daily_tx', '腾讯指数daily'),
        ]
        
        from datetime import datetime
        today = datetime.now().strftime('%Y%m%d')
        
        for method_name, desc in methods_to_try:
            try:
                if hasattr(ak, method_name):
                    safe_print(f"  尝试 {desc}...")
                    method = getattr(ak, method_name)
                    
                    # 尝试获取上证指数
                    if 'daily' in method_name:
                        data = method(symbol="sh000001", start_date=today, end_date=today)
                    else:
                        data = method(symbol="sh000001")
                    
                    if not data.empty:
                        safe_print(f"    ✅ {desc} 成功获取数据")
                        safe_print(f"    数据样本: {data.tail(1).to_dict()}")
                        return data
                    else:
                        safe_print(f"    ❌ {desc} 数据为空")
                else:
                    safe_print(f"    ❌ {desc} 方法不存在")
                    
            except Exception as e:
                safe_print(f"    ❌ {desc} 失败: {e}")
        
        # 方法2: 尝试获取股票数据中的指数ETF
        safe_print("  尝试指数ETF数据...")
        try:
            # 获取上证50ETF、沪深300ETF等作为指数参考
            etf_codes = ['510050', '510300', '159919']  # 上证50ETF, 沪深300ETF, 创业板ETF
            etf_data = ak.stock_zh_a_spot_em()
            
            results = {}
            for code in etf_codes:
                etf_info = etf_data[etf_data['代码'] == code]
                if not etf_info.empty:
                    row = etf_info.iloc[0]
                    name = row.get('名称', '')
                    price = float(row.get('最新价', 0))
                    change_pct = float(row.get('涨跌幅', 0))
                    
                    results[code] = {
                        'name': name,
                        'code': code,
                        'close': price,
                        'change_pct': change_pct
                    }
                    safe_print(f"    ✅ {name}: {price:.3f} ({change_pct:+.2f}%)")
            
            if results:
                return results
                
        except Exception as e:
            safe_print(f"    ❌ ETF数据失败: {e}")
            
    except ImportError:
        safe_print("  ❌ akshare 未安装")
    except Exception as e:
        safe_print(f"  ❌ akshare测试失败: {e}")
    
    return None

def test_tencent_api():
    """测试腾讯财经API"""
    safe_print("🔍 测试腾讯财经API...")
    
    try:
        # 腾讯财经接口
        codes = ['sh000001', 'sz399001', 'sz399006']
        url = f"http://qt.gtimg.cn/q={','.join(codes)}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            content = response.text
            safe_print(f"  ✅ 腾讯接口响应正常")
            
            results = {}
            lines = content.strip().split('\n')
            
            name_map = {
                'sh000001': '上证综指',
                'sz399001': '深证成指',
                'sz399006': '创业板指'
            }
            
            for line in lines:
                if '=' in line and '~' in line:
                    parts = line.split('=')
                    if len(parts) >= 2:
                        var_part = parts[0]
                        data_part = parts[1].strip().strip('"').rstrip('";')
                        
                        # 提取代码
                        code = None
                        for c in codes:
                            if c in var_part:
                                code = c
                                break
                        
                        if code and data_part:
                            data_fields = data_part.split('~')
                            if len(data_fields) >= 10:
                                try:
                                    results[code] = {
                                        'name': name_map.get(code, data_fields[1]),
                                        'code': code,
                                        'close': float(data_fields[3]),
                                        'change': float(data_fields[31]) if len(data_fields) > 31 else 0,
                                        'change_pct': float(data_fields[32]) if len(data_fields) > 32 else 0,
                                        'open': float(data_fields[5]) if len(data_fields) > 5 else 0,
                                        'high': float(data_fields[33]) if len(data_fields) > 33 else 0,
                                        'low': float(data_fields[34]) if len(data_fields) > 34 else 0,
                                    }
                                    safe_print(f"    ✅ {results[code]['name']}: {results[code]['close']:.2f} ({results[code]['change_pct']:+.2f}%)")
                                except (ValueError, IndexError) as e:
                                    safe_print(f"    ❌ {code}: 解析失败 {e}")
            
            return results
            
        else:
            safe_print(f"  ❌ 腾讯接口响应异常: {response.status_code}")
            
    except Exception as e:
        safe_print(f"  ❌ 腾讯接口失败: {e}")
    
    return None

def main():
    """主函数"""
    safe_print("=" * 80)
    safe_print("                   指数数据获取修复测试")
    safe_print("=" * 80)
    safe_print("")
    
    all_results = {}
    
    # 测试各种方法
    methods = [
        ("东方财富API v1", test_eastmoney_index_api),
        ("东方财富API v2", test_eastmoney_index_api_v2),
        ("新浪财经API", test_sina_index_api),
        ("腾讯财经API", test_tencent_api),
        ("akshare其他接口", test_akshare_alternative),
    ]
    
    success_count = 0
    
    for method_name, method_func in methods:
        safe_print(f"{'='*20} {method_name} {'='*20}")
        result = method_func()
        safe_print("")
        
        if result:
            all_results[method_name] = result
            success_count += 1
            safe_print(f"✅ {method_name} 成功获取数据")
        else:
            safe_print(f"❌ {method_name} 获取失败")
        
        safe_print("-" * 60)
    
    # 总结
    safe_print("")
    safe_print("=" * 80)
    safe_print("                      测试总结")
    safe_print("=" * 80)
    safe_print("")
    
    safe_print(f"📊 测试结果: {success_count}/{len(methods)} 个方法成功")
    safe_print("")
    
    if all_results:
        safe_print("🎯 推荐使用的数据源:")
        for method_name, data in all_results.items():
            safe_print(f"  ✅ {method_name}: 可获取{len(data)}个指数数据")
        
        # 选择最好的数据源
        best_method = max(all_results.keys(), key=lambda x: len(all_results[x]) if isinstance(all_results[x], dict) else 0)
        best_data = all_results[best_method]
        
        safe_print(f"")
        safe_print(f"🥇 最佳数据源: {best_method}")
        safe_print("   获取的指数数据:")
        
        if isinstance(best_data, dict):
            for code, info in best_data.items():
                name = info.get('name', code)
                close = info.get('close', 0)
                change_pct = info.get('change_pct', 0)
                safe_print(f"     {name}: {close:.2f}点 ({change_pct:+.2f}%)")
        else:
            safe_print("     数据格式不是字典类型")
        
        # 保存最佳结果
        output_file = Path(__file__).parent / 'best_index_data.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'method': best_method,
                'data': best_data,
                'timestamp': str(datetime.now())
            }, f, ensure_ascii=False, indent=2, default=str)
        
        safe_print(f"")
        safe_print(f"💾 最佳数据已保存到: {output_file}")
        
        return best_data
    else:
        safe_print("❌ 所有方法都失败了")
        return None

if __name__ == "__main__":
    from datetime import datetime
    result = main()
    if result:
        safe_print(f"\n🎉 指数数据获取修复成功!")
    else:
        safe_print(f"\n😞 指数数据获取仍有问题，需要进一步调试")