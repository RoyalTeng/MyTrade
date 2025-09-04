# MyTrade - 基于TradingAgents的量化交易系统

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()

一个本地部署的智能量化交易系统，利用TradingAgents多智能体LLM框架为A股市场进行智能分析和交易决策。

## 🌟 主要特性

- **🧠 多智能体分析**: 集成TradingAgents框架，提供技术分析、基本面分析、情绪分析等多维度智能分析
- **📊 本地数据管理**: 支持AkShare和Tushare数据源，本地缓存机制，确保数据获取稳定高效
- **🔄 完整回测引擎**: 内置专业回测系统，支持多种交易策略和绩效分析
- **📝 可解释性日志**: 记录完整的决策推理过程，提供人类可读的分析报告
- **💻 友好命令行**: 丰富的CLI命令，支持批量操作和自动化脚本
- **⚙️ 模块化设计**: 松耦合架构，易于扩展和定制
- **🔒 本地部署**: 完全本地运行，保护数据隐私和交易安全

## 🏗️ 系统架构

```
MyTrade/
├── 配置管理层      # 参数配置和环境管理
├── 数据获取层      # 行情数据采集与缓存
├── 信号生成层      # TradingAgents多智能体分析
├── 交易执行层      # 回测和模拟交易引擎
├── 日志记录层      # 可解释性决策日志
└── 命令行界面      # CLI工具和自动化脚本
```

## 🚀 快速开始

### 环境要求

- Python 3.11+
- 操作系统: Windows / macOS / Linux
- 内存: 建议8GB以上
- 磁盘: 至少2GB可用空间

### 安装步骤

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd myTrade
   ```

2. **安装依赖**
   ```bash
   # 使用Poetry (推荐)
   pip install poetry
   poetry install
   
   # 或使用pip
   pip install -r requirements.txt
   ```

3. **配置系统**
   ```bash
   # 复制配置模板
   cp config.yaml.template config.yaml
   
   # 编辑配置文件，填入必要参数
   vim config.yaml  # 或使用其他编辑器
   ```

4. **运行测试**
   ```bash
   # Windows
   run.bat system health
   
   # macOS/Linux  
   ./run.sh system health
   ```

### 配置说明

编辑 `config.yaml` 文件，主要配置项：

```yaml
data:
  source: "akshare"  # 数据源: akshare 或 tushare
  tushare_token: "your_token_here"  # Tushare用户需填写token
  
trading_agents:
  openai_api_key: "your_openai_key"  # OpenAI API密钥 (可选)
  model_fast: "gpt-3.5-turbo"       # 快速模型
  model_deep: "gpt-4"               # 深度分析模型
```

## 📖 使用指南

### 命令行工具

MyTrade 提供丰富的CLI命令：

```bash
# 显示帮助
python main.py --help

# 系统状态检查
python main.py system health
python main.py system info

# 数据管理
python main.py data stocks                    # 获取股票列表
python main.py data fetch 600519 --days 30    # 获取历史数据

# 信号生成
python main.py signal generate 600519         # 生成单个信号
python main.py signal batch 600519 000001     # 批量生成信号

# 回测分析
python main.py backtest run \
  --start-date 2024-01-01 \
  --end-date 2024-12-31 \
  --symbols "600519,000001,000002" \
  --initial-cash 1000000

# 运行演示
python main.py demo --symbol 600519
```

### Python API 使用

```python
from mytrade import (
    get_config_manager, MarketDataFetcher, 
    SignalGenerator, BacktestEngine
)

# 1. 加载配置
config_manager = get_config_manager("config.yaml")
config = config_manager.get_config()

# 2. 获取市场数据
fetcher = MarketDataFetcher(config.data)
data = fetcher.fetch_history("600519", "2024-01-01", "2024-12-31")

# 3. 生成交易信号
generator = SignalGenerator(config)
report = generator.generate_signal("600519")
print(f"信号: {report.signal.action}, 置信度: {report.signal.confidence}")

