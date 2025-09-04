# P0 优先级项目实施计划

> 基于TradingAgents企业级架构的关键正确性与契约保障

## 🎯 总体目标

建立系统的**正确性基石**，确保MyTrade系统符合生产环境的安全性、合规性和可靠性要求。

---

## 📋 项目列表 (按依赖关系排序)

### 项目1️⃣: 统一Agent协议与输出规范 (估期: 5-7天)

**目标**: 建立标准化的智能体输出协议，为后续所有Agent功能奠定基础

**技术范围**:
- 定义 `AgentOutput` 统一数据结构
- 重构现有4个分析师符合新协议
- 建立Agent基础测试框架

**交付物**:
```python
# src/mytrade/agents/protocols.py
from typing import TypedDict, Literal, Optional, Dict, Any

class AgentOutput(TypedDict):
    role: Literal["Fundamentals","Sentiment","News","Technical","Bull","Bear","Trader","Risk","PM"]
    ts: str                          # ISO时间戳
    symbol: str                      # 股票代码  
    score: Optional[float]           # 量化分数 0-1
    decision: Optional[Dict[str, Any]] # 决策信息 (仅Trader/Risk/PM)
    features: Dict[str, Any]         # 关键指标
    rationale: str                   # 自然语言解释(<300字)
    confidence: float                # 置信度 0-1
    metadata: Dict[str, Any]         # 元数据(版本、模型等)
```

**验收标准(DoD)**:
- ✅ 所有现有Agent输出符合AgentOutput协议
- ✅ 每个Agent有独立单元测试(mock输入→协议输出)
- ✅ 协议兼容性测试通过
- ✅ 文档完整(接口说明+示例)

---

### 项目2️⃣: 数据统一模式与验证 (估期: 4-5天)

**目标**: 建立统一的市场数据格式标准，确保数据质量和一致性

**技术范围**:
- 标准化DataFrame格式(时区、列名、索引)
- 数据验证与清洗管道
- 异常数据处理策略
- 多数据源适配统一

**交付物**:
```python
# src/mytrade/data/schemas.py
class MarketDataFrame(BaseModel):
    """标准市场数据格式"""
    index: DatetimeIndex    # Asia/Shanghai时区
    columns: ["open","high","low","close","volume","amount"]
    freq: Literal["D","H","30min","15min","5min","1min"]
    adjust: Literal["none","forward","backward"]
    
def validate_market_frame(df: pd.DataFrame) -> MarketDataFrame:
    """数据验证函数"""
    # 时区检查、缺失值检测、异常值识别
    pass
```

**验收标准(DoD)**:
- ✅ 统一数据验证函数，覆盖5+测试用例
- ✅ 所有数据入口调用验证函数
- ✅ 异常数据处理策略可配置(修复/忽略/中止)
- ✅ 支持akshare/tushare数据源标准化

---

### 项目3️⃣: A股交易日历与停牌检测 (估期: 3-4天)

**目标**: 实现严格的交易时间合规性控制

**技术范围**:
- A股交易日历(节假日、休市)
- 停牌股票检测与处理
- 交易时间窗口验证
- 异常交易日志记录

**交付物**:
```python
# src/mytrade/calendar/cn_calendar.py
def is_trading_day(date: str) -> bool:
    """判断是否为A股交易日"""
    
def next_trading_day(date: str) -> str:
    """获取下一个交易日"""
    
def detect_suspension(symbol: str, date: str) -> bool:
    """检测股票是否停牌"""
    
# logs/trade/anomalies.csv - 异常交易记录
```

**验收标准(DoD)**:
- ✅ 交易日历覆盖2020-2030年，包含所有法定节假日
- ✅ 停牌检测准确率>95%(基于历史数据验证)
- ✅ 回测中非交易日不触发执行
- ✅ 异常情况记录完整审计日志

---

### 项目4️⃣: 前视泄漏防护机制 (估期: 4-5天)

