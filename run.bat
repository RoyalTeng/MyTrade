@echo off
REM MyTrade Windows 启动脚本

echo ========================================
echo   MyTrade 量化交易系统
echo ========================================
echo.

REM 检查Python是否存在
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请确保Python已安装并添加到PATH中
    pause
    exit /b 1
)

REM 设置环境变量
set PYTHONPATH=%cd%\src;%PYTHONPATH%

REM 运行主程序
echo 启动MyTrade...
python main.py %*

REM 如果程序退出且没有参数，暂停以显示错误信息
if "%1"=="" (
    echo.
    echo 程序已退出
    pause
)