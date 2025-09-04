# 开发指南

本文档为MyTrade项目的开发者提供详细的开发环境搭建和开发流程指导。

## 🏗️ 开发环境搭建

### 系统要求

- **Python**: 3.11或更高版本
- **操作系统**: Windows 10+, macOS 10.15+, Ubuntu 18.04+
- **内存**: 建议8GB以上
- **磁盘空间**: 至少2GB可用空间

### 开发工具

推荐使用以下开发工具：

- **IDE**: Visual Studio Code, PyCharm
- **终端**: Windows Terminal, iTerm2
- **Git**: 版本控制
- **Poetry**: 依赖管理 (推荐)

### 环境准备

1. **安装Python**
   ```bash
   # Windows: 从官网下载安装
   # macOS: 使用Homebrew
   brew install python@3.11
   
   # Ubuntu: 使用apt
   sudo apt update
   sudo apt install python3.11 python3.11-pip
   ```

2. **安装Poetry** (推荐)
   ```bash
   # 官方安装脚本
   curl -sSL https://install.python-poetry.org | python3 -
   
   # 或使用pip
   pip install poetry
   ```

3. **安装Git**
   ```bash
   # Windows: 从官网下载
   # macOS: 使用Xcode命令行工具
   xcode-select --install
   
   # Ubuntu
   sudo apt install git
   ```

### 项目设置

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd myTrade
   ```

2. **安装依赖**
   ```bash
   # 使用Poetry (推荐)
   poetry install --dev
   
   # 或使用pip
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

3. **激活虚拟环境**
   ```bash
   # Poetry
   poetry shell
   
   # 或手动激活
   # Windows
   .venv\Scripts\activate
   # macOS/Linux
   source .venv/bin/activate
   ```

4. **安装pre-commit钩子**
   ```bash
   pre-commit install
   ```

5. **验证安装**
   ```bash
   # 运行测试
   python run_tests.py
   
   # 检查命令行工具
   python main.py --help
   ```

## 📁 项目结构详解

```
MyTrade/
├── src/mytrade/              # 主要源代码
│   ├── __init__.py           # 包初始化
│   ├── config/               # 配置管理模块
│   │   ├── __init__.py
│   │   ├── config_manager.py # 配置管理器
│   │   └── models.py         # 配置数据模型
│   ├── data/                 # 数据获取模块
│   │   ├── __init__.py
│   │   ├── market_data_fetcher.py  # 数据获取器
│   │   └── mock_data.py      # 模拟数据
│   ├── trading/              # 信号生成模块
│   │   ├── __init__.py
│   │   ├── signal_generator.py     # 信号生成器
│   │   └── mock_trading_agents.py  # 模拟智能体
│   ├── backtest/             # 回测引擎模块
│   │   ├── __init__.py
│   │   ├── backtest_engine.py      # 回测引擎
│   │   └── portfolio_manager.py    # 投资组合管理
│   ├── logging/              # 日志记录模块
│   │   ├── __init__.py
│   │   └── interpretable_logger.py # 可解释性日志
│   └── cli/                  # 命令行接口
│       ├── __init__.py
│       └── main.py           # CLI主程序
├── test/                     # 测试文件
│   ├── test_config.py
│   ├── test_data_fetcher.py
│   ├── test_signal_generator.py
│   ├── test_backtest_engine.py
│   ├── test_interpretable_logger.py
│   └── test_full_system.py
├── data/                     # 数据目录
│   ├── cache/                # 数据缓存
│   └── mock/                 # 模拟数据
├── logs/                     # 日志目录
├── docs/                     # 文档目录
├── config.yaml               # 主配置文件
├── pyproject.toml            # Poetry项目配置
├── requirements.txt          # pip依赖文件
├── main.py                   # 程序入口
├── run.bat                   # Windows启动脚本
├── run.sh                    # Linux/macOS启动脚本
└── run_tests.py              # 测试运行器
```

## 🧪 开发和测试流程

### 代码开发

1. **创建功能分支**
   ```bash
   git checkout -b feature/new-feature
   ```

2. **编写代码**
   - 遵循项目的编码规范
   - 添加必要的类型注解
   - 编写详细的文档字符串

3. **运行测试**
   ```bash
   # 运行所有测试
   python run_tests.py
   
   # 运行特定测试
   python test/test_signal_generator.py
   ```

4. **代码质量检查**
   ```bash
   # 格式化代码
   black src/ test/
   
   # 排序导入
   isort src/ test/
   
   # 检查代码质量
   flake8 src/ test/
   
   # 类型检查
   mypy src/
   ```

### 测试指南

#### 单元测试

为新功能编写单元测试：

```python
import pytest
from mytrade.trading import SignalGenerator

def test_signal_generator_initialization():
    """测试信号生成器初始化"""
    generator = SignalGenerator()
    assert generator is not None
    assert hasattr(generator, 'data_fetcher')

def test_signal_generation():
    """测试信号生成功能"""
    generator = SignalGenerator()
    report = generator.generate_signal("600519")
    
    assert report.symbol == "600519"
    assert report.signal.action in ["BUY", "SELL", "HOLD"]
    assert 0 <= report.signal.confidence <= 1
```

#### 集成测试

测试模块间的协作：

