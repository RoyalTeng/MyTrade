"""
数据获取模块集成测试 - 清理版本

测试数据获取功能、缓存机制和数据质量。
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


def test_data_fetcher():
    """数据获取模块集成测试"""
    print("="*60)
    print("           数据获取模块集成测试")
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
            print("PASS: 数据获取器初始化成功")
            print(f"   数据源: {config.source}")
            print(f"   缓存目录: {cache_dir}")
            print(f"   缓存天数: {config.cache_days}")
        except Exception as e:
            print(f"FAIL: 初始化失败: {e}")
            return False
        
        # 2. 测试股票列表获取
        print("\n2. 测试股票列表获取...")
        try:
            stock_list = fetcher.get_stock_list()
            print(f"PASS: 获取股票列表成功: {len(stock_list)} 只股票")
            
            # 检查数据格式
            if len(stock_list) > 0:
                sample = stock_list[0]
                required_fields = ['symbol', 'name']
                if all(field in sample for field in required_fields):
                    print("PASS: 股票数据格式验证通过")
                else:
                    print("FAIL: 股票数据格式验证失败")
                    return False
            else:
                print("WARN: 股票列表为空，可能是网络问题")
                
        except Exception as e:
            print(f"FAIL: 股票列表获取失败: {e}")
            return False
        
        # 3. 测试历史数据获取
        print("\n3. 测试历史数据获取...")
        try:
            test_symbol = "600519"  # 贵州茅台
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            
            # 第一次获取（从网络）
            print(f"   获取 {test_symbol} 从 {start_date} 到 {end_date}")
            data = fetcher.fetch_history(test_symbol, start_date, end_date)
            
            if data is not None and len(data) > 0:
                print(f"PASS: 历史数据获取成功: {len(data)} 条记录")
                
                # 检查数据完整性
                required_columns = ['open', 'high', 'low', 'close', 'volume']
                missing_columns = [col for col in required_columns if col not in data.columns]
                
                if not missing_columns:
                    print("PASS: 数据列完整性验证通过")
                else:
                    print(f"FAIL: 缺失数据列: {missing_columns}")
                    return False
                
                # 检查数据质量
                if data['close'].isnull().sum() == 0:
                    print("PASS: 收盘价数据质量验证通过")
                else:
                    print("FAIL: 收盘价数据存在缺失值")
                    return False
                
            else:
                print("FAIL: 历史数据获取失败或数据为空")
                return False
                
        except Exception as e:
            print(f"FAIL: 历史数据获取测试失败: {e}")
            return False
        
        # 4. 测试缓存功能
        print("\n4. 测试缓存功能...")
        try:
            # 第二次获取相同数据（从缓存）
            start_time = datetime.now()
            cached_data = fetcher.fetch_history(test_symbol, start_date, end_date)
            end_time = datetime.now()
            
            cache_time = (end_time - start_time).total_seconds()
            print(f"PASS: 缓存数据获取成功，耗时: {cache_time:.2f} 秒")
            
            # 验证缓存数据与原始数据一致性
            if cached_data is not None and data is not None:
                if len(cached_data) == len(data):
                    print("PASS: 缓存数据一致性验证通过")
                else:
                    print("FAIL: 缓存数据长度不一致")
                    return False
            
            # 检查缓存文件
            cache_info = fetcher.get_cache_info()
            print(f"PASS: 缓存信息:")
            print(f"   缓存文件数: {cache_info['file_count']}")
            print(f"   缓存大小: {cache_info['total_size_mb']:.2f} MB")
            
        except Exception as e:
            print(f"FAIL: 缓存功能测试失败: {e}")
            return False
    
    print("\n" + "="*60)
    print("PASS: 数据获取模块集成测试全部通过!")
    print("="*60)
    
    return True


if __name__ == "__main__":
    success = test_data_fetcher()
    if success:
        print("\n数据获取模块已准备就绪！")
    else:
        print("\n数据获取模块存在问题，需要修复")
    exit(0 if success else 1)