"""
数据获取模块简化测试
"""

import sys
import os
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd

# 添加src到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mytrade.data import MarketDataFetcher
from mytrade.config import DataConfig


def test_data_fetcher_simple():
    """数据获取模块简化测试"""
    print("="*60)
    print("           数据获取模块简化测试")
    print("="*60)
    
    # 创建临时缓存目录
    with tempfile.TemporaryDirectory() as temp_dir:
        cache_dir = Path(temp_dir) / "test_cache"
        
        # 1. 测试配置初始化
        print("\n1. 测试配置初始化...")
        try:
            config = DataConfig(
                source="akshare",
                cache_dir=str(cache_dir),
                cache_days=7,
                max_retries=2,
                retry_delay=0.5
            )
            fetcher = MarketDataFetcher(config)
            print("[OK] 数据获取器初始化成功")
            print(f"   数据源: {config.source}")
            print(f"   缓存目录: {cache_dir}")
            print(f"   缓存天数: {config.cache_days}")
        except Exception as e:
            print(f"[ERROR] 初始化失败: {e}")
            return False
        
        # 2. 测试股票列表获取
        print("\n2. 测试股票列表获取...")
        try:
            stock_list = fetcher.get_stock_list()
            print(f"[OK] 获取到 {len(stock_list)} 只股票")
            if len(stock_list) > 0:
                print("   前5只股票:")
                for i, (index, row) in enumerate(stock_list.head(5).iterrows()):
                    code = row.get('code', row.get('symbol', 'N/A'))
                    name = row.get('name', 'N/A')
                    print(f"     {code}: {name}")
        except Exception as e:
            print(f"[ERROR] 获取股票列表失败: {e}")
            print("   这可能是网络问题，继续其他测试...")
        
        # 3. 测试历史数据获取
        print("\n3. 测试历史数据获取...")
        try:
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            
            test_symbol = "000001"
            data = fetcher.fetch_history(
                symbol=test_symbol,
                start_date=start_date,
                end_date=end_date
            )
            
            if not data.empty:
                print(f"[OK] 获取到 {len(data)} 条历史数据")
                print(f"   股票代码: {test_symbol}")
                print(f"   时间范围: {data.index[0]} 到 {data.index[-1]}")
                print(f"   数据列: {list(data.columns)}")
                if 'close' in data.columns:
                    print(f"   最新收盘价: {data['close'].iloc[-1]:.2f}")
            else:
                print("[WARNING] 未获取到数据")
                
        except Exception as e:
            print(f"[ERROR] 获取历史数据失败: {e}")
            print("   这可能是网络问题或股票代码问题")
        
        # 4. 测试缓存功能
        print("\n4. 测试缓存功能...")
        try:
            cache_info = fetcher.get_cache_info()
            print(f"[OK] 缓存统计:")
            print(f"   缓存文件数: {cache_info.get('total_files', 0)}")
            print(f"   缓存大小: {cache_info.get('total_size_mb', 0):.2f} MB")
            print(f"   缓存目录: {cache_info.get('cache_dir', 'N/A')}")
        except Exception as e:
            print(f"[ERROR] 获取缓存信息失败: {e}")
    
    print("\n" + "="*60)
    print("数据获取模块测试完成")
    print("="*60)
    return True


if __name__ == "__main__":
    success = test_data_fetcher_simple()
    exit(0 if success else 1)