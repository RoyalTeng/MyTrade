#!/usr/bin/env python3
"""
统一数据源管理器

支持多种数据源：Akshare、Tushare、东方财富API等
自动切换和备用数据源机制
"""

import sys
import os
import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import warnings

# 添加src到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from test_encoding_fix import safe_print

warnings.filterwarnings('ignore')


class UnifiedDataSource:
    """统一数据源管理器"""
    
    def __init__(self, tushare_token=None):
        self.tushare_token = tushare_token or os.environ.get('TUSHARE_TOKEN')
        self.data_sources = {}
        self.active_sources = []
        
        safe_print("🔧 初始化统一数据源管理器...")
        self.init_all_sources()
    
    def init_all_sources(self):
        """初始化所有数据源"""
        
        # 1. 初始化Akshare
        try:
            import akshare as ak
            self.data_sources['akshare'] = ak
            self.active_sources.append('akshare')
            safe_print("  ✅ Akshare - 已激活")
        except ImportError:
            safe_print("  ❌ Akshare - 未安装")
        
        # 2. 初始化Tushare
        try:
            import tushare as ts
            if self.tushare_token:
                ts.set_token(self.tushare_token)
                self.data_sources['tushare'] = ts.pro_api()
                self.active_sources.append('tushare')
                safe_print("  ✅ Tushare - 已激活")
            else:
                safe_print("  ⚠️ Tushare - 需要API Token")
        except ImportError:
            safe_print("  ❌ Tushare - 未安装")
        
        # 3. 初始化requests (用于API调用)
        try:
            import requests
            self.data_sources['requests'] = requests
            self.active_sources.append('api_requests')
            safe_print("  ✅ API Requests - 已激活")
        except ImportError:
            safe_print("  ❌ Requests - 未安装")
        
        safe_print(f"📊 可用数据源: {', '.join(self.active_sources)}")
    
    def get_stock_realtime(self, symbol, source='auto'):
        """获取股票实时数据（多源自动切换）"""
        safe_print(f"📈 获取{symbol}实时数据...")
        
        if source == 'auto':
            # 按优先级尝试不同数据源
            sources_to_try = ['tushare', 'akshare', 'sina_api', 'eastmoney_api']
        else:
            sources_to_try = [source]
        
        for src in sources_to_try:
            if src not in self.active_sources and src != 'sina_api' and src != 'eastmoney_api':
                continue
                
            try:
                if src == 'tushare':
                    return self._get_tushare_realtime(symbol)
                elif src == 'akshare':
                    return self._get_akshare_realtime(symbol)
                elif src == 'sina_api':
                    return self._get_sina_realtime(symbol)
                elif src == 'eastmoney_api':
                    return self._get_eastmoney_realtime(symbol)
                    
            except Exception as e:
                safe_print(f"  ⚠️ {src}数据源失败: {e}")
                continue
        
        safe_print("❌ 所有数据源都无法获取实时数据")
        return {}
    
    def _get_tushare_realtime(self, symbol):
        """Tushare实时数据"""
        if 'tushare' not in self.data_sources:
            raise Exception("Tushare未初始化")
        
        # 转换股票代码格式 (601899 -> 601899.SH)
        ts_code = self._convert_to_tushare_code(symbol)
        pro = self.data_sources['tushare']
        
        # 获取最新交易日数据
        df = pro.daily(ts_code=ts_code, start_date='', end_date='')
        if df.empty:
            raise Exception("无数据返回")
        
        # 取最新一天数据
        latest = df.iloc[0]
        
        realtime_data = {
            'symbol': symbol,
            'name': self._get_stock_name_tushare(ts_code),
            'current_price': float(latest['close']),
            'change': float(latest['change']),
            'change_pct': float(latest['pct_chg']),
            'open': float(latest['open']),
            'high': float(latest['high']),
            'low': float(latest['low']),
            'prev_close': float(latest['pre_close']),
            'volume': int(latest['vol'] * 100),  # Tushare单位是手
            'turnover': float(latest['amount'] * 1000),  # Tushare单位是千元
            'trade_date': str(latest['trade_date']),
            'source': 'tushare'
        }
        
        safe_print(f"  ✅ Tushare: {realtime_data['name']} {realtime_data['current_price']:.2f}元")
        return realtime_data
    
    def _get_akshare_realtime(self, symbol):
        """Akshare实时数据"""
        if 'akshare' not in self.data_sources:
            raise Exception("Akshare未初始化")
        
        ak = self.data_sources['akshare']
        
        # 获取实时行情
        stock_spot = ak.stock_zh_a_spot_em()
        stock_info = stock_spot[stock_spot['代码'] == symbol]
        
        if stock_info.empty:
            raise Exception("未找到股票数据")
        
        row = stock_info.iloc[0]
        
        realtime_data = {
            'symbol': symbol,
            'name': str(row.get('名称', '')),
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
            'source': 'akshare'
        }
        
        safe_print(f"  ✅ Akshare: {realtime_data['name']} {realtime_data['current_price']:.2f}元")
        return realtime_data
    
    def _get_sina_realtime(self, symbol):
        """新浪财经API实时数据"""
        if 'api_requests' not in self.active_sources:
            raise Exception("Requests未可用")
        
        requests = self.data_sources['requests']
        
        # 转换代码格式
        if symbol.startswith('60'):
            sina_code = f"sh{symbol}"
        else:
            sina_code = f"sz{symbol}"
        
        url = f"https://hq.sinajs.cn/list={sina_code}"
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            raise Exception(f"请求失败: {response.status_code}")
        
        data_str = response.text.strip()
        if 'var hq_str_' not in data_str:
            raise Exception("数据格式错误")
        
        # 解析数据
        data_part = data_str.split('="')[1].split('";')[0]
        fields = data_part.split(',')
        
        if len(fields) < 30:
            raise Exception("数据字段不足")
        
        current_price = float(fields[3])
        prev_close = float(fields[2])
        
        realtime_data = {
            'symbol': symbol,
            'name': fields[0],
            'current_price': current_price,
            'prev_close': prev_close,
            'change': current_price - prev_close,
            'change_pct': ((current_price - prev_close) / prev_close * 100) if prev_close > 0 else 0,
            'open': float(fields[1]),
            'high': float(fields[4]),
            'low': float(fields[5]),
            'volume': int(float(fields[8])),
            'turnover': float(fields[9]),
            'source': 'sina_api'
        }
        
        safe_print(f"  ✅ 新浪API: {realtime_data['name']} {realtime_data['current_price']:.2f}元")
        return realtime_data
    
    def _get_eastmoney_realtime(self, symbol):
        """东方财富API实时数据"""
        if 'api_requests' not in self.active_sources:
            raise Exception("Requests未可用")
        
        requests = self.data_sources['requests']
        
        # 东方财富代码格式
        if symbol.startswith('60'):
            secid = f"1.{symbol}"
        else:
            secid = f"0.{symbol}"
        
        url = "http://push2.eastmoney.com/api/qt/stock/get"
        params = {
            'ut': 'fa5fd1943c7b386f172d6893dbfba10b',
            'invt': '2',
            'fltt': '2',
            'secid': secid,
            'fields': 'f43,f44,f45,f46,f47,f48,f49,f169,f170,f57,f58'
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code != 200:
            raise Exception(f"请求失败: {response.status_code}")
        
        data = response.json()
        if 'data' not in data or not data['data']:
            raise Exception("无数据返回")
        
        item = data['data']
        current_price = float(item.get('f43', 0)) / 100
        prev_close = float(item.get('f60', current_price)) / 100
        
        realtime_data = {
            'symbol': symbol,
            'name': f"股票{symbol}",  # 东方财富API可能需要额外接口获取名称
            'current_price': current_price,
            'prev_close': prev_close,
            'change': float(item.get('f169', 0)) / 100,
            'change_pct': float(item.get('f170', 0)) / 100,
            'open': float(item.get('f46', 0)) / 100,
            'high': float(item.get('f44', 0)) / 100,
            'low': float(item.get('f45', 0)) / 100,
            'volume': int(item.get('f47', 0)),
            'turnover': float(item.get('f48', 0)),
            'source': 'eastmoney_api'
        }
        
        safe_print(f"  ✅ 东财API: {realtime_data['name']} {realtime_data['current_price']:.2f}元")
        return realtime_data
    
    def get_historical_data(self, symbol, days=120, source='auto'):
        """获取历史数据（多源支持）"""
        safe_print(f"📊 获取{symbol}历史数据({days}天)...")
        
        if source == 'auto':
            sources_to_try = ['tushare', 'akshare']
        else:
            sources_to_try = [source]
        
        for src in sources_to_try:
            if src not in self.active_sources:
                continue
                
            try:
                if src == 'tushare':
                    return self._get_tushare_historical(symbol, days)
                elif src == 'akshare':
                    return self._get_akshare_historical(symbol, days)
                    
            except Exception as e:
                safe_print(f"  ⚠️ {src}数据源失败: {e}")
                continue
        
        safe_print("❌ 无法获取历史数据")
        return pd.DataFrame(), {}
    
    def _get_tushare_historical(self, symbol, days):
        """Tushare历史数据"""
        pro = self.data_sources['tushare']
        ts_code = self._convert_to_tushare_code(symbol)
        
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
        
        df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
        
        if df.empty:
            raise Exception("无历史数据")
        
        # 按日期排序
        df = df.sort_values('trade_date')
        
        # 计算技术指标
        indicators = self._calculate_indicators(df, 'tushare')
        
        safe_print(f"  ✅ Tushare历史数据: {len(df)}天")
        return df, indicators
    
    def _get_akshare_historical(self, symbol, days):
        """Akshare历史数据"""
        ak = self.data_sources['akshare']
        
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
        
        df = ak.stock_zh_a_hist(symbol=symbol, start_date=start_date, end_date=end_date, adjust="qfq")
        
        if df.empty:
            raise Exception("无历史数据")
        
        # 计算技术指标
        indicators = self._calculate_indicators(df, 'akshare')
        
        safe_print(f"  ✅ Akshare历史数据: {len(df)}天")
        return df, indicators
    
    def _calculate_indicators(self, df, source_type):
        """计算技术指标"""
        if df.empty:
            return {}
        
        # 根据数据源类型选择字段名
        if source_type == 'tushare':
            close_col = 'close'
            vol_col = 'vol'
        else:  # akshare
            close_col = '收盘'
            vol_col = '成交量'
        
        closes = df[close_col].values
        volumes = df[vol_col].values
        
        indicators = {
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
            'current_price': float(closes[-1]) if len(closes) > 0 else 0,
        }
        
        return indicators
    
    def _convert_to_tushare_code(self, symbol):
        """转换为Tushare代码格式"""
        if symbol.startswith('60'):
            return f"{symbol}.SH"
        elif symbol.startswith('00') or symbol.startswith('30'):
            return f"{symbol}.SZ"
        else:
            return symbol
    
    def _get_stock_name_tushare(self, ts_code):
        """从Tushare获取股票名称"""
        try:
            pro = self.data_sources['tushare']
            basic = pro.stock_basic(ts_code=ts_code)
            if not basic.empty:
                return basic.iloc[0]['name']
            return ts_code
        except:
            return ts_code
    
    def get_data_source_status(self):
        """获取数据源状态"""
        status = {
            'active_sources': self.active_sources,
            'total_sources': len(self.data_sources),
            'tushare_available': 'tushare' in self.active_sources,
            'akshare_available': 'akshare' in self.active_sources,
            'api_available': 'api_requests' in self.active_sources
        }
        
        return status


def demo_unified_data_source():
    """演示统一数据源使用"""
    safe_print("🎯 统一数据源使用演示")
    safe_print("=" * 50)
    
    # 创建数据源管理器
    data_source = UnifiedDataSource()
    
    # 显示状态
    status = data_source.get_data_source_status()
    safe_print(f"📊 数据源状态: {status}")
    safe_print("")
    
    # 测试获取紫金矿业数据
    symbol = '601899'
    
    # 获取实时数据
    realtime_data = data_source.get_stock_realtime(symbol)
    if realtime_data:
        safe_print("📈 实时数据获取成功:")
        safe_print(f"   股票名称: {realtime_data.get('name', 'N/A')}")
        safe_print(f"   当前价格: {realtime_data.get('current_price', 0):.2f}元")
        safe_print(f"   涨跌幅: {realtime_data.get('change_pct', 0):+.2f}%")
        safe_print(f"   数据源: {realtime_data.get('source', 'unknown')}")
    
    # 获取历史数据
    hist_data, indicators = data_source.get_historical_data(symbol, days=30)
    if not hist_data.empty and indicators:
        safe_print("")
        safe_print("📊 历史数据获取成功:")
        safe_print(f"   数据天数: {len(hist_data)}天")
        safe_print(f"   MA20: {indicators.get('ma20', 0):.2f}元")
        safe_print(f"   MA60: {indicators.get('ma60', 0):.2f}元")
        safe_print(f"   波动率: {indicators.get('volatility', 0):.2f}")
    
    safe_print("")
    safe_print("✅ 统一数据源演示完成")


if __name__ == "__main__":
    demo_unified_data_source()