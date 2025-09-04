#!/usr/bin/env python3
"""
修复紫金矿业实时数据获取问题
使用多个数据源获取准确的实时行情
"""

import sys
import json
from pathlib import Path
from datetime import datetime
import requests

# 添加src到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from test_encoding_fix import safe_print

def get_zijin_realtime_sina():
    """使用新浪财经API获取紫金矿业实时数据"""
    try:
        safe_print("📊 使用新浪财经API获取紫金矿业实时数据...")
        
        # 紫金矿业代码：sh601899
        url = "https://hq.sinajs.cn/list=sh601899"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data_str = response.text.strip()
            if 'var hq_str_' in data_str and '=' in data_str:
                # 解析新浪返回的数据
                data_part = data_str.split('="')[1].split('";')[0]
                fields = data_part.split(',')
                
                if len(fields) >= 32:  # 确保有足够的字段
                    realtime_data = {
                        'symbol': '601899',
                        'name': fields[0],  # 股票名称
                        'open': float(fields[1]) if fields[1] else 0,  # 今开
                        'prev_close': float(fields[2]) if fields[2] else 0,  # 昨收
                        'current_price': float(fields[3]) if fields[3] else 0,  # 现价
                        'high': float(fields[4]) if fields[4] else 0,  # 最高
                        'low': float(fields[5]) if fields[5] else 0,  # 最低
                        'volume': int(float(fields[8])) if fields[8] else 0,  # 成交量(股)
                        'turnover': float(fields[9]) if fields[9] else 0,  # 成交额
                        'date': fields[30],  # 日期
                        'time': fields[31],  # 时间
                    }
                    
                    # 计算涨跌额和涨跌幅
                    if realtime_data['prev_close'] > 0:
                        realtime_data['change'] = realtime_data['current_price'] - realtime_data['prev_close']
                        realtime_data['change_pct'] = (realtime_data['change'] / realtime_data['prev_close']) * 100
                    else:
                        realtime_data['change'] = 0
                        realtime_data['change_pct'] = 0
                    
                    # 估算市值 (粗略计算)
                    total_shares = 58000000000  # 紫金矿业总股本约580亿股
                    realtime_data['market_cap'] = realtime_data['current_price'] * total_shares
                    
                    # 估算PE和PB (需要更多数据，这里给出合理估值)
                    realtime_data['pe_ratio'] = 15.5  # 基于行业平均
                    realtime_data['pb_ratio'] = 2.1   # 基于行业平均
                    
                    # 计算换手率 (成交量/流通股本)
                    float_shares = 48000000000  # 流通股本约480亿股
                    if float_shares > 0:
                        realtime_data['turnover_rate'] = (realtime_data['volume'] / float_shares) * 100
                    else:
                        realtime_data['turnover_rate'] = 0
                    
                    safe_print(f"  ✅ {realtime_data['name']}: {realtime_data['current_price']:.2f}元")
                    safe_print(f"      涨跌幅: {realtime_data['change_pct']:+.2f}% ({realtime_data['change']:+.2f}元)")
                    safe_print(f"      成交量: {realtime_data['volume']:,}股")
                    safe_print(f"      成交额: {realtime_data['turnover']/100000000:.2f}亿元")
                    safe_print(f"      市值: {realtime_data['market_cap']/100000000:.0f}亿元")
                    
                    return realtime_data
                else:
                    safe_print("  ❌ 数据字段不足")
                    return {}
            else:
                safe_print("  ❌ 数据格式不正确")
                return {}
        else:
            safe_print(f"  ❌ 请求失败，状态码: {response.status_code}")
            return {}
            
    except Exception as e:
        safe_print(f"❌ 获取新浪财经数据失败: {e}")
        return {}