# 4. 运行回测
from mytrade.backtest import BacktestConfig
engine = BacktestEngine(config)
result = engine.run_backtest(BacktestConfig(
    start_date="2024-01-01",
    end_date="2024-12-31", 
    symbols=["600519"],
    initial_cash=1000000
))
print(f"回测收益率: {result.portfolio_summary['total_return']:.2%}")
```

## 📊 功能模块详解

### 1. 数据管理 (`mytrade.data`)

- **数据源支持**: AkShare (免费) 和 Tushare (需注册)
- **智能缓存**: 自动缓存历史数据，避免重复请求
- **数据标准化**: 统一的数据格式和字段命名
- **异常处理**: 网络异常重试和数据验证

```python
from mytrade.data import MarketDataFetcher, DataSourceConfig

# 配置数据源
config = DataSourceConfig(source="akshare", cache_dir="data/cache")
fetcher = MarketDataFetcher(config)

# 获取股票列表
stocks = fetcher.get_stock_list()

# 获取历史数据  
data = fetcher.fetch_history("600519", "2024-01-01", "2024-12-31")
```

### 2. 信号生成 (`mytrade.trading`)

- **多智能体分析**: 技术分析师、基本面分析师、情绪分析师等
- **协同决策**: 多个AI智能体协作生成最终交易信号
- **置信度评估**: 每个信号都有相应的置信度分数
- **详细分析**: 提供完整的分析过程和推理逻辑

```python
from mytrade.trading import SignalGenerator

generator = SignalGenerator()
report = generator.generate_signal("600519")

# 查看信号详情
signal = report.signal
print(f"动作: {signal.action}")
print(f"数量: {signal.volume}")  
print(f"置信度: {signal.confidence}")
print(f"原因: {signal.reason}")

# 查看详细分析
for analysis in report.detailed_analyses:
    print(f"智能体: {analysis['agent']}")
    print(f"结论: {analysis['conclusion']}")
```

### 3. 回测引擎 (`mytrade.backtest`)

- **投资组合管理**: 现金管理、持仓跟踪、交易执行
- **交易成本**: 考虑手续费、滑点等真实交易成本
- **绩效分析**: 收益率、夏普比率、最大回撤等指标
- **结果导出**: CSV、JSON格式结果文件

```python
from mytrade.backtest import BacktestEngine, BacktestConfig

# 配置回测参数
config = BacktestConfig(
    start_date="2024-01-01",
    end_date="2024-12-31",
    initial_cash=1000000,
    symbols=["600519", "000001", "000002"],
    max_positions=5,
    position_size_pct=0.2
)

# 运行回测
engine = BacktestEngine()
result = engine.run_backtest(config)

# 查看结果
print(f"总收益率: {result.portfolio_summary['total_return']:.2%}")
print(f"夏普比率: {result.performance_metrics['sharpe_ratio']:.2f}")
print(f"最大回撤: {result.performance_metrics['max_drawdown']:.2%}")
```

### 4. 可解释日志 (`mytrade.logging`)

- **分析步骤记录**: 记录每个智能体的分析过程
- **决策点追踪**: 关键决策的选择理由和置信度
- **多格式输出**: 文本日志、JSON数据、Markdown报告
- **历史查询**: 支持历史决策过程的回溯分析

```python
from mytrade.logging import InterpretableLogger, AgentType

logger = InterpretableLogger(log_dir="logs/interpretable")

# 开始交易会话
session_id = logger.start_trading_session("600519", "2024-01-15")

# 记录分析步骤
logger.log_analysis_step(
    agent_type=AgentType.TECHNICAL_ANALYST,
    input_data={"price_data": "..."},
    analysis_process="技术指标分析",
    conclusion="趋势向上",
    confidence=0.75,
    reasoning=["均线多头排列", "成交量放大"]
)

# 结束会话
summary = logger.end_trading_session(
    final_decision={"action": "BUY", "volume": 1000}
)
```

## 🧪 测试和验证

### 运行所有测试

```bash
# 运行完整测试套件
python run_tests.py

