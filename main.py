#!/usr/bin/env python3
"""
MyTrade 主启动脚本

用于启动MyTrade量化交易系统的主程序。
"""

import sys
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

if __name__ == "__main__":
    from mytrade.cli import cli
    cli()