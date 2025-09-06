"""
所有修复模块的验证测试脚本
"""

import subprocess
import sys
from pathlib import Path


def run_test(test_file, description):
    """运行单个测试"""
    print(f"\n{'='*60}")
    print(f"运行测试: {description}")
    print(f"文件: {test_file}")
    print('='*60)
    
    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=Path(__file__).parent
        )
        
        if result.returncode == 0:
            print("[PASS] 测试通过")
            return True
        else:
            print("[FAIL] 测试失败")
            if result.stderr:
                print(f"错误信息: {result.stderr[:500]}...")
            return False
            
    except subprocess.TimeoutExpired:
        print("[FAIL] 测试超时")
        return False
    except Exception as e:
        print(f"[FAIL] 测试异常: {e}")
        return False


def main():
    """运行所有修复的测试"""
    print("="*60)
    print("           所有修复模块验证测试")
    print("="*60)
    
    tests = [
        ("test/test_data_fetcher_simple.py", "数据获取模块"),
        ("test/test_portfolio_simple.py", "投资组合管理模块"),
        ("test/test_logger_minimal.py", "可解释性日志模块"),
        ("test/test_system_simple.py", "完整系统集成")
    ]
    
    results = []
    
    for test_file, description in tests:
        success = run_test(test_file, description)
        results.append((description, success))
    
    # 汇总结果
    print(f"\n{'='*60}")
    print("测试结果汇总")
    print('='*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"总测试数: {total}")
    print(f"通过测试: {passed}")
    print(f"失败测试: {total - passed}")
    print(f"成功率: {passed/total*100:.1f}%")
    
    print("\n详细结果:")
    for description, success in results:
        status = "[PASS]" if success else "[FAIL]"
        print(f"  {description}: {status}")
    
    if passed == total:
        print(f"\n[SUCCESS] 所有测试都通过了！MyTrade系统运行正常。")
        return True
    else:
        print(f"\n[WARNING] 还有 {total - passed} 个测试需要修复。")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)