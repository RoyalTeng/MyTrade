"""
修复Windows下Unicode编码显示问题的测试工具

提供跨平台的Unicode输出支持。
"""

import sys
import os
import codecs
from io import StringIO


def setup_unicode_output():
    """设置Unicode输出支持"""
    if sys.platform.startswith('win'):
        # Windows平台特殊处理
        try:
            # 尝试设置控制台编码为UTF-8
            os.system('chcp 65001 > nul')
            
            # 重新配置stdout和stderr
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
            sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())
        except Exception:
            # 如果失败，使用ASCII安全模式
            pass


def safe_print(*args, **kwargs):
    """安全的打印函数，自动处理编码问题"""
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        # 如果遇到编码错误，转换为ASCII安全字符
        safe_args = []
        for arg in args:
            if isinstance(arg, str):
                # 替换Unicode字符为ASCII等价物
                safe_str = (arg.replace('✅', 'PASS')
                              .replace('❌', 'FAIL') 
                              .replace('⚠️', 'WARN')
                              .replace('🎉', '*')
                              .replace('🚀', '^')
                              .replace('📊', '>')
                              .replace('🔧', '#')
                              .replace('1️⃣', '1.')
                              .replace('2️⃣', '2.')
                              .replace('3️⃣', '3.')
                              .replace('4️⃣', '4.')
                              .replace('5️⃣', '5.')
                              .replace('6️⃣', '6.')
                              .replace('7️⃣', '7.')
                              .replace('8️⃣', '8.')
                              .replace('9️⃣', '9.'))
                safe_args.append(safe_str)
            else:
                safe_args.append(arg)
        print(*safe_args, **kwargs)


# 在模块导入时自动设置
if __name__ != "__main__":
    setup_unicode_output()


# 测试函数
def test_encoding_fix():
    """测试编码修复功能"""
    print("="*60)
    safe_print("           编码修复测试")
    print("="*60)
    
    safe_print("\n1. 测试基本Unicode字符...")
    safe_print("✅ PASS: 成功显示")
    safe_print("❌ FAIL: 失败显示") 
    safe_print("⚠️ WARN: 警告显示")
    
    safe_print("\n2. 测试Emoji字符...")
    safe_print("🎉 庆祝完成")
    safe_print("🚀 系统就绪")
    safe_print("📊 数据分析")
    
    safe_print("\n3. 测试数字Emoji...")
    safe_print("1️⃣ 第一步")
    safe_print("2️⃣ 第二步")
    safe_print("3️⃣ 第三步")
    
    print("\nPASS: 编码修复测试完成")
    return True


if __name__ == "__main__":
    test_encoding_fix()