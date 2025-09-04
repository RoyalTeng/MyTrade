# 贡献指南

感谢您对MyTrade项目的关注！我们欢迎各种形式的贡献，包括但不限于：

- 🐛 Bug报告和修复
- ✨ 新功能开发
- 📖 文档改进
- 🧪 测试用例编写
- 💡 功能建议和讨论

## 🚀 快速开始

### 1. 环境准备

确保您的开发环境满足以下要求：

- Python 3.11+
- Git
- Poetry (推荐) 或 pip

### 2. 获取代码

```bash
# Fork项目到您的GitHub账户
# 然后克隆您的Fork

git clone https://github.com/YOUR_USERNAME/mytrade.git
cd mytrade

# 添加上游仓库
git remote add upstream https://github.com/ORIGINAL_OWNER/mytrade.git
```

### 3. 设置开发环境

```bash
# 使用Poetry安装依赖 (推荐)
poetry install --dev

# 或者使用pip
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 安装pre-commit钩子
pre-commit install
```

### 4. 运行测试

```bash
# 运行所有测试
python run_tests.py

# 运行特定测试
python test/test_signal_generator.py

# 检查代码质量
flake8 src/
black --check src/
isort --check-only src/
```

## 📋 开发流程

### 1. 创建功能分支

```bash
# 从主分支创建新分支
git checkout main
git pull upstream main
git checkout -b feature/your-feature-name

# 或者修复bug
git checkout -b fix/bug-description
```

### 2. 开发和测试

- 在相应的模块中添加或修改代码
- 确保代码符合项目的编码规范
- 添加必要的测试用例
- 更新相关文档

### 3. 提交代码

```bash
# 添加修改的文件
git add .

# 提交代码 (使用清晰的提交信息)
git commit -m "feat: add new trading signal algorithm"

# 或者修复bug
git commit -m "fix: resolve data fetching timeout issue"
```

### 4. 推送和创建Pull Request

```bash
# 推送到您的Fork
git push origin feature/your-feature-name

# 在GitHub上创建Pull Request
```

## 🎯 代码规范

### Python编码风格

我们使用以下工具来保持代码质量：

- **Black**: 代码格式化
- **Flake8**: 代码检查
- **isort**: 导入排序
- **mypy**: 类型检查

### 代码格式化

```bash
# 格式化代码
black src/ test/

# 排序导入
isort src/ test/

# 检查代码质量
flake8 src/ test/
mypy src/
```

### 提交信息规范

使用约定式提交格式：

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

类型 (type):
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更改
- `style`: 代码格式修改
- `refactor`: 重构代码
- `test`: 添加测试
- `chore`: 构建过程或辅助工具的变动

示例：
```
feat(trading): add momentum-based signal generator
fix(data): resolve akshare API timeout issue
docs(readme): update installation instructions
```

### 代码注释和文档

- 所有公共函数必须有详细的文档字符串
- 复杂逻辑需要添加注释说明
- 使用类型注解提高代码可读性

```python
def generate_signal(
    self, 
    symbol: str, 
    target_date: Optional[Union[str, date]] = None,
    lookback_days: int = 30,
    force_update: bool = False
) -> AnalysisReport:
    """
    为指定股票生成交易信号
    
    Args:
        symbol: 股票代码
        target_date: 目标日期，默认为当前日期
        lookback_days: 回看天数，用于获取历史数据
        force_update: 是否强制更新数据
    
    Returns:
        分析报告对象，包含交易信号和详细分析
        
    Raises:
        ValueError: 当股票代码无效或数据获取失败时
    """
```

## 🧪 测试指南

### 测试结构

```
test/
├── test_config.py              # 配置管理测试
├── test_data_fetcher.py        # 数据获取测试
├── test_signal_generator.py    # 信号生成测试
├── test_backtest_engine.py     # 回测引擎测试
├── test_interpretable_logger.py # 日志记录测试
├── test_full_system.py         # 系统集成测试
└── conftest.py                 # 测试配置和fixture
```

### 编写测试

- 为新功能编写对应的测试用例
- 测试应该覆盖正常情况和异常情况
- 使用mock来隔离外部依赖
- 测试函数命名要清晰描述测试目的

```python
def test_signal_generator_basic_functionality():
    """测试信号生成器的基本功能"""
    generator = SignalGenerator()
    report = generator.generate_signal("600519")
    
    assert report.symbol == "600519"
    assert report.signal.action in ["BUY", "SELL", "HOLD"]
    assert 0 <= report.signal.confidence <= 1
    assert len(report.detailed_analyses) > 0

def test_signal_generator_invalid_symbol():
    """测试信号生成器处理无效股票代码的情况"""
    generator = SignalGenerator()
    
    with pytest.raises(ValueError, match="Invalid symbol"):
        generator.generate_signal("INVALID")
```

### 运行测试

```bash
# 运行所有测试
python run_tests.py

# 运行特定测试文件
python -m pytest test/test_signal_generator.py -v

# 运行特定测试函数
python -m pytest test/test_signal_generator.py::test_basic_functionality -v

# 生成测试覆盖率报告
python -m pytest --cov=src/mytrade test/
```

## 📖 文档贡献

### 文档类型

- **README.md**: 项目总览和快速开始
- **API文档**: 模块和函数的详细说明
- **教程**: 使用示例和最佳实践
- **开发文档**: 架构设计和开发指南

### 文档编写规范

- 使用清晰简洁的语言
- 提供完整的代码示例
- 保持文档与代码同步更新
- 使用Markdown格式

## 🐛 问题报告

### 报告Bug

在提交Bug报告前，请：

1. 检查是否已有相似问题
2. 尝试使用最新版本重现问题
3. 收集必要的错误信息和日志

Bug报告应包含：

- **问题描述**: 清晰描述遇到的问题
- **重现步骤**: 详细的重现步骤
- **预期行为**: 您期望的正确行为
- **实际行为**: 实际发生的情况
- **环境信息**: Python版本、操作系统等
- **错误信息**: 完整的错误堆栈信息

### 功能建议

功能建议应包含：

- **用例描述**: 为什么需要这个功能
- **建议方案**: 您希望如何实现
- **替代方案**: 其他可能的实现方式
- **相关资源**: 相关文档或参考资料

## 📋 发布流程

### 版本号规范

使用语义化版本号 (Semantic Versioning):

- **主版本号**: 不兼容的API修改
- **次版本号**: 向后兼容的功能性新增
- **修订版本号**: 向后兼容的bug修复

### 发布检查清单

发布前确保：

- [ ] 所有测试通过
- [ ] 文档已更新
- [ ] CHANGELOG已更新
- [ ] 版本号已更新
- [ ] 创建发布标签

## 🤝 行为准则

### 我们的承诺

为了营造一个开放和友好的环境，我们承诺：

- 尊重不同的观点和经验
- 接受建设性的批评
- 关注对社区最有利的事情
- 对其他社区成员表示同理心

### 不当行为

不可接受的行为包括：

- 使用性化的语言或图像
- 人身攻击或侮辱/贬损的评论
- 公开或私下的骚扰
- 未经许可发布他人的私人信息

## 📞 获取帮助

如果您在贡献过程中遇到问题：

- 查看现有的Issues和文档
- 在GitHub上创建新的Issue
- 发送邮件到 team@mytrade.com
- 加入我们的讨论群组

## 🙏 感谢

感谢所有为MyTrade项目做出贡献的开发者！您的贡献让这个项目变得更好。

---

再次感谢您的贡献！🎉