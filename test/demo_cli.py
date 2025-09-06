#!/usr/bin/env python3
"""
MyTrade CLI 演示脚本

展示命令行工具的主要功能。
"""

import subprocess
import sys
from pathlib import Path

def run_command(cmd_args, description):
    """运行CLI命令并显示结果"""
    print(f"\n{'='*60}")
    print(f"演示: {description}")
    print(f"命令: python main.py {' '.join(cmd_args)}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            [sys.executable, "main.py"] + cmd_args,
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True,
            timeout=60  # 60秒超时
        )
        
        if result.stdout:
            print("输出:")
            print(result.stdout)
        
        if result.stderr:
            print("错误:")
            print(result.stderr)
        
        if result.returncode != 0:
            print(f"命令执行失败，退出码: {result.returncode}")
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("❌ 命令执行超时")
        return False
    except Exception as e:
        print(f"❌ 命令执行出错: {e}")
        return False

def main():
    """主演示流程"""
    print("🎬 MyTrade CLI 功能演示")
    print("=" * 60)
    
    # 演示命令列表
    demos = [
        (["--help"], "显示帮助信息"),
        (["system", "info"], "显示系统信息"),
        (["system", "health"], "系统健康检查"),
        (["data", "stocks"], "获取股票列表"),
        (["data", "fetch", "600519", "--days", "5"], "获取股票历史数据"),
        (["signal", "generate", "600519"], "生成交易信号"),
        (["demo", "--symbol", "600519"], "运行完整演示"),
    ]
    
    successful_demos = 0
    
    for cmd_args, description in demos:
        success = run_command(cmd_args, description)
        if success:
            successful_demos += 1
        
        print(f"状态: {'✅ 成功' if success else '❌ 失败'}")
        input("\n按Enter键继续下一个演示...")
    
    # 总结
    print(f"\n{'='*60}")
    print("📊 演示结果总结")
    print(f"{'='*60}")
    print(f"总演示数量: {len(demos)}")
    print(f"成功演示: {successful_demos}")
    print(f"失败演示: {len(demos) - successful_demos}")
    
    if successful_demos == len(demos):
        print("\n🎉 所有CLI功能演示成功!")
    else:
        print(f"\n⚠️ {len(demos) - successful_demos} 个演示失败")
    
    print("\n📖 更多用法请参考:")
    print("  python main.py --help")
    print("  python main.py <command> --help")

if __name__ == "__main__":
    main()