```python
def test_end_to_end_workflow():
    """测试端到端工作流程"""
    from mytrade import (
        get_config_manager, MarketDataFetcher, 
        SignalGenerator, PortfolioManager
    )
    
    # 加载配置
    config_manager = get_config_manager("config.yaml")
    config = config_manager.get_config()
    
    # 获取数据
    fetcher = MarketDataFetcher(config.data)
    data = fetcher.fetch_history("600519", "2024-01-01", "2024-01-31")
    
    # 生成信号
    generator = SignalGenerator(config)
    report = generator.generate_signal("600519")
    
    # 执行交易
    portfolio = PortfolioManager()
    success = portfolio.execute_trade(
        symbol="600519",
        action=report.signal.action,
        shares=100,
        price=45.0
    )
    
    assert success or report.signal.action == "HOLD"
```

### 调试技巧

1. **使用日志**
   ```python
   import logging
   
   logger = logging.getLogger(__name__)
   logger.debug("调试信息")
   logger.info("普通信息")
   logger.warning("警告信息")
   logger.error("错误信息")
   ```

2. **使用断点调试**
   ```python
   # 在代码中插入断点
   import pdb; pdb.set_trace()
   
   # 或使用breakpoint() (Python 3.7+)
   breakpoint()
   ```

3. **使用VS Code调试**
   - 设置断点
   - 使用F5启动调试
   - 查看变量和调用栈

## 🏗️ 架构设计

### 设计原则

1. **模块化**: 每个模块负责特定功能，接口清晰
2. **松耦合**: 模块间通过接口交互，降低依赖
3. **可测试**: 所有组件都可以独立测试
4. **可扩展**: 易于添加新功能和数据源
5. **错误处理**: 完善的异常处理和错误恢复

### 核心组件

#### 配置管理 (`config`)
- 统一的配置管理接口
- 支持环境变量和配置文件
- 配置验证和热重载

#### 数据层 (`data`)
- 抽象的数据源接口
- 多数据源支持
- 缓存和数据标准化

#### 交易逻辑 (`trading`)
- TradingAgents集成
- 信号生成和验证
- 批量处理支持

#### 回测引擎 (`backtest`)
- 投资组合状态管理
- 交易执行模拟
- 绩效指标计算

#### 日志系统 (`logging`)
- 结构化日志记录
- 多格式输出支持
- 历史数据查询

### 数据流

```
配置文件 → 配置管理器 → 各模块配置
                    ↓
市场数据源 → 数据获取器 → 本地缓存 → 信号生成器
                                        ↓
                    回测引擎 ← 交易信号
                        ↓
                    投资组合管理器 → 交易记录
                        ↓
                    绩效分析 → 报告生成
```

## 🔧 配置和部署

### 开发环境配置

1. **创建开发配置**
   ```yaml
   # config.dev.yaml
   data:
     source: "akshare"
     cache_dir: "data/cache"
     cache_expire_hours: 1  # 开发环境快速过期
   
   logging:
     level: "DEBUG"
     dir: "logs/dev"
   
   trading_agents:
     model_fast: "gpt-3.5-turbo"
     use_online_data: false
   ```

2. **设置环境变量**
   ```bash
   # 创建 .env 文件
   echo "OPENAI_API_KEY=your_key_here" > .env
   echo "TUSHARE_TOKEN=your_token_here" >> .env
   ```

### 生产环境部署

1. **安装生产依赖**
   ```bash
   poetry install --no-dev
   ```

2. **生产配置**
   ```yaml
   # config.prod.yaml
   logging:
     level: "INFO"
     max_file_size_mb: 100
   
   data:
     cache_expire_hours: 24
   ```

3. **启动服务**
   ```bash
   # Linux系统服务
   sudo systemctl start mytrade
   
   # 或直接运行
   python main.py --config config.prod.yaml
   ```

## 📈 性能优化

### 数据获取优化

1. **批量请求**
   ```python
   # 批量获取多只股票数据
   symbols = ["600519", "000001", "000002"]
   data_batch = fetcher.fetch_batch(symbols, start_date, end_date)
   ```

2. **缓存策略**
   ```python
   # 智能缓存更新
   if cache_expired or force_update:
       data = fetch_from_source()
       save_to_cache(data)
   else:
       data = load_from_cache()
   ```

### 计算优化

1. **使用NumPy和Pandas**
   ```python
   # 向量化计算
   returns = (data['close'] / data['close'].shift(1) - 1).dropna()
   volatility = returns.rolling(20).std()
   ```

2. **并发处理**
   ```python
   from concurrent.futures import ThreadPoolExecutor
   
   with ThreadPoolExecutor(max_workers=4) as executor:
       results = executor.map(generate_signal, symbols)
   ```

## 🐛 常见问题

### 环境问题

**Q: Poetry安装失败**
```bash
# 解决方案：使用官方安装脚本
curl -sSL https://install.python-poetry.org | python3 -
```

**Q: 依赖冲突**
```bash
# 清理并重新安装
poetry env remove python
poetry install
```

### 运行问题

**Q: 数据获取失败**
- 检查网络连接
- 验证API token
- 查看错误日志

**Q: 测试失败**
- 确保所有依赖已安装
- 检查配置文件是否正确
- 查看具体错误信息

### 性能问题

**Q: 程序运行缓慢**
- 启用数据缓存
- 调整批处理大小
- 检查系统资源使用

## 📚 相关资源

### 文档
- [Python官方文档](https://docs.python.org/)
- [Poetry文档](https://python-poetry.org/docs/)
- [Pandas文档](https://pandas.pydata.org/docs/)

### 数据源
- [AkShare文档](https://akshare.akfamily.xyz/)
- [Tushare文档](https://tushare.pro/document/2)

### 开发工具
- [Black代码格式化](https://black.readthedocs.io/)
- [Flake8代码检查](https://flake8.pycqa.org/)
- [mypy类型检查](https://mypy.readthedocs.io/)

---

如有其他问题，请参考项目文档或提交Issue。