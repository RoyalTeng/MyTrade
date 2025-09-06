# MyTrade 量化交易系统使用指南

## 🚀 系统启动方式

**推荐启动方式：**

### 1. 命令行启动（推荐）
```bash
python main.py --help
```
- ✅ **标准启动方式**
- 显示所有可用命令和选项
- 跨平台兼容

### 2. Unix/Linux系统
```bash
./run.sh
```
- 适用于Linux/MacOS系统
- 自动设置环境变量

### 3. Windows系统
```bash
python main.py [command] [options]
```
- 直接使用Python命令
- 无需额外脚本文件

## 📊 主要功能介绍

### 1. 演示功能 (Demo)
```bash
python main.py demo
```
**作用：** 运行完整的量化交易演示流程
**适用于：** 首次使用，了解系统capabilities

### 2. 交互式界面 (Interactive)
```bash
python main.py interactive
```
**作用：** 启动交互式操作界面
**适用于：** 实时操作和策略调试

### 3. 数据管理 (Data)
```bash
python main.py data --help
```
**作用：** 管理股票数据、更新数据源
**功能包括：**
- 数据源配置
- 数据更新和缓存管理
- 数据质量检查

### 4. 信号生成 (Signal)
```bash
python main.py signal --help
```
**作用：** 生成交易信号和买卖建议
**功能包括：**
- 技术分析信号
- 基本面分析信号
- 多因子综合信号

### 5. 回测功能 (Backtest)
```bash
python main.py backtest --help
```
**作用：** 历史数据回测验证策略
**功能包括：**
- 策略回测
- 收益分析
- 风险评估

### 6. 系统管理 (System)
```bash
python main.py system --help
```
**作用：** 系统配置和管理
**功能包括：**
- 系统配置
- 日志管理
- 性能监控

## 🎯 A股投资分析功能

我们已经为您准备了专门的A股投资分析功能：

### 运行投资分析
```bash
python test/analyze_market_for_investment.py
```

### 查看分析报告
生成的报告位置：
```
reports/A股投资建议报告_10000元本金20%收益目标_20250906.md
```

**分析内容包括：**
- 📈 实时市场行情分析
- 🎯 10只精选投资标的
- 💰 详细仓位配置建议
- ⚠️ 风险管理策略
- 📊 20%收益目标达成路径

## 🔧 系统配置

### Python环境
- ✅ **已检测到：** Python 3.13.5
- ✅ **状态：** 正常运行

### 数据源配置
系统集成了双数据源：
- **Tushare Pro**: 专业级金融数据
- **AKShare**: 开源金融数据
- **智能切换**: 自动备用机制

### 项目结构
```
MyTrade/
├── main.py                    # 主程序入口
├── src/                       # 源代码目录
│   ├── mytrade/              # 核心业务逻辑
│   └── data/                 # 数据管理模块
├── test/                     # 测试脚本目录
│   ├── demo_cli.py           # CLI演示脚本
│   ├── interactive.py        # 交互式界面
│   └── analyze_*.py          # 各类分析脚本
├── data/                     # 数据存储目录
├── reports/                  # 分析报告目录
├── configs/                  # 配置文件目录
├── logs/                     # 日志文件目录
└── run.sh                    # Unix启动脚本
```

## 🚀 快速上手指南

### 第一步：查看系统帮助
```bash
python main.py --help
```

### 第二步：运行演示
```bash
python main.py demo
```

### 第三步：查看投资分析
```bash
python test/analyze_market_for_investment.py
```

### 第四步：探索交互模式
```bash
python main.py interactive
```

### 第五步：体验各项功能
```bash
# 数据管理
python main.py data --help

# 信号生成
python main.py signal --help

# 回测功能  
python main.py backtest --help

# 系统管理
python main.py system --help
```

## 💡 使用建议

### 初次使用
1. **运行演示**：了解系统基本功能
2. **查看投资报告**：体验实际应用价值
3. **尝试交互模式**：熟悉操作界面

### 日常使用
1. **数据管理**：定期更新市场数据
2. **信号生成**：获取交易信号
3. **策略回测**：验证投资策略

### 高级应用
1. **自定义策略**：开发个人交易策略
2. **系统配置**：优化系统参数
3. **API集成**：连接实际交易接口

## ❓ 常见问题

### Q: 如何查看完整的命令帮助？
A: 运行 `python main.py --help` 或使用菜单选项

### Q: 数据从哪里来？
A: 系统使用Tushare Pro和AKShare获取真实市场数据

### Q: 能否实盘交易？
A: 当前版本主要用于分析和回测，实盘需要额外配置

### Q: 如何更新股票数据？
A: 使用 `python main.py data` 命令管理数据

## 📞 支持信息

- **系统版本**: MyTrade v1.0
- **Python版本**: 3.13.5 (已验证)
- **数据源**: Tushare Pro + AKShare
- **支持市场**: A股、港股、美股

## 🎉 开始使用

现在您可以直接使用命令行开始使用MyTrade系统：

### 基础命令
```bash
# 查看帮助
python main.py --help

# 运行演示
python main.py demo

# 启动交互模式
python main.py interactive

# 查看投资分析
python test/analyze_market_for_investment.py
```

### 进阶使用
```bash
# 配置详细输出
python main.py -v demo

# 启用调试模式
python main.py --debug interactive

# 指定配置文件
python main.py -c config.yaml data
```

祝您使用愉快，投资顺利！ 🚀📈