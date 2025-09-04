"""
前视泄漏防护机制测试

验证时间完整性保护系统的各项功能
"""

import sys
from pathlib import Path
from datetime import datetime, date, timedelta
from decimal import Decimal

# 添加src到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mytrade.core.temporal_guard import (
    TemporalViolationType, TemporalViolation, TemporalContext,
    TemporalGuard, PointInTimeDataAccess, RollingWindowGuard,
    create_temporal_guard, create_point_in_time_access
)
from mytrade.data.schemas import MarketDataPoint, TradingSignal, SignalType, DataSource
from mytrade.data.trading_calendar import create_ashare_calendar


def test_temporal_context():
    """测试时间上下文"""
    print("="*60)
    print("           时间上下文测试")
    print("="*60)
    
    try:
        # 1. 创建时间上下文
        print("\n1. 创建时间上下文...")
        
        current_time = datetime(2024, 9, 4, 10, 30, 0)
        context = TemporalContext(
            current_time=current_time,
            simulation_mode=True,
            max_lookback_days=30,
            strict_mode=True
        )
        
        print(f"[OK] 时间上下文创建成功")
        print(f"   当前时间: {context.current_time}")
        print(f"   模拟模式: {context.simulation_mode}")
        print(f"   最大回看: {context.max_lookback_days} 天")
        print(f"   严格模式: {context.strict_mode}")
        
        # 2. 测试时间边界计算
        print("\n2. 测试时间边界计算...")
        
        earliest = context.get_earliest_allowed()
        latest = context.get_latest_allowed()
        
        print(f"[OK] 时间边界计算成功")
        print(f"   最早允许: {earliest}")
        print(f"   最晚允许: {latest}")
        print(f"   时间跨度: {(latest - earliest).days} 天")
        
        # 3. 测试时间推进
        print("\n3. 测试时间推进...")
        
        new_time = current_time + timedelta(hours=1)
        context.update_current_time(new_time)
        
        print(f"[OK] 时间推进成功")
        print(f"   新时间: {context.current_time}")
        print(f"   违规记录: {len(context.violations)} 条")
        
        # 4. 测试时间倒退检测
        print("\n4. 测试时间倒退检测...")
        
        try:
            backward_time = current_time - timedelta(minutes=30)
            context.update_current_time(backward_time)
            print("[ERROR] 时间倒退应该被检测到")
        except ValueError as e:
            print(f"[OK] 时间倒退检测成功: {e}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] 时间上下文测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_temporal_guard_basic():
    """测试时间防护基础功能"""
    print("\n" + "="*60)
    print("           时间防护基础测试")
    print("="*60)
    
    try:
        # 1. 创建时间防护
        print("\n1. 创建时间防护...")
        
        calendar = create_ashare_calendar()
        guard = create_temporal_guard(calendar)
        
        print(f"[OK] 时间防护创建成功")
        
        # 2. 测试时间作用域
        print("\n2. 测试时间作用域...")
        
        base_time = datetime(2024, 9, 4, 10, 30, 0)
        
        with guard.temporal_scope(
            current_time=base_time,
            simulation_mode=True,
            max_lookback_days=60,
            strict_mode=False  # 使用非严格模式便于测试
        ) as context:
            print(f"[OK] 进入时间作用域")
            print(f"   当前时间: {context.current_time}")
            print(f"   最大回看: {context.max_lookback_days} 天")
            
            # 3. 测试数据时间戳验证
            print("\n3. 测试数据时间戳验证...")
            
            # 有效时间戳（过去数据）
            valid_timestamp = base_time - timedelta(days=10)
            is_valid = guard.validate_data_timestamp(valid_timestamp, "market_data")
            print(f"   有效时间戳 ({valid_timestamp}): {'通过' if is_valid else '拒绝'}")
            
            # 无效时间戳（未来数据）
            future_timestamp = base_time + timedelta(hours=1)
            is_valid = guard.validate_data_timestamp(future_timestamp, "market_data")
            print(f"   未来时间戳 ({future_timestamp}): {'通过' if is_valid else '拒绝'}")
            
            # 超出回看期
            old_timestamp = base_time - timedelta(days=100)
            is_valid = guard.validate_data_timestamp(old_timestamp, "market_data")
            print(f"   超期时间戳 ({old_timestamp}): {'通过' if is_valid else '拒绝'}")
            
            # 4. 测试违规统计
            print("\n4. 测试违规统计...")
            
            summary = guard.get_violation_summary()
            print(f"[OK] 违规统计生成成功")
            print(f"   总违规数: {summary['total_violations']}")
            print(f"   按类型统计: {summary['violations_by_type']}")
            print(f"   按严重程度: {summary['violations_by_severity']}")
        
        print(f"[OK] 退出时间作用域")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] 时间防护基础测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_point_in_time_access():
    """测试时间点数据访问"""
    print("\n" + "="*60)
    print("           时间点数据访问测试")
    print("="*60)
    
    try:
        # 1. 创建数据访问控制器
        print("\n1. 创建数据访问控制器...")
        
        guard = create_temporal_guard()
        data_access = create_point_in_time_access(guard)
        
        print(f"[OK] 数据访问控制器创建成功")
        
        # 2. 测试市场数据获取
        print("\n2. 测试市场数据获取...")
        
        query_time = datetime(2024, 9, 4, 14, 30, 0)
        
        with guard.temporal_scope(query_time, strict_mode=False) as context:
            
            market_data = data_access.get_market_data(
                symbol="000001",
                end_time=query_time,
                lookback_periods=20
            )
            
            print(f"[OK] 市场数据获取成功")
            print(f"   股票代码: 000001")
            print(f"   查询时间: {query_time}")
            print(f"   数据条数: {len(market_data)}")
            
            if market_data:
                first_data = market_data[0]
                last_data = market_data[-1]
                print(f"   时间范围: {first_data.timestamp} 至 {last_data.timestamp}")
                print(f"   最新价格: {last_data.close_price}")
        
        # 3. 测试交易信号验证
        print("\n3. 测试交易信号验证...")
        
        signal = TradingSignal(
            signal_id="test_signal_001",
            symbol="000001",
            timestamp=query_time,
            signal_type=SignalType.BUY,
            strength=0.75,
            confidence=0.82,
            valid_from=query_time,
            valid_until=query_time + timedelta(hours=2),
            agent_id="test_agent",
            agent_type="TestAgent",
            reasoning="测试信号"
        )
        
        with guard.temporal_scope(query_time, strict_mode=False) as context:
            is_valid = data_access.validate_signal_timing(signal)
            
            print(f"[OK] 交易信号验证完成")
            print(f"   信号ID: {signal.signal_id}")
            print(f"   验证结果: {'通过' if is_valid else '拒绝'}")
            print(f"   生成时间: {signal.timestamp}")
            print(f"   有效期至: {signal.valid_until}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] 时间点数据访问测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_rolling_window_protection():
    """测试滚动窗口防护"""
    print("\n" + "="*60)
    print("           滚动窗口防护测试")
    print("="*60)
    
    try:
        # 1. 创建滚动窗口防护
        print("\n1. 创建滚动窗口防护...")
        
        guard = create_temporal_guard()
        window_guard = RollingWindowGuard(guard)
        
        print(f"[OK] 滚动窗口防护创建成功")
        
        # 2. 创建滚动窗口
        print("\n2. 创建滚动窗口...")
        
        window = window_guard.create_rolling_window(
            window_id="ma_5",
            window_size=5,
            min_periods=3
        )
        
        print(f"[OK] 滚动窗口创建成功")
        print(f"   窗口ID: {window.window_id}")
        print(f"   窗口大小: {window.window_size}")
        print(f"   最小期数: {window.min_periods}")
        
        # 3. 测试数据添加
        print("\n3. 测试数据添加...")
        
        base_time = datetime(2024, 9, 4, 10, 0, 0)
        
        with guard.temporal_scope(base_time + timedelta(hours=2), strict_mode=False) as context:
            
            # 添加历史数据点
            prices = [11.50, 11.65, 11.80, 11.75, 11.90]
            
            for i, price in enumerate(prices):
                data_point = {'price': price, 'volume': 1000000}
                timestamp = base_time + timedelta(minutes=i*30)
                
                window.add_data_point(data_point, timestamp)
                
                window_info = window.get_window_info()
                print(f"   数据点 {i+1}: 价格={price}, 时间={timestamp.strftime('%H:%M')}, 窗口大小={window_info['current_size']}")
            
            # 4. 测试窗口计算
            print("\n4. 测试窗口计算...")
            
            # 计算移动平均
            def calculate_ma(data_buffer):
                return sum(d['price'] for d in data_buffer) / len(data_buffer)
            
            ma_result = window.calculate(calculate_ma)
            
            print(f"[OK] 滚动窗口计算完成")
            print(f"   移动平均: {ma_result:.2f}")
            
            window_info = window.get_window_info()
            print(f"   窗口状态: {'就绪' if window_info['is_ready'] else '未就绪'}")
            print(f"   数据范围: {window_info['earliest_timestamp']} 至 {window_info['latest_timestamp']}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] 滚动窗口防护测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_strict_mode_violations():
    """测试严格模式违规处理"""
    print("\n" + "="*60)
    print("           严格模式违规测试")
    print("="*60)
    
    try:
        # 1. 测试严格模式
        print("\n1. 测试严格模式...")
        
        guard = create_temporal_guard()
        base_time = datetime(2024, 9, 4, 10, 30, 0)
        
        with guard.temporal_scope(base_time, strict_mode=True) as context:
            
            print(f"[OK] 进入严格模式")
            print(f"   当前时间: {context.current_time}")
            
            # 尝试访问未来数据（应该抛出异常）
            try:
                future_time = base_time + timedelta(hours=1)
                guard.validate_data_timestamp(future_time, "test_data")
                print("[ERROR] 严格模式应该拒绝未来数据")
            except ValueError as e:
                print(f"[OK] 严格模式正确拒绝未来数据: {e}")
        
        # 2. 测试非严格模式
        print("\n2. 测试非严格模式...")
        
        with guard.temporal_scope(base_time, strict_mode=False) as context:
            
            print(f"[OK] 进入非严格模式")
            
            # 尝试访问未来数据（应该记录违规但不抛异常）
            future_time = base_time + timedelta(hours=1)
            is_valid = guard.validate_data_timestamp(future_time, "test_data")
            
            print(f"[OK] 非严格模式处理未来数据: 有效={is_valid}")
            
            summary = guard.get_violation_summary()
            print(f"   记录违规: {summary['total_violations']} 条")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] 严格模式违规测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_trading_time_validation():
    """测试交易时间验证"""
    print("\n" + "="*60)
    print("           交易时间验证测试")
    print("="*60)
    
    try:
        # 1. 创建时间防护与数据访问
        print("\n1. 创建时间防护...")
        
        calendar = create_ashare_calendar()
        guard = create_temporal_guard(calendar)
        
        print(f"[OK] 时间防护创建成功")
        
        # 2. 测试不同时间的验证
        print("\n2. 测试不同时间的验证...")
        
        test_times = [
            (datetime(2024, 9, 4, 9, 30, 0), "开盘时间"),   # 交易时间
            (datetime(2024, 9, 4, 12, 0, 0), "午休时间"),   # 非交易时间
            (datetime(2024, 9, 4, 14, 30, 0), "下午交易"),  # 交易时间
            (datetime(2024, 9, 4, 16, 0, 0), "收盘后"),     # 非交易时间
            (datetime(2024, 9, 7, 10, 0, 0), "周末"),       # 周末
        ]
        
        for test_time, description in test_times:
            with guard.temporal_scope(test_time + timedelta(hours=1), strict_mode=False) as context:
                is_valid = guard.validate_data_timestamp(test_time, "market_data")
                print(f"   {description} ({test_time.strftime('%m-%d %H:%M')}): {'有效' if is_valid else '无效'}")
        
        # 3. 获取最终违规统计
        print("\n3. 最终违规统计...")
        
        with guard.temporal_scope(datetime.now(), strict_mode=False) as context:
            summary = guard.get_violation_summary()
            
            print(f"[OK] 违规统计完成")
            print(f"   总违规数: {summary['total_violations']}")
            
            if summary['violations_by_type']:
                print("   违规类型分布:")
                for vtype, count in summary['violations_by_type'].items():
                    print(f"     {vtype}: {count} 条")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] 交易时间验证测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_temporal_integrity_end_to_end():
    """测试端到端时间完整性"""
    print("\n" + "="*60)
    print("           端到端时间完整性测试")
    print("="*60)
    
    try:
        # 1. 模拟完整的回测场景
        print("\n1. 模拟回测场景...")
        
        guard = create_temporal_guard()
        data_access = create_point_in_time_access(guard)
        
        # 回测时间范围
        start_date = datetime(2024, 8, 1, 9, 30, 0)
        end_date = datetime(2024, 9, 4, 15, 0, 0)
        current_time = start_date
        
        violation_count = 0
        data_points_processed = 0
        
        print(f"[OK] 回测场景设置")
        print(f"   开始时间: {start_date}")
        print(f"   结束时间: {end_date}")
        
        # 2. 逐日推进模拟
        print("\n2. 逐日推进模拟...")
        
        while current_time < end_date:
            
            with guard.temporal_scope(current_time, strict_mode=False) as context:
                
                # 获取历史数据（模拟策略需要的数据）
                try:
                    market_data = data_access.get_market_data(
                        symbol="000001",
                        end_time=current_time,
                        lookback_periods=20
                    )
                    data_points_processed += len(market_data)
                    
                    # 模拟生成交易信号
                    if market_data:
                        signal = TradingSignal(
                            signal_id=f"signal_{current_time.strftime('%Y%m%d_%H%M')}",
                            symbol="000001",
                            timestamp=current_time,
                            signal_type=SignalType.HOLD,
                            strength=0.5,
                            confidence=0.6,
                            valid_from=current_time,
                            agent_id="backtest_agent",
                            agent_type="BacktestAgent",
                            reasoning="回测模拟信号"
                        )
                        
                        data_access.validate_signal_timing(signal)
                    
                except Exception as e:
                    print(f"   时间 {current_time}: 处理异常 - {e}")
                
                # 统计违规
                summary = guard.get_violation_summary()
                new_violations = summary['total_violations'] - violation_count
                violation_count = summary['total_violations']
                
                if new_violations > 0:
                    print(f"   时间 {current_time.strftime('%m-%d %H:%M')}: 新增违规 {new_violations} 条")
            
            # 推进时间（每次前进1小时）
            current_time += timedelta(hours=1)
        
        # 3. 最终统计
        print("\n3. 最终统计...")
        
        with guard.temporal_scope(end_date, strict_mode=False) as context:
            final_summary = guard.get_violation_summary()
            
            print(f"[OK] 回测完成")
            print(f"   处理数据点: {data_points_processed:,} 个")
            print(f"   总违规数: {final_summary['total_violations']} 条")
            print(f"   违规率: {final_summary['total_violations']/max(data_points_processed,1)*100:.2f}%")
            
            if final_summary['violations_by_type']:
                print("   违规类型:")
                for vtype, count in final_summary['violations_by_type'].items():
                    print(f"     {vtype}: {count} 条")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] 端到端时间完整性测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("开始前视泄漏防护机制测试...")
    
    tests = [
        ("时间上下文测试", test_temporal_context),
        ("时间防护基础测试", test_temporal_guard_basic),
        ("时间点数据访问测试", test_point_in_time_access),
        ("滚动窗口防护测试", test_rolling_window_protection),
        ("严格模式违规测试", test_strict_mode_violations),
        ("交易时间验证测试", test_trading_time_validation),
        ("端到端时间完整性测试", test_temporal_integrity_end_to_end),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n开始 {test_name}...")
        success = test_func()
        results.append((test_name, success))
    
    # 汇总结果
    print(f"\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"总测试数: {total}")
    print(f"通过测试: {passed}")
    print(f"失败测试: {total - passed}")
    
    for test_name, success in results:
        status = "[PASS]" if success else "[FAIL]"
        print(f"  {test_name}: {status}")
    
    if passed == total:
        print(f"\n[SUCCESS] 前视泄漏防护机制工作正常！")
        return True
    else:
        print(f"\n[WARNING] 还有 {total - passed} 个测试需要修复")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)