**目标**: 建立时间序列数据安全机制，防止未来数据泄漏

**技术范围**:
- 信号生成时间点严格控制
- T+1开盘执行机制
- 前视泄漏检测与告警
- 数据时间戳验证

**交付物**:
```python
# src/mytrade/guards/temporal_guard.py
class TemporalGuard:
    def validate_signal_timing(self, signal_ts: str, market_data_end: str) -> bool:
        """验证信号时间不超前于数据时间"""
        
    def enforce_execution_rule(self, rule: Literal["next_open","next_close","vwap"]):
        """强制执行规则：T+1开盘成交"""
        
# 前视泄漏单元测试
def test_future_data_leak_detection():
    """构造未来数据窥探情形，必须检测并失败"""
```

**验收标准(DoD)**:
- ✅ 信号时间戳 ≤ 执行bar.open_time 强制约束
- ✅ 前视泄漏单元测试100%覆盖
- ✅ 违规信号自动丢弃/顺延并记录日志
- ✅ 支持next_open/next_close/vwap执行规则

---

### 项目5️⃣: 精确费用模型 (估期: 2-3天)

**目标**: 建立精确的A股交易成本模型

**技术范围**:
- 佣金(万分之几，最低5元)
- 印花税(千分之一，卖出单边)
- 过户费(沪市万分之0.2)
- 滑点模型(可配置)

**交付物**:
```python
# src/mytrade/costs/fee_calculator.py
class FeeCalculator:
    def calculate_total_cost(
        self, 
        symbol: str,
        action: Literal["BUY","SELL"], 
        shares: int, 
        price: float,
        config: FeeConfig
    ) -> Dict[str, float]:
        """返回: {commission, stamp_duty, transfer_fee, slippage, total}"""
```

**验收标准(DoD)**:
- ✅ 费用计算精确到分，符合A股规则
- ✅ 支持券商费率差异化配置
- ✅ 所有交易成本计入净值曲线
- ✅ 费用明细可追溯审计

---

## 🚀 实施时间表

```
Week 1: 项目1(统一协议) + 项目2(数据模式) 
Week 2: 项目3(交易日历) + 项目4(防护机制)
Week 3: 项目5(费用模型) + 集成测试 + 文档

总计: 18-24工作日
```

## 📊 里程碑检查点

### Checkpoint 1 (第1周末)
- [ ] AgentOutput协议定义完成
- [ ] 现有4个Agent重构完成  
- [ ] 数据验证管道就绪
- [ ] 单元测试覆盖率>80%

### Checkpoint 2 (第2周末) 
- [ ] 交易日历功能完整
- [ ] 前视泄漏防护生效
- [ ] 集成测试通过
- [ ] 异常处理机制验证

### Checkpoint 3 (第3周末)
- [ ] 费用模型精确计算
- [ ] 端到端验证通过
- [ ] 性能回归测试
- [ ] 生产就绪文档

## ⚠️  风险缓解

1. **时间风险**: 每个项目预留20%缓冲时间
2. **技术风险**: 关键模块提前POC验证
3. **数据风险**: 建立多套测试数据集
4. **集成风险**: 每日构建+回归测试

---

## 🎯 成功标准

**技术指标**:
- 所有P0项目100%交付
- 单元测试覆盖率>85%
- 集成测试通过率100%
- 性能无明显回归

**业务指标**:
- 回测准确性提升(费用模型精确化)
- 合规性保障(交易日历+停牌)
- 数据质量提升(统一验证)
- 系统可信度增强(前视泄漏防护)

---

## 👥 建议团队配置

- **架构师 1人**: 统一协议设计+技术决策
- **核心开发 2人**: 各项目并行开发  
- **测试工程师 1人**: 单元测试+集成测试+性能测试
- **产品 1人**: 需求澄清+验收标准制定

**预估总工作量**: 60-80人天

---

是否开始实施第一个项目：**统一Agent协议与输出规范**？