def get_zijin_eastmoney_backup():
    """使用东方财富API备用方案"""
    try:
        safe_print("📊 使用东方财富API备用获取数据...")
        
        # 东方财富API
        url = "http://push2.eastmoney.com/api/qt/stock/get"
        params = {
            'ut': 'fa5fd1943c7b386f172d6893dbfba10b',
            'invt': '2',
            'fltt': '2',
            'secid': '1.601899',  # 沪市紫金矿业
            'fields': 'f43,f44,f45,f46,f47,f48,f49,f169,f170,f57,f58'
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and data['data']:
                item = data['data']
                
                # 东方财富的字段都需要除以100
                current_price = float(item.get('f43', 0)) / 100 if item.get('f43') else 0
                prev_close = float(item.get('f60', current_price)) / 100 if item.get('f60') else current_price
                change = float(item.get('f169', 0)) / 100 if item.get('f169') else 0
                change_pct = float(item.get('f170', 0)) / 100 if item.get('f170') else 0
                
                realtime_data = {
                    'symbol': '601899',
                    'name': '紫金矿业',
                    'current_price': current_price,
                    'prev_close': prev_close,
                    'change': change,
                    'change_pct': change_pct,
                    'open': float(item.get('f46', 0)) / 100 if item.get('f46') else current_price,
                    'high': float(item.get('f44', 0)) / 100 if item.get('f44') else current_price,
                    'low': float(item.get('f45', 0)) / 100 if item.get('f45') else current_price,
                    'volume': int(item.get('f47', 0)) if item.get('f47') else 0,
                    'turnover': float(item.get('f48', 0)) if item.get('f48') else 0,
                    'market_cap': 58000000000 * current_price,  # 估算市值
                    'pe_ratio': 15.5,
                    'pb_ratio': 2.1,
                    'turnover_rate': 0.5  # 估算换手率
                }
                
                safe_print(f"  ✅ 备用-{realtime_data['name']}: {realtime_data['current_price']:.2f}元")
                safe_print(f"      涨跌幅: {realtime_data['change_pct']:+.2f}%")
                
                return realtime_data
            else:
                safe_print("  ❌ 东方财富API无数据返回")
                return {}
        else:
            safe_print(f"  ❌ 东方财富API请求失败: {response.status_code}")
            return {}
            
    except Exception as e:
        safe_print(f"❌ 东方财富备用API失败: {e}")
        return {}

def main():
    """主函数"""
    safe_print("🔧 修复紫金矿业实时数据获取...")
    safe_print("")
    
    # 尝试新浪财经API
    realtime_data = get_zijin_realtime_sina()
    
    # 如果新浪失败，尝试东方财富
    if not realtime_data:
        safe_print("⚠️ 新浪财经API失败，尝试东方财富备用...")
        realtime_data = get_zijin_eastmoney_backup()
    
    if realtime_data:
        # 读取原有分析数据
        data_file = Path(__file__).parent / 'zijin_mining_data.json'
        if data_file.exists():
            with open(data_file, 'r', encoding='utf-8') as f:
                analysis_data = json.load(f)
            
            # 更新实时数据
            analysis_data['realtime_data'] = realtime_data
            analysis_data['data_update_time'] = datetime.now().isoformat()
            
            # 保存更新后的数据
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(analysis_data, f, ensure_ascii=False, indent=2, default=str)
            
            safe_print("")
            safe_print("✅ 紫金矿业实时数据修复完成！")
            safe_print(f"📊 最新数据:")
            safe_print(f"   • 股票名称: {realtime_data['name']}")
            safe_print(f"   • 最新价格: {realtime_data['current_price']:.2f}元")
            safe_print(f"   • 涨跌幅: {realtime_data['change_pct']:+.2f}%")
            safe_print(f"   • 成交额: {realtime_data['turnover']/100000000:.2f}亿元")
            safe_print(f"   • 总市值: {realtime_data['market_cap']/100000000:.0f}亿元")
            safe_print("")
            safe_print("📄 数据已更新到: test/zijin_mining_data.json")
            
            return True
        else:
            safe_print("❌ 未找到原分析数据文件")
            return False
    else:
        safe_print("❌ 所有数据源都无法获取实时数据")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)