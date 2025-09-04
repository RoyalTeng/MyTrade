"""
测试行情数据采集模块
"""

import sys
import logging
from pathlib import Path

# 添加src到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mytrade.data import MarketDataFetcher
from mytrade.data.market_data_fetcher import DataSourceConfig


def test_market_data_fetcher():
    """测试数据采集功能"""
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 配置数据源
    config = DataSourceConfig(
        source="akshare",
        cache_dir=Path("../data/cache")
    )
    
    # 创建数据采集器
    fetcher = MarketDataFetcher(config)
    
    print("=== 测试数据采集功能 ===")
    
    # 测试获取贵州茅台历史数据
    try:
        print("1. 获取贵州茅台(600519)最近5天数据...")
        data = fetcher.fetch_recent("600519", days=5)
        print(f"获取成功! 数据形状: {data.shape}")
        print(f"日期范围: {data.index[0]} 到 {data.index[-1]}")
        print("前3行数据:")
        print(data.head(3))
        print()
    except Exception as e:
        print(f"获取失败: {e}")
        print()
    
    # 测试获取指定时间范围的数据
    try:
        print("2. 获取平安银行(000001)指定时间范围数据...")
        data = fetcher.fetch_history(
            symbol="000001",
            start_date="2024-01-01", 
            end_date="2024-01-31"
        )
        print(f"获取成功! 数据形状: {data.shape}")
        print("数据统计:")
        print(data.describe())
        print()
    except Exception as e:
        print(f"获取失败: {e}")
        print()
    
    # 测试缓存功能
    try:
        print("3. 测试缓存功能...")
        # 第一次获取（从网络）
        start_time = time.time()
        data1 = fetcher.fetch_recent("600519", days=3)
        time1 = time.time() - start_time
        
        # 第二次获取（从缓存）
        start_time = time.time()
        data2 = fetcher.fetch_recent("600519", days=3)
        time2 = time.time() - start_time
        
        print(f"第一次获取耗时: {time1:.2f}秒")
        print(f"第二次获取耗时: {time2:.2f}秒")
        print(f"数据一致性: {data1.equals(data2)}")
        print()
    except Exception as e:
        print(f"缓存测试失败: {e}")
        print()
    
    # 获取缓存信息
    try:
        print("4. 缓存信息:")
        cache_info = fetcher.get_cache_info()
        for key, value in cache_info.items():
            print(f"  {key}: {value}")
        print()
    except Exception as e:
        print(f"获取缓存信息失败: {e}")


if __name__ == "__main__":
    import time
    test_market_data_fetcher()