# 运行特定模块测试
python test/test_signal_generator.py
python test/test_backtest_engine.py
python test/test_full_system.py
```

### CLI功能演示

```bash
# 运行CLI功能演示
python demo_cli.py

# 运行快速演示
python main.py demo --symbol 600519
```

## 📁 项目结构

```
MyTrade/
├── src/mytrade/           # 源代码目录
│   ├── config/            # 配置管理模块
│   ├── data/              # 数据获取模块  
│   ├── trading/           # 信号生成模块
│   ├── backtest/          # 回测引擎模块
│   ├── logging/           # 日志记录模块
│   └── cli/               # 命令行界面
├── test/                  # 测试脚本目录
├── data/                  # 数据缓存目录
├── logs/                  # 日志输出目录
├── config.yaml            # 主配置文件
├── main.py                # 主程序入口
├── run.bat                # Windows启动脚本
├── run.sh                 # Linux/macOS启动脚本
└── README.md              # 项目文档
```

## ⚙️ 高级配置

### 配置文件详解

```yaml
# 数据源配置
data:
  source: "akshare"              # 数据源选择
  tushare_token: "${TUSHARE_TOKEN}"  # 环境变量支持
  cache_dir: "data/cache"        # 缓存目录
  cache_expire_hours: 24         # 缓存过期时间

# TradingAgents配置
trading_agents:
  model_fast: "gpt-3.5-turbo"    # 快速分析模型
  model_deep: "gpt-4"            # 深度分析模型
  use_online_data: false         # 是否使用在线数据
  debate_rounds: 2               # 智能体辩论轮数
  openai_api_key: "${OPENAI_API_KEY}"

# 回测配置
backtest:
  default_initial_cash: 1000000  # 默认初始资金
  default_commission_rate: 0.001 # 默认手续费率
  default_slippage_rate: 0.0005  # 默认滑点率

# 日志配置  
logging:
  level: "INFO"                  # 日志级别
  dir: "logs"                    # 日志目录
  max_file_size_mb: 100         # 最大文件大小
```

### 环境变量

在系统中设置以下环境变量：

```bash
# Windows
set TUSHARE_TOKEN=your_tushare_token_here
set OPENAI_API_KEY=your_openai_key_here

# Linux/macOS
export TUSHARE_TOKEN=your_tushare_token_here
export OPENAI_API_KEY=your_openai_key_here
```

## 🤝 贡献指南

我们欢迎各种形式的贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详细信息。

### 开发环境设置

1. Fork 项目并克隆到本地
2. 创建开发分支: `git checkout -b feature-name`
3. 安装开发依赖: `poetry install --dev`
4. 运行测试确保功能正常: `python run_tests.py`
5. 提交更改并创建Pull Request

### 代码规范

- 使用 Black 进行代码格式化
- 使用 Flake8 进行代码检查  
- 使用 isort 进行导入排序
- 添加类型注解和文档字符串
- 为新功能编写测试用例

## ❗ 风险声明

**重要提示**: 本系统仅用于学习和研究目的，不构成任何投资建议。

- 量化交易存在风险，历史表现不代表未来收益
- 请在充分了解风险的基础上使用本系统
- 实盘交易前请进行充分的回测和验证
- 作者和贡献者不承担任何投资损失责任

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

感谢以下开源项目和服务：

- [TradingAgents](https://github.com/trading-agents) - 多智能体LLM框架
- [AkShare](https://github.com/akfamily/akshare) - 金融数据接口
- [Tushare](https://tushare.pro/) - 金融数据服务
- [Click](https://click.palletsprojects.com/) - 命令行接口框架
- [Pydantic](https://pydantic-docs.helpmanual.io/) - 数据验证库

## 📞 联系我们

- 项目主页: [GitHub Repository](https://github.com/your-username/mytrade)
- 问题报告: [GitHub Issues](https://github.com/your-username/mytrade/issues)
- 邮箱: team@mytrade.com

---

⭐ 如果这个项目对您有帮助，请给我们一个Star！