"""
可解释性日志模块简化测试 v2
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# 添加src到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mytrade.logging import InterpretableLogger, AgentType, AnalysisStep, DecisionPoint


def test_logger_simple():
    """可解释性日志模块简化测试"""
    print("="*60)
    print("           可解释性日志模块简化测试")
    print("="*60)
    
    try:
        # 使用项目中的logs目录
        log_dir = Path(__file__).parent.parent / "logs" / "test"
        log_dir.mkdir(parents=True, exist_ok=True)
        
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
            "strategy": "价值投资"
        }
        session_id = logger.start_trading_session("000001", context)
        print(f"[OK] 交易会话已开始")
        print(f"   会话ID: {session_id}")
        
        # 3. 记录分析步骤
        print("\n3. 记录分析步骤...")
        
        # 记录基本面分析步骤
        step_id = logger.log_analysis_step(
            agent_type=AgentType.FUNDAMENTAL_ANALYST,
            input_data={"pe_ratio": 15.2, "pb_ratio": 1.8},
            analysis_process="对000001进行基本面分析",
            conclusion="估值合理，财务状况良好",
            confidence=0.75,
            reasoning=["PE比值15.2在合理范围内", "PB比值1.8相对偏低", "ROE稳定"],
            supporting_data={"industry_avg_pe": 18.5, "market_cap": "1200亿"}
        )
        print(f"[OK] 分析步骤已记录，步骤ID: {step_id}")
        
        # 4. 记录决策点
        print("\n4. 记录决策点...")
        
        decision_id = logger.log_decision_point(
            context="震荡市场环境下的交易决策",
            options=[
                {"action": "BUY", "volume": 1000, "rationale": "基本面良好"},
                {"action": "HOLD", "volume": 0, "rationale": "等待更好时机"},
                {"action": "SELL", "volume": 0, "rationale": "当前无持仓"}
            ],
            chosen_option={"action": "BUY", "volume": 1000, "price": 12.50},
            rationale="基本面分析显示估值合理，技术面支持，适合建仓",
            risk_assessment={
                "max_loss_pct": 5.0,
                "expected_return_pct": 10.0,
                "time_horizon": "3个月"
            },
            confidence=0.72
        )
        print(f"[OK] 决策点已记录，决策ID: {decision_id}")
        
        # 5. 结束交易会话
        print("\n5. 结束交易会话...")
        result = {"status": "completed", "action_taken": "BUY"}
        logger.end_trading_session(result)
        print("[OK] 交易会话已结束")
        
        # 6. 检查生成的文件
        print("\n6. 检查生成的文件...")
        log_files = list(log_dir.glob("*.log"))
        json_files = list(log_dir.glob("*.json"))
        md_files = list(log_dir.glob("*.md"))
        
        print(f"[OK] 日志文件统计:")
        print(f"   .log文件: {len(log_files)}")
        print(f"   .json文件: {len(json_files)}")
        print(f"   .md文件: {len(md_files)}")
        
        if log_files:
            print(f"   最新日志文件: {log_files[-1].name}")
        
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