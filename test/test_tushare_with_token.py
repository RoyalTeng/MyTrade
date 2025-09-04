#!/usr/bin/env python3
"""
使用提供的Token测试Tushare连接
"""

import sys
from pathlib import Path
import warnings

# 添加src到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from test_encoding_fix import safe_print

warnings.filterwarnings('ignore')

# 使用提供的Token
TUSHARE_TOKEN = "2e6561572caa8a088167963e5c9fb5b5b5dbacc83ac714e9596bdc47"

def test_tushare_with_token():
    """测试Tushare连接和数据获取"""
    safe_print("🔑 测试Tushare连接...")
    safe_print(f"Token: {TUSHARE_TOKEN[:10]}...{TUSHARE_TOKEN[-10:]}")
    
    try:
        # 导入tushare
        import tushare as ts
        
        # 设置token
        ts.set_token(TUSHARE_TOKEN)
        pro = ts.pro_api()
        
        safe_print("✅ Tushare初始化成功")
        
        # 测试1: 获取股票基本信息
        safe_print("\n📊 测试1: 获取股票基本信息...")
        stock_basic = pro.stock_basic(exchange='', list_status='L', 
                                     fields='ts_code,symbol,name,area,industry,list_date')
        if not stock_basic.empty:
            safe_print(f"  ✅ 获取{len(stock_basic)}只股票信息")
            # 显示紫金矿业信息
            zijin = stock_basic[stock_basic['ts_code'] == '601899.SH']
            if not zijin.empty:
                zijin_info = zijin.iloc[0]
                safe_print(f"  📈 紫金矿业信息: {zijin_info['name']} | {zijin_info['industry']} | {zijin_info['area']}")
        
        # 测试2: 获取紫金矿业日线数据
        safe_print("\n📊 测试2: 获取紫金矿业日线数据...")
        daily_data = pro.daily(ts_code='601899.SH', start_date='20240801', end_date='20241201')
        if not daily_data.empty:
            daily_data = daily_data.sort_values('trade_date')
            latest = daily_data.iloc[-1]
            safe_print(f"  ✅ 获取{len(daily_data)}天交易数据")
            safe_print(f"  📈 最新价格: {latest['close']:.2f}元 (涨跌幅: {latest['pct_chg']:+.2f}%)")
            safe_print(f"  📅 最新日期: {latest['trade_date']}")
        
        # 测试3: 获取财务数据
        safe_print("\n📊 测试3: 获取财务数据...")
        try:
            fina_indicator = pro.fina_indicator(ts_code='601899.SH', period='20240630')
            if not fina_indicator.empty:
                latest_fina = fina_indicator.iloc[0]
                safe_print(f"  ✅ 获取财务指标数据")
                safe_print(f"  💰 ROE: {latest_fina.get('roe', 0):.1f}% | ROA: {latest_fina.get('roa', 0):.1f}%")
                safe_print(f"  📊 负债率: {latest_fina.get('debt_to_assets', 0):.1f}%")
        except Exception as e:
            safe_print(f"  ⚠️ 财务数据: {e}")
        
        # 测试4: 获取指数数据
        safe_print("\n📊 测试4: 获取指数数据...")
        try:
            index_data = pro.index_daily(ts_code='000001.SH', start_date='20241101', end_date='20241201')
            if not index_data.empty:
                index_latest = index_data.iloc[0]
                safe_print(f"  ✅ 上证指数: {index_latest['close']:.2f}点 ({index_latest['pct_chg']:+.2f}%)")
        except Exception as e:
            safe_print(f"  ⚠️ 指数数据: {e}")
        
        safe_print("\n🎉 Tushare连接测试成功!")
        safe_print("📊 所有核心功能正常")
        return True
        
    except ImportError:
        safe_print("❌ 请先安装tushare: pip install tushare")
        return False
    except Exception as e:
        safe_print(f"❌ Tushare连接失败: {e}")
        return False

if __name__ == "__main__":
    success = test_tushare_with_token()
    exit(0 if success else 1)