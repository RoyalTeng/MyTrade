"""
可解释性日志模块简化测试
"""

import sys
import os
import tempfile
from pathlib import Path
from datetime import datetime
import json

# 添加src到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mytrade.logging import InterpretableLogger


def test_logger_simple():
    """可解释性日志模块简化测试"""
    print("="*60)
    print("           可解释性日志模块简化测试")
    print("="*60)
    
    try:
        # 使用临时目录作为日志目录
        with tempfile.TemporaryDirectory() as temp_dir:
            log_dir = Path(temp_dir) / "test_logs"
            
            # 1. 初始化日志记录器
            print("\n1. 初始化日志记录器...")
            logger = InterpretableLogger(log_dir=str(log_dir))
            print(f"[OK] 日志记录器初始化成功")
            print(f"   会话ID: {logger.session_id}")
            print(f"   日志目录: {log_dir}")
            
            # 2. 开始交易会话
            print("\n2. 开始交易会话...")
            context = {
                "symbol": "000001",
                "date": "2025-09-04",
                "strategy": "价值投资",
                "market_condition": "震荡",
                "risk_level": "中等"
            }
            session_id = logger.start_trading_session("000001", context)
            print(f"[OK] 交易会话已开始")
            print(f"   会话ID: {session_id}")
            
            # 3. 记录分析过程
            print("\n3. 记录分析过程...")
            
            # 基本面分析师
            fundamental_analysis = {
                "agent": "基本面分析师",
                "analysis": {
                    "pe_ratio": 15.2,
                    "pb_ratio": 1.8,
                    "roe": 0.12,
                    "debt_ratio": 0.35
                },
                "conclusion": "估值合理，财务状况良好",
                "recommendation": "BUY",
                "confidence": 0.75
            }
            logger.log_agent_analysis(fundamental_analysis)
            print("[OK] 基本面分析已记录")
            
            # 技术分析师
            technical_analysis = {
                "agent": "技术分析师",
                "analysis": {
                    "rsi": 45.2,
                    "macd": "金叉",
                    "ma20": 12.30,
                    "volume_ratio": 1.2
                },
                "conclusion": "技术指标偏多头",
                "recommendation": "BUY",
                "confidence": 0.68
            }
            logger.log_agent_analysis(technical_analysis)
            print("[OK] 技术分析已记录")
            
            # 4. 记录最终决策
            print("\n4. 记录最终决策...")
            decision = {
                "action": "BUY",
                "volume": 1000,
                "price": 12.50,
                "confidence": 0.72,
                "reasoning": "基本面和技术面都支持买入，综合评估后决定建仓"
            }
            logger.log_trading_decision(decision)
            print("[OK] 交易决策已记录")
            
            # 5. 结束交易会话
            print("\n5. 结束交易会话...")
            logger.end_trading_session({"status": "completed", "result": "success"})
            print("[OK] 交易会话已结束")
            
            # 6. 检查生成的日志文件
            print("\n6. 检查生成的日志文件...")
            log_files = list(log_dir.glob("**/*.json"))
            print(f"[OK] 生成了 {len(log_files)} 个JSON日志文件")
            
            md_files = list(log_dir.glob("**/*.md"))
            print(f"[OK] 生成了 {len(md_files)} 个Markdown日志文件")
            
            # 7. 读取并验证日志内容
            print("\n7. 验证日志内容...")
            if log_files:
                sample_file = log_files[0]
                with open(sample_file, 'r', encoding='utf-8') as f:
                    log_content = json.load(f)
                print(f"[OK] JSON日志文件内容验证通过")
                print(f"   文件: {sample_file.name}")
                print(f"   会话ID: {log_content.get('session_id', 'N/A')}")
                print(f"   记录数: {len(log_content.get('records', []))}")
            
            if md_files:
                sample_md = md_files[0]
                with open(sample_md, 'r', encoding='utf-8') as f:
                    md_content = f.read()
                print(f"[OK] Markdown文件内容验证通过")
                print(f"   文件: {sample_md.name}")
                print(f"   内容长度: {len(md_content)} 字符")
            
        print("\n" + "="*60)
        print("可解释性日志模块测试完成")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"[ERROR] 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_logger_simple()
    exit(0 if success else 1)