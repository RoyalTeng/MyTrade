# Tushare数据源配置指南

## 📊 Tushare简介

Tushare是一个免费、开源的python财经数据接口包，主要实现对股票、期货等金融数据的便捷访问，为金融分析师、算法交易员、数据科学家提供专业的数据支持。

- **官网**: https://tushare.pro
- **文档**: https://tushare.pro/document/2
- **社区**: https://waditu.com

## 🚀 快速开始

### 第一步：注册账号

1. 访问 [https://tushare.pro/register](https://tushare.pro/register)
2. 注册账号并验证邮箱
3. 完成实名认证（需要上传身份证）
4. 实名认证通过后即可获得API Token

### 第二步：获取API Token

1. 登录Tushare Pro
2. 进入"用户中心" -> "接口权限" 
3. 复制您的Token（格式类似：`xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`）

### 第三步：安装依赖

```bash
# 安装tushare
pip install tushare

# 或者指定版本
pip install tushare>=1.2.89
```

### 第四步：配置Token

#### 方法1: 环境变量设置（推荐）

**Windows:**
```cmd
set TUSHARE_TOKEN=你的token值
```

**Linux/Mac:**
```bash
export TUSHARE_TOKEN=你的token值
```

**永久设置（Windows）:**
1. 右键"此电脑" -> "属性" -> "高级系统设置"
2. 点击"环境变量" 
3. 新建系统变量：
   - 变量名：`TUSHARE_TOKEN`
   - 变量值：你的token

#### 方法2: 代码中设置

```python
from unified_data_source import UnifiedDataSource

# 直接传入token
data_source = UnifiedDataSource(tushare_token="你的token")
```

## 📈 使用示例

### 基础用法

```python
#!/usr/bin/env python3
"""
Tushare数据源使用示例
"""

from tushare_data_source import TushareDataSource

# 初始化（自动读取环境变量中的token）
ts_source = TushareDataSource()

# 或者直接传入token
ts_source = TushareDataSource(token="你的token")

# 获取股票基本信息
stock_basic = ts_source.get_stock_basic()
print(f"获取{len(stock_basic)}只股票信息")

# 获取紫金矿业日线数据
daily_data = ts_source.get_daily_data('601899.SH', days=60)
print(f"获取{len(daily_data)}天数据")

# 计算技术指标
indicators = ts_source.calculate_technical_indicators(daily_data)
print(f"当前价格: {indicators['current_price']:.2f}元")
print(f"MA20: {indicators['ma20']:.2f}元")

# 获取财务数据
financial = ts_source.get_financial_data('601899.SH')
if financial.get('indicators'):
    print(f"ROE: {financial['indicators']['roe']:.2f}%")
```

### 统一数据源使用

```python
from unified_data_source import UnifiedDataSource

# 初始化统一数据源
data_source = UnifiedDataSource()

# 自动选择最佳数据源获取实时数据
realtime = data_source.get_stock_realtime('601899')
if realtime:
    print(f"{realtime['name']}: {realtime['current_price']:.2f}元")
    print(f"数据来源: {realtime['source']}")

# 获取历史数据（自动选择数据源）
hist_data, indicators = data_source.get_historical_data('601899', days=120)
print(f"历史数据: {len(hist_data)}天")
print(f"技术指标: MA5={indicators['ma5']:.2f}, MA20={indicators['ma20']:.2f}")
```

## 📊 数据类型说明

### 1. 股票数据

| 接口 | 说明 | 示例 |
|------|------|------|
| `stock_basic` | 股票基本信息 | 股票列表、上市日期等 |
| `daily` | 日线行情 | 开高低收、成交量等 |
| `weekly` | 周线行情 | 周K线数据 |
| `monthly` | 月线行情 | 月K线数据 |

### 2. 财务数据

| 接口 | 说明 | 数据内容 |
|------|------|----------|
| `income` | 利润表 | 营业收入、净利润等 |
| `balancesheet` | 资产负债表 | 总资产、总负债等 |
| `cashflow` | 现金流量表 | 经营/投资/筹资现金流 |
| `fina_indicator` | 财务指标 | ROE、ROA、负债率等 |

### 3. 指数数据

| 接口 | 说明 | 覆盖范围 |
|------|------|----------|
| `index_basic` | 指数基本信息 | 指数列表、基日等 |
| `index_daily` | 指数日线 | 上证、深证、创业板等 |

## ⚠️ 使用限制

### 免费用户限制

- **调用频率**: 每分钟200次
- **并发数**: 1个
- **数据权限**: 基础数据

### VIP用户权限

- **调用频率**: 每分钟400-2000次
- **并发数**: 2-5个  
- **数据权限**: 更多高级数据

### 积分规则

- 每天签到获得积分
- 分享获得积分
- 积分可兑换更多调用次数

## 🔧 常见问题

### Q1: Token无效怎么办？
**A**: 
1. 检查Token是否正确复制
2. 确认实名认证是否通过
3. 检查账号状态是否正常

### Q2: 调用频率超限？
**A**: 
1. 减少调用频率
2. 增加请求间隔
3. 考虑升级VIP

### Q3: 某些数据获取不到？
**A**: 
1. 检查股票代码格式（需要后缀.SH/.SZ）
2. 确认数据日期是否为交易日
3. 部分数据需要VIP权限

### Q4: 如何获取实时数据？
**A**: 
Tushare的"实时"数据实际是最新交易日数据，真正的实时数据需要：
1. 使用其他API补充
2. 结合多数据源策略
3. 我们的统一数据源会自动处理这个问题

## 📋 代码格式说明

### 股票代码格式
- **上海交易所**: `600000.SH`、`601899.SH`
- **深圳交易所**: `000001.SZ`、`300001.SZ`
- **转换示例**:
  ```python
  # 普通格式转Tushare格式
  def convert_code(code):
      if code.startswith('60'):
          return f"{code}.SH"
      else:
          return f"{code}.SZ"
  ```

### 日期格式
- **格式**: `YYYYMMDD`
- **示例**: `20250904`

## 🎯 最佳实践

### 1. 错误处理
```python
try:
    data = ts_source.get_daily_data('601899.SH')
    if data.empty:
        print("无数据返回")
except Exception as e:
    print(f"获取数据失败: {e}")
```

### 2. 频率控制
```python
import time

for code in stock_codes:
    data = ts_source.get_daily_data(f"{code}.SH")
    time.sleep(0.5)  # 避免频率限制
```

### 3. 数据缓存
```python
import pickle
from pathlib import Path

# 保存数据
def save_data(data, filename):
    with open(filename, 'wb') as f:
        pickle.dump(data, f)

# 加载数据
def load_data(filename):
    if Path(filename).exists():
        with open(filename, 'rb') as f:
            return pickle.load(f)
    return None
```

## 📞 技术支持

- **官方文档**: https://tushare.pro/document/2
- **QQ群**: 124134140
- **微信群**: 关注"Tushare"公众号加群
- **GitHub**: https://github.com/waditu/tushare

## 📄 许可证

Tushare遵循BSD开源协议，商业使用需要注意相关条款。

---

**⚠️ 重要提示**: 
1. 请遵守Tushare的使用协议
2. 不要频繁调用API，避免被限制
3. 生产环境建议使用VIP账户
4. 数据仅供研究使用，投资风险自担