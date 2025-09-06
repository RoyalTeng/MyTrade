#!/usr/bin/env python3
"""
MyTrade 交互式启动脚本

直接启动交互式界面的便捷脚本
"""

import sys
import os
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def main():
    """启动交互式界面"""
    print("=" * 60)
    print("[MyTrade] 量化交易系统")
    print("=" * 60)
    
    try:
        from mytrade.cli import cli
        
        # 直接调用交互式界面
        import click
        ctx = click.Context(cli)
        
        # 初始化配置
        try:
            from mytrade import get_config_manager
            config_manager = get_config_manager('config.yaml')
            ctx.obj = {
                'config_manager': config_manager,
                'config': config_manager.get_config()
            }
            print("[OK] 系统配置加载成功")
        except Exception as e:
            print(f"[WARNING] 配置加载失败，使用默认配置: {e}")
            ctx.obj = {'config': None}
        
        # 启动交互式界面
        print("\n启动交互式界面...")
        print("输入 'help' 查看可用命令，输入 'exit' 退出")
        
        interactive_shell(ctx)
        
    except ImportError as e:
        print(f"[ERROR] 导入失败: {e}")
        print("请确保在正确的conda环境中运行：conda activate myTrade")
        return 1
    except Exception as e:
        print(f"[ERROR] 启动失败: {e}")
        return 1
    
    return 0

def interactive_shell(ctx):
    """交互式命令行界面"""
    print("\n" + "=" * 50)
    print("MyTrade 交互式界面")
    print("=" * 50)
    print("可用命令：")
    print("  demo [symbol]     - 完整演示流程")
    print("  signal [symbol]   - 生成交易信号")
    print("  info              - 系统信息")
    print("  help              - 显示帮助")
    print("  exit              - 退出程序")
    print("=" * 50)
    
    while True:
        try:
            user_input = input("\nMyTrade> ").strip()
            
            if not user_input:
                continue
                
            parts = user_input.split()
            command = parts[0].lower()
            
            if command in ['exit', 'quit', 'q']:
                print("[INFO] 感谢使用MyTrade系统！再见！")
                break
                
            elif command == 'help':
                show_help()
                
            elif command == 'demo':
                symbol = parts[1] if len(parts) > 1 else '000001'
                run_demo(symbol)
                
            elif command == 'signal':
                symbol = parts[1] if len(parts) > 1 else '000001'
                run_signal(symbol)
                
            elif command == 'info':
                show_info()
                
            elif command == 'cls' or command == 'clear':
                os.system('cls' if os.name == 'nt' else 'clear')
                
            else:
                print(f"[ERROR] 未知命令: {command}")
                print("输入 'help' 查看可用命令")
                
        except KeyboardInterrupt:
            print("\n[INFO] 按 Ctrl+C 退出，或输入 'exit' 退出")
        except EOFError:
            print("\n[INFO] 感谢使用MyTrade系统！")
            break
        except Exception as e:
            print(f"[ERROR] 执行命令时出错: {e}")

def show_help():
    """显示帮助信息"""
    print("\n=== MyTrade 命令帮助 ===")
    print("[DEMO] demo [symbol]      - 运行完整演示流程 (默认: 000001)")
    print("[SIGNAL] signal [symbol]    - 生成智能交易信号 (默认: 000001)")
    print("[INFO] info              - 显示系统信息")
    print("[HELP] help              - 显示此帮助信息")
    print("[EXIT] exit/quit/q       - 退出交互界面")
    print("[CLEAR] cls/clear         - 清屏")
    print("\n例如：")
    print("  demo 600519        - 演示贵州茅台")
    print("  signal 000002      - 分析万科A")

def run_demo(symbol):
    """运行演示"""
    print(f"\n[DEMO] 运行完整演示流程，股票代码: {symbol}")
    try:
        # 直接调用CLI命令
        os.system(f'python main.py demo --symbol {symbol}')
    except Exception as e:
        print(f"[ERROR] 演示失败: {e}")

def run_signal(symbol):
    """运行信号生成"""
    print(f"\n[SIGNAL] 生成交易信号，股票代码: {symbol}")
    try:
        # 直接调用CLI命令
        os.system(f'python main.py signal generate {symbol}')
    except Exception as e:
        print(f"[ERROR] 信号生成失败: {e}")

def show_info():
    """显示系统信息"""
    print(f"\n[INFO] 系统信息")
    try:
        os.system('python main.py system info')
    except Exception as e:
        print(f"[ERROR] 获取系统信息失败: {e}")

if __name__ == "__main__":
    sys.exit(main())