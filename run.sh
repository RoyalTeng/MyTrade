#!/bin/bash
# MyTrade Linux/macOS 启动脚本

echo "========================================"
echo "  MyTrade 量化交易系统"
echo "========================================"
echo

# 检查Python是否存在
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请确保Python3已安装"
    exit 1
fi

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 设置环境变量
export PYTHONPATH="$SCRIPT_DIR/src:$PYTHONPATH"

# 运行主程序
echo "启动MyTrade..."
python3 main.py "$@"

exit_code=$?
if [ $exit_code -ne 0 ] && [ $# -eq 0 ]; then
    echo
    echo "程序已退出，退出码: $exit_code"
    read -p "按Enter键继续..."
fi

exit $exit_code