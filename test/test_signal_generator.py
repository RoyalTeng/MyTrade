"""
测试交易信号生成模块
"""

import sys
import logging
from pathlib import Path
from datetime import datetime, timedelta

# 添加src到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mytrade.trading import SignalGenerator
from mytrade.config import get_config_manager


def test_signal_generator():
    """测试信号生成器功能"""
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("=== 测试交易信号生成功能 ===")
    
    # 初始化配置（使用默认配置）
    config_manager = get_config_manager("../config.yaml")
    
    # 创建信号生成器
    signal_generator = SignalGenerator()
    
    # 1. 测试单个股票信号生成
    print("\\n1. 测试单个股票信号生成...")
    try:
        report = signal_generator.generate_signal("600519")
        
        print(f"股票代码: {report.symbol}")
        print(f"分析日期: {report.date}")
        print(f"交易信号: {report.signal.action}")
        print(f"建议数量: {report.signal.volume}")
        print(f"信心度: {report.signal.confidence:.2f}")
        print(f"原因: {report.signal.reason}")
        print(f"分析摘要: {report.summary}")
        print()
        
        # 显示详细分析
        print("详细分析结果:")
        for i, analysis in enumerate(report.detailed_analyses, 1):
            agent_name = analysis.get('agent', f'Agent_{i}')
            print(f"  {i}. {agent_name}")
            
            if 'analysis' in analysis:
                for key, value in analysis['analysis'].items():
                    print(f"     {key}: {value}")
            if 'conclusion' in analysis:
                print(f"     结论: {analysis['conclusion']}")
            if 'decision' in analysis:
                decision = analysis['decision']
                print(f"     决策: {decision}")
            print()
            
    except Exception as e:
        print(f"信号生成失败: {e}")
    
    # 2. 测试批量信号生成
    print("2. 测试批量信号生成...")
    try:
        symbols = ["600519", "000001", "000002"]
        batch_results = signal_generator.generate_batch_signals(symbols)
        
        print(f"批量处理结果: {len(batch_results)} 只股票")
        for symbol, report in batch_results.items():
            signal = report.signal
            print(f"  {symbol}: {signal.action} (数量: {signal.volume}, 信心: {signal.confidence:.2f})")
        print()
        
    except Exception as e:
        print(f"批量信号生成失败: {e}")
    
    # 3. 测试历史日期信号生成
    print("3. 测试历史日期信号生成...")
    try:
        yesterday = datetime.now() - timedelta(days=1)
        historical_report = signal_generator.generate_signal(
            "600519", 
            target_date=yesterday.strftime("%Y-%m-%d")
        )
        
        print(f"历史信号 - {historical_report.date}:")
        print(f"  操作: {historical_report.signal.action}")
        print(f"  信心度: {historical_report.signal.confidence:.2f}")
        print()
        
    except Exception as e:
        print(f"历史信号生成失败: {e}")
    
    # 4. 测试支持的股票代码
    print("4. 获取支持的股票代码...")
    try:
        supported_symbols = signal_generator.get_supported_symbols()
        print(f"支持 {len(supported_symbols)} 只股票")
        print(f"示例: {supported_symbols[:10]}")
        print()
    except Exception as e:
        print(f"获取股票列表失败: {e}")
    
    # 5. 测试健康检查
    print("5. 系统健康检查...")
    try:
        health_status = signal_generator.health_check()
        print(f"整体状态: {health_status['status']}")
        print("组件状态:")
        for component, status in health_status['components'].items():
            print(f"  {component}: {status['status']}")
            if 'error' in status:
                print(f"    错误: {status['error']}")
        print()
    except Exception as e:
        print(f"健康检查失败: {e}")
    
    print("信号生成器测试完成!")


if __name__ == "__main__":
    test_signal_generator()