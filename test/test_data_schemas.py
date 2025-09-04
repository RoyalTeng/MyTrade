"""
数据统一模式与交易日历测试

验证新的数据格式标准化和A股交易日历功能
"""

import sys
import json
from pathlib import Path
from datetime import datetime, date, timedelta
from decimal import Decimal

# 添加src到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mytrade.data.schemas import (
    MarketType, DataSource, TradingStatus,
    MarketDataPoint, MarketDataBatch,
    FinancialMetric, NewsItem,
    SignalType, TradingSignal,
    DataValidator
)
from mytrade.data.trading_calendar import (
    MarketStatus, HolidayType,
    AShareTradingCalendar, SuspensionDetector,
    create_ashare_calendar, create_suspension_detector
)


def test_market_data_schemas():
    """测试市场数据模式"""
    print("="*60)
    print("           市场数据模式测试")
    print("="*60)
    
    try:
        # 1. 测试MarketDataPoint创建与验证
        print("\n1. 测试MarketDataPoint创建与验证...")
        
        market_data = MarketDataPoint(
            symbol="000001",
            timestamp=datetime(2024, 9, 4, 9, 30, 0),
            trading_date=date(2024, 9, 4),
            open_price=Decimal("11.50"),
            high_price=Decimal("11.80"),
            low_price=Decimal("11.40"),
            close_price=Decimal("11.75"),
            volume=1000000,
            amount=Decimal("11750000.00"),
            turnover_rate=Decimal("2.5"),
            pe_ratio=Decimal("15.2"),
            pb_ratio=Decimal("1.8"),
            data_source=DataSource.AKSHARE
        )
        
        print(f"[OK] MarketDataPoint创建成功")
        print(f"   股票: {market_data.symbol}")
        print(f"   时间: {market_data.timestamp}")
        print(f"   OHLC: {market_data.open_price}/{market_data.high_price}/{market_data.low_price}/{market_data.close_price}")
        print(f"   成交量: {market_data.volume:,}")
        print(f"   数据源: {market_data.data_source}")
        
        # 2. 测试数据验证
        print("\n2. 测试数据验证...")
        
        # 测试价格验证（应该成功）
        try:
            valid_data = MarketDataPoint(
                symbol="000001",
                timestamp=datetime.now(),
                trading_date=date.today(),
                open_price=Decimal("10.00"),
                high_price=Decimal("10.50"), 
                low_price=Decimal("9.80"),
                close_price=Decimal("10.20"),
                volume=100000,
                amount=Decimal("1000000"),
                data_source=DataSource.TUSHARE
            )
            print("[OK] 有效数据验证通过")
        except Exception as e:
            print(f"[ERROR] 有效数据验证失败: {e}")
        
        # 测试价格验证（应该失败）
        try:
            invalid_data = MarketDataPoint(
                symbol="000001",
                timestamp=datetime.now(),
                trading_date=date.today(),
                open_price=Decimal("10.00"),
                high_price=Decimal("9.50"),  # 高价低于开盘价
                low_price=Decimal("9.80"),
                close_price=Decimal("10.20"),
                volume=100000,
                amount=Decimal("1000000"),
                data_source=DataSource.AKSHARE
            )
            print("[ERROR] 无效数据验证应该失败但没有失败")
        except Exception as e:
            print(f"[OK] 无效数据验证正确拒绝: {e}")
        
        # 3. 测试JSON序列化
        print("\n3. 测试JSON序列化...")
        
        data_dict = market_data.model_dump(mode='json')
        data_json = json.dumps(data_dict, ensure_ascii=False, indent=2)
        
        print(f"[OK] JSON序列化成功")
        print(f"   JSON长度: {len(data_json)} 字符")
        print(f"   包含字段: {len(data_dict)} 个")
        
        # 4. 测试批量数据
        print("\n4. 测试批量数据...")
        
        batch_data = MarketDataBatch(
            symbol="000001",
            start_date=date(2024, 9, 1),
            end_date=date(2024, 9, 4),
            data_points=[market_data],
            total_records=1,
            data_source=DataSource.AKSHARE
        )
        
        print(f"[OK] 批量数据创建成功")
        print(f"   时间范围: {batch_data.start_date} 至 {batch_data.end_date}")
        print(f"   数据点数: {len(batch_data.data_points)}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] 市场数据模式测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_financial_schemas():
    """测试财务数据模式"""
    print("\n" + "="*60)
    print("           财务数据模式测试") 
    print("="*60)
    
    try:
        # 创建财务指标数据
        financial_metric = FinancialMetric(
            symbol="000001",
            report_date=date(2024, 6, 30),
            publish_date=date(2024, 8, 30),
            revenue=Decimal("1000000000"),
            net_profit=Decimal("150000000"),
            gross_profit_margin=Decimal("0.25"),
            net_profit_margin=Decimal("0.15"),
            roe=Decimal("0.12"),
            roa=Decimal("0.08"),
            total_assets=Decimal("5000000000"),
            total_liabilities=Decimal("3000000000"),
            debt_to_equity=Decimal("0.60"),
            current_ratio=Decimal("2.1"),
            revenue_growth=Decimal("0.08"),
            profit_growth=Decimal("0.12"),
            data_source=DataSource.TUSHARE
        )
        
        print(f"[OK] 财务指标创建成功")
        print(f"   股票: {financial_metric.symbol}")
        print(f"   报告期: {financial_metric.report_date}")
        print(f"   营收: {financial_metric.revenue:,}")
        print(f"   净利润: {financial_metric.net_profit:,}")
        print(f"   ROE: {financial_metric.roe:.1%}")
        print(f"   负债率: {financial_metric.debt_to_equity:.1%}")
        
        # 测试JSON序列化
        financial_dict = financial_metric.model_dump(mode='json')
        financial_json = json.dumps(financial_dict, ensure_ascii=False, indent=2)
        
        print(f"[OK] 财务数据JSON序列化成功")
        print(f"   JSON长度: {len(financial_json)} 字符")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] 财务数据模式测试失败: {e}")
        return False


