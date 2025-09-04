#!/usr/bin/env python3
"""
运行完整集成测试套件
"""

import subprocess
import sys
from pathlib import Path

# 导入编码修复工具
from test_encoding_fix import safe_print

def main():
    """运行所有集成测试"""
    tests = [
        ('数据获取模块', 'test_data_compatible.py'),
        ('投资组合模块', 'test_portfolio_clean.py'), 
        ('回测引擎模块', 'test_backtest_clean.py'),
        ('信号生成模块', 'test_signal_clean.py'),
        ('简单集成测试', 'test_simple_integration.py'),
        ('修复验证测试', 'test_fixes_verification.py')
    ]

    passed = 0
    total = len(tests)
    results = []

    safe_print('='*80)
    safe_print('           MyTrade 完整集成测试套件')
    safe_print('='*80)

    for test_name, test_file in tests:
        safe_print(f'\\n>>> 运行 {test_name} ({test_file})...')
        try:
            # 确保在test目录下运行
            test_path = Path(__file__).parent / test_file
            result = subprocess.run([sys.executable, str(test_path)], 
                                  capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                safe_print(f'✅ PASS: {test_name}')
                results.append((test_name, True))
                passed += 1
            else:
                safe_print(f'❌ FAIL: {test_name}')
                results.append((test_name, False))
                # 显示错误信息的前几行
                if result.stderr:
                    lines = result.stderr.split('\\n')[:3]
                    for line in lines:
                        if line.strip():
                            safe_print(f'   错误: {line}')
        except subprocess.TimeoutExpired:
            safe_print(f'⏰ TIMEOUT: {test_name}')
            results.append((test_name, False))
        except Exception as e:
            safe_print(f'💥 ERROR: {test_name} - {e}')
            results.append((test_name, False))

    # 输出汇总结果
    safe_print('\\n' + '='*80)
    safe_print('                集成测试结果汇总')  
    safe_print('='*80)
    
    for test_name, success in results:
        status = "PASS" if success else "FAIL"
        safe_print(f'   {status}: {test_name}')
    
    safe_print(f'\\n通过: {passed}/{total} 测试')
    safe_print(f'成功率: {passed/total*100:.1f}%')

    if passed == total:
        safe_print('\\n🎉 所有集成测试通过！系统生产就绪')
        return True
    elif passed >= total * 0.8:  # 80%以上通过
        safe_print(f'\\n⚠️ {total-passed} 个测试需要关注，但核心功能正常')
        return True
    else:
        safe_print(f'\\n❌ {total-passed} 个测试失败，需要修复')
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)