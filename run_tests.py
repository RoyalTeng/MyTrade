#!/usr/bin/env python3
"""
MyTrade 测试运行器

运行所有模块的测试用例，验证系统功能。
"""

import sys
import subprocess
from pathlib import Path
import time

def run_test(test_file, description):
    """运行单个测试文件"""
    print(f"\n{'='*60}")
    print(f"运行测试: {description}")
    print(f"文件: {test_file}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        # 运行测试
        result = subprocess.run([
            sys.executable, 
            str(test_file)
        ], 
        cwd=Path(__file__).parent,
        capture_output=False,
        text=True
        )
        
        duration = time.time() - start_time
        
        if result.returncode == 0:
            print(f"PASS (Duration: {duration:.1f}s)")
            return True
        else:
            print(f"FAIL (Exit code: {result.returncode})")
            return False
            
    except Exception as e:
        print(f"ERROR: Test execution failed: {e}")
        return False

def main():
    """主测试流程"""
    print("MyTrade System Test Suite")
    print("=" * 60)
    
    # 获取项目根目录
    root_dir = Path(__file__).parent
    test_dir = root_dir / "test"
    
    # 定义测试文件和描述
    tests = [
        (test_dir / "test_config.py", "配置管理模块测试"),
        (test_dir / "test_data_fetcher.py", "数据获取模块测试"),
        (test_dir / "test_signal_generator.py", "信号生成模块测试"),
        (test_dir / "test_portfolio_manager.py", "投资组合管理模块测试"),
        (test_dir / "test_backtest_engine.py", "回测引擎模块测试"),
        (test_dir / "test_interpretable_logger.py", "可解释性日志模块测试"),
        (test_dir / "test_full_system.py", "完整系统集成测试"),
    ]
    
    # 检查测试文件是否存在
    available_tests = []
    missing_tests = []
    
    for test_file, description in tests:
        if test_file.exists():
            available_tests.append((test_file, description))
        else:
            missing_tests.append((test_file, description))
    
    print(f"Found {len(available_tests)} available tests")
    if missing_tests:
        print(f"Missing {len(missing_tests)} test files:")
        for test_file, desc in missing_tests:
            print(f"  - {test_file.name}: {desc}")
    
    if not available_tests:
        print("ERROR: No test files found!")
        return False
    
    # 运行测试
    passed_tests = []
    failed_tests = []
    
    total_start_time = time.time()
    
    for test_file, description in available_tests:
        success = run_test(test_file, description)
        
        if success:
            passed_tests.append(description)
        else:
            failed_tests.append(description)
        
        # 短暂休息，避免资源冲突
        time.sleep(1)
    
    total_duration = time.time() - total_start_time
    
    # 输出测试结果摘要
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    print(f"Total time: {total_duration:.1f} seconds")
    print(f"Total tests: {len(available_tests)}")
    print(f"Passed: {len(passed_tests)}")
    print(f"Failed: {len(failed_tests)}")
    
    if passed_tests:
        print("\nPassed tests:")
        for test in passed_tests:
            print(f"  - {test}")
    
    if failed_tests:
        print("\nFailed tests:")
        for test in failed_tests:
            print(f"  - {test}")
    
    # 最终状态
    if len(failed_tests) == 0:
        print(f"\nAll tests passed! System is healthy!")
        return True
    else:
        print(f"\n{len(failed_tests)} tests failed, please check related modules")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)