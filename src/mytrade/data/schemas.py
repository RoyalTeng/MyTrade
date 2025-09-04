"""
数据统一模式定义
基于TradingAgents企业级架构的标准化数据格式

严格验证所有输入数据，防止数据质量问题传播到Agent系统
"""

from typing import Optional, Dict, Any, List, Literal
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, Field, validator


class MarketType(Enum):
    """市场类型"""
    A_SHARE = "A_SHARE"          # A股
    B_SHARE = "B_SHARE"          # B股  
    HK_STOCK = "HK_STOCK"        # 港股
    US_STOCK = "US_STOCK"        # 美股


class DataSource(Enum):
    """数据源枚举"""
    AKSHARE = "akshare"
    TUSHARE = "tushare"  
    SINA = "sina"
    EASTMONEY = "eastmoney"
    NETEASE_163 = "163"
    MANUAL = "manual"


class TradingStatus(Enum):
    """交易状态"""
    TRADING = "trading"          # 正常交易
    SUSPENDED = "suspended"      # 停牌
    DELISTED = "delisted"        # 退市
    IPO_PENDING = "ipo_pending"  # 待上市


# ============================================================
# 市场数据模式 - Market Data Schemas  
# ============================================================

class MarketDataPoint(BaseModel):
    """标准化市场数据点"""
    
    # 基础信息
    symbol: str = Field(..., min_length=6, max_length=10, description="股票代码")
    timestamp: datetime = Field(..., description="时间戳")
    trading_date: date = Field(..., description="交易日期")
    
    # OHLCV数据
    open_price: Decimal = Field(..., gt=0, description="开盘价")
    high_price: Decimal = Field(..., gt=0, description="最高价")
    low_price: Decimal = Field(..., gt=0, description="最低价")
    close_price: Decimal = Field(..., gt=0, description="收盘价")
    volume: int = Field(..., ge=0, description="成交量")
    amount: Decimal = Field(..., ge=0, description="成交额")
    
    # 技术指标
    turnover_rate: Optional[Decimal] = Field(None, ge=0, le=100, description="换手率%")
    pe_ratio: Optional[Decimal] = Field(None, ge=0, description="市盈率")
    pb_ratio: Optional[Decimal] = Field(None, ge=0, description="市净率")
    
    # 元数据
    market_type: MarketType = Field(default=MarketType.A_SHARE)
    data_source: DataSource = Field(..., description="数据源")
    data_quality: Literal["high", "medium", "low"] = Field(default="medium")
    
    @validator('high_price')
    def validate_high_price(cls, v, values):
        if 'low_price' in values and v < values['low_price']:
            raise ValueError("最高价不能低于最低价")
        return v
    
    @validator('close_price') 
    def validate_close_price(cls, v, values):
        if 'high_price' in values and 'low_price' in values:
            if not (values['low_price'] <= v <= values['high_price']):
                raise ValueError("收盘价必须在最高价和最低价之间")
        return v
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
        }


class MarketDataBatch(BaseModel):
    """批量市场数据"""
    
    symbol: str = Field(..., description="股票代码")
    start_date: date = Field(..., description="开始日期")
    end_date: date = Field(..., description="结束日期")
    data_points: List[MarketDataPoint] = Field(..., min_items=1)
    
    # 批量元数据
    total_records: int = Field(..., ge=1, description="总记录数")
    data_source: DataSource = Field(..., description="数据源")
    fetch_timestamp: datetime = Field(default_factory=datetime.now)
    
    @validator('data_points')
    def validate_data_consistency(cls, v):
        if len(v) == 0:
            return v
            
        # 验证所有数据点的symbol一致
        symbols = {dp.symbol for dp in v}
        if len(symbols) > 1:
            raise ValueError(f"数据点symbol不一致: {symbols}")
        
        # 验证时间序列顺序
        dates = [dp.trading_date for dp in v]
        if dates != sorted(dates):
            raise ValueError("数据点时间序列未排序")
        
        return v


# ============================================================
# 财务数据模式 - Financial Data Schemas
# ============================================================

class FinancialMetric(BaseModel):
    """财务指标"""
    
    symbol: str = Field(..., description="股票代码")
    report_date: date = Field(..., description="报告期")
    publish_date: Optional[date] = Field(None, description="发布日期")
    
    # 盈利能力指标
    revenue: Optional[Decimal] = Field(None, description="营业收入")
    net_profit: Optional[Decimal] = Field(None, description="净利润") 
    gross_profit_margin: Optional[Decimal] = Field(None, ge=0, le=1, description="毛利率")
    net_profit_margin: Optional[Decimal] = Field(None, ge=0, le=1, description="净利率")
    roe: Optional[Decimal] = Field(None, ge=-1, le=1, description="净资产收益率")
    roa: Optional[Decimal] = Field(None, ge=-1, le=1, description="总资产收益率")
    
    # 偿债能力指标
    total_assets: Optional[Decimal] = Field(None, ge=0, description="总资产")
    total_liabilities: Optional[Decimal] = Field(None, ge=0, description="总负债")
    debt_to_equity: Optional[Decimal] = Field(None, ge=0, description="资产负债率")
    current_ratio: Optional[Decimal] = Field(None, ge=0, description="流动比率")
    quick_ratio: Optional[Decimal] = Field(None, ge=0, description="速动比率")
    
    # 成长能力指标
    revenue_growth: Optional[Decimal] = Field(None, description="营收增长率")
    profit_growth: Optional[Decimal] = Field(None, description="利润增长率")
    
    # 元数据
    data_source: DataSource = Field(..., description="数据源")
    data_quality: Literal["high", "medium", "low"] = Field(default="medium")
    
    class Config:
        use_enum_values = True
        json_encoders = {
            date: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
        }


