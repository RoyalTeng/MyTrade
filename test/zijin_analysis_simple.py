#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from test_encoding_fix import safe_print
from mytrade.config import get_config_manager
from mytrade.data.market_data_fetcher import MarketDataFetcher, DataSourceConfig
from mytrade.trading import SignalGenerator

def main():
    safe_print("紫金矿业(601899)分析开始")
    
    # 初始化组件
    config = DataSourceConfig(source="akshare", cache_dir=Path("data/cache"))
    fetcher = MarketDataFetcher(config)
    
    config_manager = get_config_manager("config.yaml")
    config = config_manager.get_config()
    signal_generator = SignalGenerator(config)
    
    # 获取数据
    from datetime import datetime, timedelta
    end_date = datetime.now().strftime("%Y%m%d")
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
    
    data = fetcher.fetch_history("601899", start_date, end_date)
    
    if not data.empty:
        latest = data.iloc[-1]
        prev = data.iloc[-2]
        change = ((latest["close"] - prev["close"]) / prev["close"]) * 100
        
        safe_print(f"当前价格: {latest["close"]:.2f}元")
        safe_print(f"日涨跌幅: {change:+.2f}%")
        safe_print(f"成交量: {latest["volume"]:,.0f}股")
        
        # 生成交易信号
        signal_report = signal_generator.generate_signal("601899")
        if signal_report:
            signal = signal_report.signal
            safe_print(f"AI信号: {signal.action}")
            safe_print(f"置信度: {signal.confidence:.2f}")
        
        safe_print("分析完成")
        return True
    else:
        safe_print("数据获取失败")
        return False

if __name__ == "__main__":
    main()
