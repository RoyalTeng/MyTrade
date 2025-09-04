"""
可解释性日志模块最小化测试
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# 添加src到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# 禁用日志器的控制台输出来避免编码问题
import logging
logging.basicConfig(level=logging.ERROR)

from mytrade.logging import InterpretableLogger, AgentType


def test_logger_minimal():
    """可解释性日志模块最小化测试"""
    print("="*60)
    print("           可解释性日志模块最小化测试")
    print("="*60)
    
    try:
        # 使用项目中的logs目录
        log_dir = Path(__file__).parent.parent / "logs" / "test"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. 初始化日志记录器 (禁用控制台输出)
        print("\n1. 初始化日志记录器...")
        logger = InterpretableLogger(log_dir=str(log_dir))
        logger.enable_console_output = False  # 禁用控制台输出避免编码问题
        print(f"[OK] 日志记录器初始化成功")
        print(f"   会话ID: {logger.session_id}")
        
        # 2. 开始交易会话
        print("\n2. 开始交易会话...")
        context = {"symbol": "000001", "strategy": "test"}
        session_id = logger.start_trading_session("000001", context)
        print(f"[OK] 交易会话已开始")
        print(f"   会话ID: {session_id[:50]}...")  # 截断显示
        
        # 3. 记录分析步骤
        print("\n3. 记录分析步骤...")
        step_id = logger.log_analysis_step(
            agent_type=AgentType.FUNDAMENTAL_ANALYST,
            input_data={"pe": 15.2, "pb": 1.8},
            analysis_process="基本面分析",
            conclusion="估值合理",
            confidence=0.75,
            reasoning=["PE合理", "PB偏低"],
            supporting_data={"industry_pe": 18.5}
        )
        print(f"[OK] 分析步骤已记录")
        
        # 4. 记录决策点
        print("\n4. 记录决策点...")
        decision_id = logger.log_decision_point(
            context="市场分析决策",
            options=[
                {"action": "BUY", "volume": 1000},
                {"action": "HOLD", "volume": 0}
            ],
            chosen_option={"action": "BUY", "volume": 1000},
            rationale="基本面支持",
            confidence=0.72
        )
        print(f"[OK] 决策点已记录")
        
        # 5. 结束交易会话
        print("\n5. 结束交易会话...")
        result = {"status": "completed"}
        logger.end_trading_session(result)
        print("[OK] 交易会话已结束")
        
        # 6. 检查生成的文件
        print("\n6. 检查生成的文件...")
        log_files = list(log_dir.glob("*.log"))
        json_files = list(log_dir.glob("*.json"))
        
        total_files = len(log_files) + len(json_files)
        print(f"[OK] 生成了 {total_files} 个日志文件")
        if log_files:
            print(f"   日志文件: {log_files[-1].name}")
        if json_files:
            print(f"   JSON文件: {json_files[-1].name}")
        
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
    success = test_logger_minimal()
    exit(0 if success else 1)