# ============================================================
# 新闻数据模式 - News Data Schemas
# ============================================================

class NewsItem(BaseModel):
    """标准化新闻数据"""
    
    # 基础信息
    news_id: str = Field(..., description="新闻ID")
    title: str = Field(..., min_length=1, max_length=200, description="新闻标题")
    content: Optional[str] = Field(None, max_length=10000, description="新闻内容")
    summary: Optional[str] = Field(None, max_length=500, description="新闻摘要")
    
    # 时间信息
    publish_time: datetime = Field(..., description="发布时间")
    crawl_time: datetime = Field(default_factory=datetime.now, description="爬取时间")
    
    # 来源信息
    source: str = Field(..., description="新闻源")
    author: Optional[str] = Field(None, description="作者")
    url: Optional[str] = Field(None, description="原文链接")
    
    # 关联信息
    related_symbols: List[str] = Field(default_factory=list, description="相关股票")
    keywords: List[str] = Field(default_factory=list, description="关键词")
    
    # 情感分析
    sentiment_score: Optional[float] = Field(None, ge=-1, le=1, description="情感得分")
    sentiment_label: Optional[Literal["positive", "negative", "neutral"]] = None
    
    # 影响度评估
    impact_score: Optional[float] = Field(None, ge=0, le=1, description="影响度得分")
    relevance_score: Optional[float] = Field(None, ge=0, le=1, description="相关度得分")
    
    # 元数据
    data_source: DataSource = Field(..., description="数据源")
    language: Literal["zh", "en"] = Field(default="zh", description="语言")
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# ============================================================
# 交易信号模式 - Trading Signal Schemas
# ============================================================

class SignalType(Enum):
    """信号类型"""
    BUY = "BUY"
    SELL = "SELL"  
    HOLD = "HOLD"
    REDUCE = "REDUCE"
    INCREASE = "INCREASE"


class TradingSignal(BaseModel):
    """标准化交易信号"""
    
    # 基础信息
    signal_id: str = Field(..., description="信号ID")
    symbol: str = Field(..., description="股票代码")
    timestamp: datetime = Field(default_factory=datetime.now, description="信号生成时间")
    
    # 信号内容
    signal_type: SignalType = Field(..., description="信号类型")
    strength: float = Field(..., ge=0, le=1, description="信号强度")
    confidence: float = Field(..., ge=0, le=1, description="置信度")
    
    # 交易建议
    target_price: Optional[Decimal] = Field(None, gt=0, description="目标价格")
    stop_loss: Optional[Decimal] = Field(None, gt=0, description="止损价格")
    position_size: Optional[float] = Field(None, ge=0, le=1, description="建议仓位")
    
    # 有效期
    valid_from: datetime = Field(..., description="信号有效开始时间")
    valid_until: Optional[datetime] = Field(None, description="信号失效时间")
    
    # 生成信息
    agent_id: str = Field(..., description="生成Agent ID")
    agent_type: str = Field(..., description="Agent类型")
    reasoning: str = Field(..., max_length=500, description="决策推理")
    
    # 元数据  
    market_condition: Optional[str] = Field(None, description="市场环境")
    risk_level: Literal["low", "medium", "high"] = Field(default="medium")
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
        }


# ============================================================  
# 数据验证工具 - Data Validation Utilities
# ============================================================

class DataValidator:
    """数据验证工具类"""
    
    @staticmethod
    def validate_symbol_format(symbol: str, market_type: MarketType) -> bool:
        """验证股票代码格式"""
        if market_type == MarketType.A_SHARE:
            # A股代码格式：6位数字
            return len(symbol) == 6 and symbol.isdigit()
        elif market_type == MarketType.HK_STOCK:
            # 港股代码格式：5位数字，前缀00/03/06/08
            return len(symbol) == 5 and symbol.isdigit()
        return True
    
    @staticmethod  
    def validate_trading_time(timestamp: datetime, market_type: MarketType) -> bool:
        """验证交易时间"""
        if market_type == MarketType.A_SHARE:
            # A股交易时间：9:30-11:30, 13:00-15:00
            time = timestamp.time()
            morning = time >= datetime.strptime("09:30", "%H:%M").time() and \
                     time <= datetime.strptime("11:30", "%H:%M").time()
            afternoon = time >= datetime.strptime("13:00", "%H:%M").time() and \
                       time <= datetime.strptime("15:00", "%H:%M").time()
            return morning or afternoon
        return True
    
    @staticmethod
    def estimate_data_quality(data_point: MarketDataPoint) -> str:
        """评估数据质量"""
        score = 1.0
        
        # 检查必要字段完整性
        required_fields = ['open_price', 'high_price', 'low_price', 'close_price', 'volume']
        missing_fields = [f for f in required_fields if getattr(data_point, f) is None]
        if missing_fields:
            score -= 0.3
        
        # 检查数据合理性
        try:
            if data_point.volume == 0:  # 零成交量可能有问题
                score -= 0.2
            if data_point.high_price == data_point.low_price == data_point.open_price == data_point.close_price:
                score -= 0.3  # 一字板情况
        except:
            score -= 0.5
        
        if score >= 0.8:
            return "high"
        elif score >= 0.5:
            return "medium"
        else:
            return "low"


# 导出主要类型
__all__ = [
    'MarketType', 'DataSource', 'TradingStatus',
    'MarketDataPoint', 'MarketDataBatch', 
    'FinancialMetric', 'NewsItem', 
    'SignalType', 'TradingSignal',
    'DataValidator'
]