def test_news_schemas():
    """测试新闻数据模式"""
    print("\n" + "="*60)
    print("           新闻数据模式测试")
    print("="*60)
    
    try:
        # 创建新闻数据
        news = NewsItem(
            news_id="news_20240904_001",
            title="某公司发布三季度业绩预告，净利润同比增长15%",
            content="某上市公司今日发布三季度业绩预告...",
            summary="公司三季度业绩预告显示净利润同比增长15%",
            publish_time=datetime(2024, 9, 4, 16, 30, 0),
            source="新浪财经",
            author="财经记者",
            url="https://finance.sina.com.cn/example",
            related_symbols=["000001", "000002"],
            keywords=["业绩预告", "净利润", "同比增长"],
            sentiment_score=0.6,
            sentiment_label="positive",
            impact_score=0.7,
            relevance_score=0.8,
            data_source=DataSource.SINA,
            language="zh"
        )
        
        print(f"[OK] 新闻数据创建成功")
        print(f"   新闻ID: {news.news_id}")
        print(f"   标题: {news.title[:50]}...")
        print(f"   发布时间: {news.publish_time}")
        print(f"   相关股票: {', '.join(news.related_symbols)}")
        print(f"   情感得分: {news.sentiment_score:.2f} ({news.sentiment_label})")
        print(f"   影响度: {news.impact_score:.2f}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] 新闻数据模式测试失败: {e}")
        return False


def test_trading_signal_schemas():
    """测试交易信号模式"""
    print("\n" + "="*60)
    print("           交易信号模式测试")
    print("="*60)
    
    try:
        # 创建交易信号
        signal = TradingSignal(
            signal_id="signal_20240904_001",
            symbol="000001",
            timestamp=datetime.now(),
            signal_type=SignalType.BUY,
            strength=0.75,
            confidence=0.82,
            target_price=Decimal("12.50"),
            stop_loss=Decimal("10.80"),
            position_size=0.05,
            valid_from=datetime.now(),
            valid_until=datetime.now() + timedelta(hours=24),
            agent_id="fundamental_analyst",
            agent_type="FundamentalAnalyst",
            reasoning="基本面分析显示估值合理，ROE良好，建议适度建仓",
            market_condition="neutral",
            risk_level="medium"
        )
        
        print(f"[OK] 交易信号创建成功")
        print(f"   信号ID: {signal.signal_id}")
        print(f"   股票: {signal.symbol}")
        print(f"   信号类型: {signal.signal_type}")
        print(f"   信号强度: {signal.strength:.2%}")
        print(f"   置信度: {signal.confidence:.2%}")
        print(f"   目标价: {signal.target_price}")
        print(f"   止损价: {signal.stop_loss}")
        print(f"   生成Agent: {signal.agent_type}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] 交易信号模式测试失败: {e}")
        return False


