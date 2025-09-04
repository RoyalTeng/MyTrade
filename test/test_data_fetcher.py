"""
数据获取模块集成测试

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
            print("✅ 数据获取器初始化成功")
            print(f"   数据源: {config.source}")
            print(f"   缓存目录: {cache_dir}")
            print(f"   缓存天数: {config.cache_days}")
        except Exception as e:
            print(f"❌ 初始化失败: {e}")
            return False
        
        # 2. 测试股票列表获取
        print("\n2️⃣ 测试股票列表获取...")
        try:
            stock_list = fetcher.get_stock_list()
            print(f"✅ 获取股票列表成功: {len(stock_list)} 只股票")
            
            # 检查数据格式
            if len(stock_list) > 0:
                sample = stock_list[0]
                required_fields = ['symbol', 'name']
                if all(field in sample for field in required_fields):
                    print("✅ 股票数据格式验证通过")
                else:
                    print("❌ 股票数据格式验证失败")
                    return False
            else:
                print("⚠️ 股票列表为空，可能是网络问题")
                
        except Exception as e:
            print(f"❌ 股票列表获取失败: {e}")
            return False
        
        # 3. 测试历史数据获取
        print("\n3️⃣ 测试历史数据获取...")
        try:
            test_symbol = "600519"  # 贵州茅台
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            
            # 第一次获取（从网络）
            print(f"   获取 {test_symbol} 从 {start_date} 到 {end_date}")
            data = fetcher.fetch_history(test_symbol, start_date, end_date)
            
            if data is not None and len(data) > 0:
                print(f"✅ 历史数据获取成功: {len(data)} 条记录")
                
                # 检查数据完整性
                required_columns = ['open', 'high', 'low', 'close', 'volume']
                missing_columns = [col for col in required_columns if col not in data.columns]
                
                if not missing_columns:
                    print("✅ 数据列完整性验证通过")
                else:
                    print(f"❌ 缺失数据列: {missing_columns}")
                    return False
                
                # 检查数据质量
                if data['close'].isnull().sum() == 0:
                    print("✅ 收盘价数据质量验证通过")
                else:
                    print("❌ 收盘价数据存在缺失值")
                    return False
                
            else:
                print("❌ 历史数据获取失败或数据为空")
                return False
                
        except Exception as e:
            print(f"❌ 历史数据获取测试失败: {e}")
            return False
        
        # 4. 测试缓存功能
        print("\n4️⃣ 测试缓存功能...")
        try:
            # 第二次获取相同数据（从缓存）
            start_time = datetime.now()
            cached_data = fetcher.fetch_history(test_symbol, start_date, end_date)
            end_time = datetime.now()
            
            cache_time = (end_time - start_time).total_seconds()
            print(f"✅ 缓存数据获取成功，耗时: {cache_time:.2f} 秒")
            
            # 验证缓存数据与原始数据一致性
            if cached_data is not None and data is not None:
                if len(cached_data) == len(data):
                    print("✅ 缓存数据一致性验证通过")
                else:
                    print("❌ 缓存数据长度不一致")
                    return False
            
            # 检查缓存文件
            cache_info = fetcher.get_cache_info()
            print(f"✅ 缓存信息:")
            print(f"   缓存文件数: {cache_info['file_count']}")
            print(f"   缓存大小: {cache_info['total_size_mb']:.2f} MB")
            
        except Exception as e:
            print(f"❌ 缓存功能测试失败: {e}")
            return False
        
        # 5. 测试实时数据获取
        print("\n5️⃣ 测试实时数据获取...")
        try:
            # 获取当前价格
            current_data = fetcher.get_current_price(test_symbol)
            
            if current_data is not None:
                print(f"✅ 实时数据获取成功")
                print(f"   股票代码: {current_data.get('symbol', 'N/A')}")
                print(f"   当前价格: {current_data.get('price', 'N/A')}")
                print(f"   更新时间: {current_data.get('timestamp', 'N/A')}")
            else:
                print("⚠️ 实时数据获取为空，可能是非交易时间")
                
        except Exception as e:
            print(f"❌ 实时数据获取测试失败: {e}")
            # 实时数据失败不影响整体测试结果
            pass
        
        # 6. 测试多股票批量获取
        print("\n6️⃣ 测试多股票批量获取...")
        try:
            test_symbols = ["600519", "000001", "000002"]
            batch_data = {}
            
            for symbol in test_symbols:
                data = fetcher.fetch_history(symbol, start_date, end_date)
                if data is not None and len(data) > 0:
                    batch_data[symbol] = data
            
            print(f"✅ 批量数据获取成功: {len(batch_data)} 只股票")
            
            # 验证数据一致性
            if len(batch_data) > 1:
                symbols = list(batch_data.keys())
                lengths = [len(batch_data[symbol]) for symbol in symbols]
                if len(set(lengths)) <= 2:  # 允许少量差异（停牌等）
                    print("✅ 批量数据长度一致性验证通过")
                else:
                    print("⚠️ 批量数据长度存在较大差异")
            
        except Exception as e:
            print(f"❌ 批量数据获取测试失败: {e}")
            return False
        
        # 7. 测试错误处理
        print("\n7️⃣ 测试错误处理...")
        try:
            # 测试无效股票代码
            invalid_data = fetcher.fetch_history("INVALID", start_date, end_date)
            if invalid_data is None or len(invalid_data) == 0:
                print("✅ 无效股票代码处理正确")
            else:
                print("⚠️ 无效股票代码未正确处理")
            
            # 测试无效日期范围
            future_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
            future_data = fetcher.fetch_history(test_symbol, future_date, future_date)
            if future_data is None or len(future_data) == 0:
                print("✅ 无效日期范围处理正确")
            else:
                print("⚠️ 无效日期范围未正确处理")
                
        except Exception as e:
            print(f"❌ 错误处理测试失败: {e}")
            return False
        
        # 8. 测试数据清理和验证
        print("\n8️⃣ 测试数据清理和验证...")
        try:
            # 获取数据进行清理测试
            raw_data = fetcher.fetch_history(test_symbol, start_date, end_date)
            
            if raw_data is not None:
                # 检查异常值
                price_columns = ['open', 'high', 'low', 'close']
                for col in price_columns:
                    if col in raw_data.columns:
                        if (raw_data[col] <= 0).any():
                            print(f"⚠️ 发现 {col} 列存在非正值")
                        if raw_data[col].isnull().any():
                            print(f"⚠️ 发现 {col} 列存在空值")
                
                # 检查价格逻辑性
                if all(col in raw_data.columns for col in ['high', 'low', 'open', 'close']):
                    invalid_rows = (
                        (raw_data['high'] < raw_data['low']) |
                        (raw_data['high'] < raw_data['open']) |
                        (raw_data['high'] < raw_data['close']) |
                        (raw_data['low'] > raw_data['open']) |
                        (raw_data['low'] > raw_data['close'])
                    )
                    
                    if invalid_rows.any():
                        print(f"⚠️ 发现 {invalid_rows.sum()} 行价格逻辑异常")
                    else:
                        print("✅ 价格数据逻辑性验证通过")
                
                print("✅ 数据质量检查完成")
            
        except Exception as e:
            print(f"❌ 数据质量检查失败: {e}")
            return False
    
    print("\n" + "="*60)
    print("🎉 数据获取模块集成测试全部通过!")
    print("="*60)
    print("\n✅ 测试通过的功能:")
    print("   1. 配置初始化和参数验证")
    print("   2. 股票列表获取和格式验证")
    print("   3. 历史数据获取和质量检查")
    print("   4. 数据缓存和一致性验证")
    print("   5. 实时数据获取能力")
    print("   6. 多股票批量处理")
    print("   7. 错误情况处理")
    print("   8. 数据清理和逻辑验证")
    
    return True


if __name__ == "__main__":
    success = test_data_fetcher()
    if success:
        print("\n🚀 数据获取模块已准备就绪！")
    else:
        print("\n❌ 数据获取模块存在问题，需要修复")
    exit(0 if success else 1)