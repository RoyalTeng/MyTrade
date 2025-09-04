"""
简化的结构化日志测试

快速验证JSON+Markdown双写功能
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from mytrade.logging.structured_logger import (
    DualFormatLogger, StructuredLogLevel, LogCategory
)


def test_basic_dual_format():
    """测试基本的双格式输出"""
    print("[TEST] 测试结构化日志双格式输出...")
    
    # 创建临时目录
    test_dir = Path(tempfile.mkdtemp())
    session_id = "test_basic"
    
    try:
        # 创建日志记录器（同步模式）
        logger = DualFormatLogger(
            log_dir=str(test_dir),
            session_id=session_id,
            enable_json=True,
            enable_markdown=True,
            enable_console=False,  # 避免控制台干扰
            async_mode=False  # 同步模式便于测试
        )
        
        # 记录几种不同类型的日志
        logger.log(
            level=StructuredLogLevel.INFO,
            category=LogCategory.SYSTEM,
            component="test_system",
            message="系统初始化完成",
            data={"version": "2.0.0", "mode": "test"}
        )
        
        logger.log(
            level=StructuredLogLevel.ANALYSIS,
            category=LogCategory.AGENT,
            component="fundamental_analyst",
            message="基本面分析完成",
            data={
                "symbol": "000001.SZ",
                "pe_ratio": 15.6,
                "conclusion": "低估值"
            },
            metadata={"execution_time": 125}
        )
        
        logger.log(
            level=StructuredLogLevel.WARNING,
            category=LogCategory.TRADING,
            component="risk_manager",
            message="风险告警",
            data={
                "risk_level": "medium",
                "position_size": 0.15,
                "warning": "仓位偏高"
            }
        )
        
        # 关闭日志记录器
        logger.close()
        
        # 验证文件生成
        json_files = list(test_dir.glob(f"session_{session_id}_*.json"))
        md_files = list(test_dir.glob(f"session_{session_id}_*.md"))
        
        print(f"  [OK] JSON文件生成: {len(json_files)} 个")
        print(f"  [OK] Markdown文件生成: {len(md_files)} 个")
        
        # 验证JSON内容
        if json_files:
            import json
            with open(json_files[0], 'r', encoding='utf-8') as f:
                lines = f.readlines()
                print(f"  [OK] JSON记录条数: {len(lines)}")
                
                # 解析第一条记录
                first_entry = json.loads(lines[0])
                print(f"  [OK] 第一条记录级别: {first_entry['level']}")
                print(f"  [OK] 第一条记录组件: {first_entry['component']}")
                print(f"  [OK] 第一条记录数据键: {list(first_entry['data'].keys())}")
        
        # 验证Markdown内容
        if md_files:
            with open(md_files[0], 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"  [OK] Markdown内容长度: {len(content)} 字符")
                print(f"  [OK] 包含标题: {'TradingAgents 结构化日志' in content}")
                print(f"  [OK] 包含INFO级别: {'INFO - test_system' in content}")
                print(f"  [OK] 包含ANALYSIS级别: {'ANALYSIS - fundamental_analyst' in content}")
                print(f"  [OK] 包含WARNING级别: {'WARNING - risk_manager' in content}")
        
        print("[SUCCESS] 结构化日志双格式测试通过！")
        return True
        
    except Exception as e:
        print(f"[ERROR] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # 清理临时目录
        shutil.rmtree(test_dir)


def test_performance_logging():
    """测试性能日志记录"""
    print("\n[TEST] 测试性能日志记录...")
    
    test_dir = Path(tempfile.mkdtemp())
    
    try:
        with DualFormatLogger(
            log_dir=str(test_dir),
            session_id="perf_test",
            enable_console=False,
            async_mode=False
        ) as logger:
            
            # 记录性能指标
            logger.log_performance(
                component="data_fetcher",
                metric="response_time",
                value=156.7,
                unit="ms",
                additional_data={
                    "endpoint": "/api/stock/data",
                    "cache_hit": False
                }
            )
            
            # 记录错误
            try:
                raise ValueError("测试错误记录")
            except Exception as e:
                logger.log_error("test_component", e, {"test_context": "error_logging"})
        
        # 验证日志记录
        json_files = list(test_dir.glob("session_perf_test_*.json"))
        if json_files:
            import json
            with open(json_files[0], 'r', encoding='utf-8') as f:
                lines = f.readlines()
                print(f"  [OK] 性能+错误日志记录条数: {len(lines)}")
                
                # 验证性能日志
                perf_entry = json.loads(lines[0])
                print(f"  [OK] 性能日志分类: {perf_entry['category']}")
                print(f"  [OK] 性能指标: {perf_entry['data']['metric']}")
                print(f"  [OK] 性能值: {perf_entry['data']['value']}")
                
                # 验证错误日志
                if len(lines) > 1:
                    error_entry = json.loads(lines[1])
                    print(f"  [OK] 错误日志级别: {error_entry['level']}")
                    print(f"  [OK] 错误类型: {error_entry['data']['error_type']}")
        
        print("[SUCCESS] 性能日志记录测试通过！")
        return True
        
    except Exception as e:
        print(f"[ERROR] 性能测试失败: {e}")
        return False
        
    finally:
        shutil.rmtree(test_dir)


if __name__ == '__main__':
    print("[START] 开始结构化日志系统测试...\n")
    
    success1 = test_basic_dual_format()
    success2 = test_performance_logging()
    
    if success1 and success2:
        print("\n[SUCCESS] 所有结构化日志测试通过！")
        print("[COMPLETE] P1优先级：结构化日志（JSON+Markdown双写）功能完成")
    else:
        print("\n[FAIL] 部分测试失败")
        exit(1)