def test_trading_calendar():
    """测试交易日历"""
    print("\n" + "="*60)
    print("           交易日历测试")
    print("="*60)
    
    try:
        # 1. 创建交易日历
        print("\n1. 创建A股交易日历...")
        
        calendar = create_ashare_calendar()
        
        print("[OK] A股交易日历创建成功")
        
        # 2. 测试交易日判断
        print("\n2. 测试交易日判断...")
        
        test_dates = [
            date(2024, 9, 2),   # 周一，应该是交易日
            date(2024, 9, 7),   # 周六，不是交易日
            date(2024, 9, 8),   # 周日，不是交易日
            date(2024, 10, 1),  # 国庆节，不是交易日
            date(2024, 10, 8),  # 国庆后，应该是交易日
        ]
        
        for test_date in test_dates:
            is_trading = calendar.is_trading_day(test_date)
            print(f"   {test_date} ({test_date.strftime('%A')}): {'交易日' if is_trading else '非交易日'}")
        
        # 3. 测试获取交易日列表
        print("\n3. 测试获取交易日列表...")
        
        start_date = date(2024, 9, 1)
        end_date = date(2024, 9, 30)
        trading_days = calendar.get_trading_days(start_date, end_date)
        
        print(f"[OK] 9月交易日获取成功")
        print(f"   时间范围: {start_date} 至 {end_date}")
        print(f"   交易日数量: {len(trading_days)} 天")
        print(f"   首个交易日: {trading_days[0] if trading_days else '无'}")
        print(f"   最后交易日: {trading_days[-1] if trading_days else '无'}")
        
        # 4. 测试下一个/上一个交易日
        print("\n4. 测试下一个/上一个交易日...")
        
        base_date = date(2024, 9, 6)  # 假设这是周五
        next_trading = calendar.get_next_trading_day(base_date)
        prev_trading = calendar.get_previous_trading_day(base_date)
        
        print(f"[OK] 交易日导航成功")
        print(f"   基准日期: {base_date}")
        print(f"   下一个交易日: {next_trading}")
        print(f"   上一个交易日: {prev_trading}")
        
        # 5. 测试市场状态
        print("\n5. 测试市场状态...")
        
        test_times = [
            datetime(2024, 9, 4, 9, 0, 0),   # 盘前
            datetime(2024, 9, 4, 10, 30, 0), # 交易中
            datetime(2024, 9, 4, 12, 0, 0),  # 午休
            datetime(2024, 9, 4, 14, 30, 0), # 交易中
            datetime(2024, 9, 4, 16, 0, 0),  # 盘后
        ]
        
        for test_time in test_times:
            status = calendar.get_market_status(test_time)
            print(f"   {test_time.strftime('%H:%M')}: {status.value}")
        
        # 6. 测试交易日历摘要
        print("\n6. 测试交易日历摘要...")
        
        summary = calendar.get_trading_calendar_summary(2024)
        
        print(f"[OK] 2024年交易日历摘要")
        print(f"   总天数: {summary['total_days']} 天")
        print(f"   交易日: {summary['trading_days']} 天")
        print(f"   非交易日: {summary['non_trading_days']} 天")
        print(f"   节假日数量: {summary['holidays_count']} 个")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] 交易日历测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_suspension_detection():
    """测试停牌检测"""
    print("\n" + "="*60)
    print("           停牌检测测试")
    print("="*60)
    
    try:
        # 1. 创建停牌检测器
        print("\n1. 创建停牌检测器...")
        
        calendar = create_ashare_calendar()
        detector = create_suspension_detector(calendar)
        
        print("[OK] 停牌检测器创建成功")
        
        # 2. 测试正常交易数据
        print("\n2. 测试正常交易检测...")
        
        normal_data = [
            {
                'timestamp': '2024-09-02T09:30:00',
                'volume': 1000000,
                'open_price': 11.50,
                'high_price': 11.80,
                'low_price': 11.40,
                'close_price': 11.75
            },
            {
                'timestamp': '2024-09-03T09:30:00', 
                'volume': 1200000,
                'open_price': 11.75,
                'high_price': 12.00,
                'low_price': 11.60,
                'close_price': 11.85
            },
            {
                'timestamp': '2024-09-04T09:30:00',
                'volume': 900000,
                'open_price': 11.85,
                'high_price': 12.10,
                'low_price': 11.70,
                'close_price': 11.95
            }
        ]
        
        is_suspended, reason, details = detector.detect_suspension("000001", normal_data)
        
        print(f"[OK] 正常交易检测完成")
        print(f"   是否停牌: {is_suspended}")
        print(f"   检测状态: {details['analysis'].get('status', '未知')}")
        
        # 3. 测试停牌数据（零成交量）
        print("\n3. 测试零成交量停牌检测...")
        
        suspended_data = [
            {
                'timestamp': '2024-09-02T09:30:00',
                'volume': 0,  # 零成交量
                'open_price': 11.50,
                'high_price': 11.50,
                'low_price': 11.50,
                'close_price': 11.50
            },
            {
                'timestamp': '2024-09-03T09:30:00',
                'volume': 0,  # 零成交量
                'open_price': 11.50,
                'high_price': 11.50,
                'low_price': 11.50,
                'close_price': 11.50
            },
            {
                'timestamp': '2024-09-04T09:30:00',
                'volume': 0,  # 零成交量
                'open_price': 11.50,
                'high_price': 11.50,
                'low_price': 11.50,
                'close_price': 11.50
            }
        ]
        
        is_suspended, reason, details = detector.detect_suspension("000002", suspended_data)
        
        print(f"[OK] 停牌检测完成")
        print(f"   是否停牌: {is_suspended}")
        print(f"   停牌原因: {reason or '无'}")
        print(f"   零成交量天数: {details['analysis'].get('zero_volume_days', 0)}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] 停牌检测测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_data_validation():
    """测试数据验证工具"""
    print("\n" + "="*60) 
    print("           数据验证测试")
    print("="*60)
    
    try:
        # 1. 测试股票代码格式验证
        print("\n1. 测试股票代码格式验证...")
        
        test_symbols = [
            ("000001", MarketType.A_SHARE, True),   # 有效A股代码
            ("600519", MarketType.A_SHARE, True),   # 有效A股代码
            ("00700", MarketType.HK_STOCK, True),   # 有效港股代码
            ("AAPL", MarketType.A_SHARE, False),    # 无效A股代码
            ("0000", MarketType.A_SHARE, False),    # 无效长度
        ]
        
        for symbol, market_type, expected in test_symbols:
            result = DataValidator.validate_symbol_format(symbol, market_type)
            status = "[OK]" if result == expected else "[FAIL]"
            print(f"   {status} {symbol} ({market_type.value}): {result}")
        
        # 2. 测试数据质量评估
        print("\n2. 测试数据质量评估...")
        
        # 高质量数据
        high_quality_data = MarketDataPoint(
            symbol="000001",
            timestamp=datetime.now(),
            trading_date=date.today(),
            open_price=Decimal("11.50"),
            high_price=Decimal("11.80"),
            low_price=Decimal("11.40"),
            close_price=Decimal("11.75"),
            volume=1000000,
            amount=Decimal("11750000"),
            data_source=DataSource.AKSHARE
        )
        
        quality = DataValidator.estimate_data_quality(high_quality_data)
        print(f"   高质量数据评估: {quality}")
        
        # 低质量数据（零成交量）
        low_quality_data = MarketDataPoint(
            symbol="000001",
            timestamp=datetime.now(),
            trading_date=date.today(),
            open_price=Decimal("11.50"),
            high_price=Decimal("11.50"),
            low_price=Decimal("11.50"),
            close_price=Decimal("11.50"),
            volume=0,  # 零成交量
            amount=Decimal("0"),
            data_source=DataSource.MANUAL
        )
        
        quality = DataValidator.estimate_data_quality(low_quality_data)
        print(f"   低质量数据评估: {quality}")
        
        print("[OK] 数据验证测试完成")
        return True
        
    except Exception as e:
        print(f"[ERROR] 数据验证测试失败: {e}")
        return False


def main():
    """运行所有测试"""
    print("开始数据统一模式与交易日历测试...")
    
    tests = [
        ("市场数据模式测试", test_market_data_schemas),
        ("财务数据模式测试", test_financial_schemas),
        ("新闻数据模式测试", test_news_schemas),
        ("交易信号模式测试", test_trading_signal_schemas),
        ("交易日历测试", test_trading_calendar),
        ("停牌检测测试", test_suspension_detection),
        ("数据验证测试", test_data_validation),
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
        print(f"\n[SUCCESS] 数据统一模式与交易日历系统工作正常！")
        return True
    else:
        print(f"\n[WARNING] 还有 {total - passed} 个测试需要修复")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)