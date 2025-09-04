"""
前视泄漏防护机制 (Look-Ahead Bias Prevention)

基于TradingAgents企业级架构的时间完整性保护：
- 严格防止使用未来信息进行历史决策
- 实现时间点数据访问控制
- 提供回测时间完整性验证
- 支持滚动窗口计算的时间边界管理
"""

from typing import Dict, Any, List, Optional, Set, Callable, Union
from datetime import datetime, date, timedelta
from dataclasses import dataclass, field
from enum import Enum
import logging
import threading
from contextlib import contextmanager
from abc import ABC, abstractmethod

import pandas as pd
import numpy as np
from ..data.schemas import MarketDataPoint, TradingSignal, DataSource
from ..data.trading_calendar import AShareTradingCalendar


class TemporalViolationType(Enum):
    """时间违规类型"""
    FUTURE_DATA_ACCESS = "future_data_access"       # 访问未来数据
    INVALID_TIMESTAMP = "invalid_timestamp"         # 无效时间戳
    BACKWARD_TIME_TRAVEL = "backward_time_travel"   # 时间倒退
    NON_TRADING_TIME = "non_trading_time"          # 非交易时间
    INSUFFICIENT_LOOKBACK = "insufficient_lookback" # 回看期不足
    CROSS_PERIOD_LEAK = "cross_period_leak"        # 跨期泄漏


@dataclass
class TemporalViolation:
    """时间违规记录"""
    violation_type: TemporalViolationType
    timestamp: datetime
    description: str
    context: Dict[str, Any] = field(default_factory=dict)
    severity: str = "high"  # high, medium, low
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'violation_type': self.violation_type.value,
            'timestamp': self.timestamp.isoformat(),
            'description': self.description,
            'context': self.context,
            'severity': self.severity
        }


@dataclass
class TemporalContext:
    """时间上下文状态"""
    current_time: datetime
    simulation_mode: bool = True
    max_lookback_days: int = 252  # 默认一年交易日
    allowed_future_minutes: int = 0  # 允许的未来时间容差(分钟)
    strict_mode: bool = True
    violations: List[TemporalViolation] = field(default_factory=list)
    
    # 时间边界缓存
    _earliest_allowed: Optional[datetime] = None
    _latest_allowed: Optional[datetime] = None
    
    def get_earliest_allowed(self) -> datetime:
        """获取最早允许的时间"""
        if self._earliest_allowed is None:
            self._earliest_allowed = self.current_time - timedelta(days=self.max_lookback_days)
        return self._earliest_allowed
    
    def get_latest_allowed(self) -> datetime:
        """获取最晚允许的时间"""
        if self._latest_allowed is None:
            self._latest_allowed = self.current_time + timedelta(minutes=self.allowed_future_minutes)
        return self._latest_allowed
    
    def update_current_time(self, new_time: datetime):
        """更新当前时间"""
        if self.current_time and new_time < self.current_time:
            violation = TemporalViolation(
                violation_type=TemporalViolationType.BACKWARD_TIME_TRAVEL,
                timestamp=new_time,
                description=f"时间倒退：从 {self.current_time} 到 {new_time}",
                context={'previous_time': self.current_time.isoformat()},
                severity="high"
            )
            self.violations.append(violation)
            if self.strict_mode:
                raise ValueError(f"时间倒退违规: {violation.description}")
        
        self.current_time = new_time
        # 清除缓存
        self._earliest_allowed = None
        self._latest_allowed = None


class TemporalGuard:
    """时间防护核心类"""
    
    def __init__(self, calendar: Optional[AShareTradingCalendar] = None):
        """初始化时间防护
        
        Args:
            calendar: 交易日历实例
        """
        self.calendar = calendar or AShareTradingCalendar()
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # 线程本地存储，支持多线程环境
        self._local = threading.local()
        
        # 全局配置
        self.global_config = {
            'default_lookback_days': 252,
            'max_future_tolerance_minutes': 5,
            'enable_trading_time_check': True,
            'enable_strict_mode': True,
        }
    
    @property
    def context(self) -> Optional[TemporalContext]:
        """获取当前线程的时间上下文"""
        return getattr(self._local, 'context', None)
    
    @context.setter
    def context(self, ctx: TemporalContext):
        """设置当前线程的时间上下文"""
        self._local.context = ctx
    
    @contextmanager
    def temporal_scope(self, 
                      current_time: datetime,
                      simulation_mode: bool = True,
                      max_lookback_days: int = None,
                      strict_mode: bool = None):
        """时间作用域上下文管理器
        
        Args:
            current_time: 当前模拟时间
            simulation_mode: 是否为模拟模式
            max_lookback_days: 最大回看天数
            strict_mode: 是否启用严格模式
        """
        # 保存之前的上下文
        previous_context = self.context
        
        # 创建新的时间上下文
        new_context = TemporalContext(
            current_time=current_time,
            simulation_mode=simulation_mode,
            max_lookback_days=max_lookback_days or self.global_config['default_lookback_days'],
            allowed_future_minutes=self.global_config['max_future_tolerance_minutes'],
            strict_mode=strict_mode if strict_mode is not None else self.global_config['enable_strict_mode']
        )
        
        self.context = new_context
        
        try:
            self.logger.debug(f"进入时间作用域: {current_time}")
            yield new_context
        finally:
            # 恢复之前的上下文
            self.context = previous_context
            self.logger.debug(f"退出时间作用域: {current_time}")
    
    def validate_data_timestamp(self, data_timestamp: datetime, data_type: str = "unknown") -> bool:
        """验证数据时间戳的合法性
        
        Args:
            data_timestamp: 数据时间戳
            data_type: 数据类型描述
            
        Returns:
            bool: 验证是否通过
            
        Raises:
            ValueError: 严格模式下的时间违规
        """
        if not self.context:
            self.logger.warning("未设置时间上下文，跳过时间验证")
            return True
        
        ctx = self.context
        violations = []
        
        # 1. 检查是否访问未来数据
        if data_timestamp > ctx.get_latest_allowed():
            violation = TemporalViolation(
                violation_type=TemporalViolationType.FUTURE_DATA_ACCESS,
                timestamp=data_timestamp,
                description=f"访问未来数据：{data_type} 时间戳 {data_timestamp} 超过允许的最大时间 {ctx.get_latest_allowed()}",
                context={
                    'data_type': data_type,
                    'current_time': ctx.current_time.isoformat(),
                    'future_offset': (data_timestamp - ctx.current_time).total_seconds()
                }
            )
            violations.append(violation)
        
        # 2. 检查是否超出回看期
        if data_timestamp < ctx.get_earliest_allowed():
            violation = TemporalViolation(
                violation_type=TemporalViolationType.INSUFFICIENT_LOOKBACK,
                timestamp=data_timestamp,
                description=f"数据超出回看期：{data_type} 时间戳 {data_timestamp} 早于允许的最早时间 {ctx.get_earliest_allowed()}",
                context={
                    'data_type': data_type,
                    'lookback_days': ctx.max_lookback_days,
                    'lookback_offset': (ctx.current_time - data_timestamp).days
                }
            )
            violations.append(violation)
        
        # 3. 检查交易时间（如果启用）
        if (self.global_config['enable_trading_time_check'] and 
            data_type in ['market_data', 'trading_signal']):
            
            is_valid, message = self.calendar.validate_market_data_time(data_timestamp)
            if not is_valid:
                violation = TemporalViolation(
                    violation_type=TemporalViolationType.NON_TRADING_TIME,
                    timestamp=data_timestamp,
                    description=f"非交易时间数据：{message}",
                    context={
                        'data_type': data_type,
                        'validation_message': message
                    },
                    severity="medium"
                )
                violations.append(violation)
        
        # 记录违规
        ctx.violations.extend(violations)
        
        # 严格模式下抛出异常
        if violations and ctx.strict_mode:
            high_severity_violations = [v for v in violations if v.severity == "high"]
            if high_severity_violations:
                raise ValueError(f"时间完整性违规: {high_severity_violations[0].description}")
        
        return len(violations) == 0
    
    def advance_time(self, new_time: datetime) -> None:
        """推进模拟时间
        
        Args:
            new_time: 新的时间
        """
        if not self.context:
            raise ValueError("未设置时间上下文")
        
        self.context.update_current_time(new_time)
        self.logger.debug(f"时间推进至: {new_time}")
    
    def get_violation_summary(self) -> Dict[str, Any]:
        """获取违规统计摘要
        
        Returns:
            Dict: 违规统计信息
        """
        if not self.context:
            return {'total_violations': 0, 'violations_by_type': {}, 'violations_by_severity': {}}
        
        violations = self.context.violations
        
        # 按类型统计
        by_type = {}
        for violation in violations:
            vtype = violation.violation_type.value
            by_type[vtype] = by_type.get(vtype, 0) + 1
        
        # 按严重程度统计
        by_severity = {}
        for violation in violations:
            severity = violation.severity
            by_severity[severity] = by_severity.get(severity, 0) + 1
        
        return {
            'total_violations': len(violations),
            'violations_by_type': by_type,
            'violations_by_severity': by_severity,
            'current_time': self.context.current_time.isoformat() if self.context.current_time else None,
            'simulation_mode': self.context.simulation_mode,
            'strict_mode': self.context.strict_mode
        }


# ============================================================
# 时间感知数据访问层 - Time-Aware Data Access Layer
# ============================================================

class PointInTimeDataAccess:
    """时间点数据访问控制器"""
    
    def __init__(self, guard: TemporalGuard):
        """初始化时间点数据访问控制
        
        Args:
            guard: 时间防护实例
        """
        self.guard = guard
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # 数据缓存
        self._data_cache: Dict[str, pd.DataFrame] = {}
        self._index_cache: Dict[str, Dict] = {}
    
    def get_market_data(self, 
                       symbol: str, 
                       end_time: Optional[datetime] = None,
                       lookback_periods: int = 100,
                       data_source: str = "default") -> List[MarketDataPoint]:
        """获取指定时间点的市场数据
        
        Args:
            symbol: 股票代码
            end_time: 结束时间，None表示使用当前时间
            lookback_periods: 回看期数
            data_source: 数据源标识
            
        Returns:
            List[MarketDataPoint]: 市场数据列表
        """
        # 确定查询时间
        query_time = end_time or (self.guard.context.current_time if self.guard.context else datetime.now())
        
        # 验证时间
        if self.guard.context:
            self.guard.validate_data_timestamp(query_time, "market_data")
        
        # 计算查询范围
        calendar = self.guard.calendar
        end_date = query_time.date()
        
        # 获取交易日
        try:
            # 向前推算足够的自然日以确保包含指定数量的交易日
            start_date = end_date - timedelta(days=lookback_periods * 2)  # 保守估算
            trading_days = calendar.get_trading_days(start_date, end_date)
            
            if len(trading_days) > lookback_periods:
                trading_days = trading_days[-lookback_periods:]
                
        except Exception as e:
            self.logger.warning(f"获取交易日失败: {e}")
            trading_days = [end_date]
        
        # 模拟数据获取（实际实现中从数据源获取）
        mock_data = []
        base_price = 11.50
        
        for i, trading_day in enumerate(trading_days):
            # 验证每个数据点的时间
            data_timestamp = datetime.combine(trading_day, query_time.time())
            
            if self.guard.context:
                try:
                    self.guard.validate_data_timestamp(data_timestamp, "market_data")
                except ValueError:
                    # 跳过违规数据点
                    continue
            
            # 生成模拟数据
            price_change = (np.random.random() - 0.5) * 0.1
            price = base_price * (1 + price_change)
            
            data_point = MarketDataPoint(
                symbol=symbol,
                timestamp=data_timestamp,
                trading_date=trading_day,
                open_price=price * 0.998,
                high_price=price * 1.015,
                low_price=price * 0.985,
                close_price=price,
                volume=int(np.random.random() * 2000000 + 500000),
                amount=price * int(np.random.random() * 2000000 + 500000),
                data_source=DataSource.MANUAL.value  # 使用有效的枚举值
            )
            
            mock_data.append(data_point)
            base_price = price
        
        self.logger.debug(f"获取 {symbol} 市场数据: {len(mock_data)} 条记录")
        return mock_data
    
    def validate_signal_timing(self, signal: TradingSignal) -> bool:
        """验证交易信号的时间合法性
        
        Args:
            signal: 交易信号
            
        Returns:
            bool: 验证是否通过
        """
        # 验证信号生成时间
        is_valid = self.guard.validate_data_timestamp(signal.timestamp, "trading_signal")
        
        # 验证信号有效期
        if signal.valid_until:
            if signal.valid_until < signal.timestamp:
                violation = TemporalViolation(
                    violation_type=TemporalViolationType.INVALID_TIMESTAMP,
                    timestamp=signal.timestamp,
                    description=f"信号有效期早于生成时间: {signal.valid_until} < {signal.timestamp}",
                    context={
                        'signal_id': signal.signal_id,
                        'symbol': signal.symbol
                    }
                )
                if self.guard.context:
                    self.guard.context.violations.append(violation)
                is_valid = False
        
        return is_valid


# ============================================================
# 滚动窗口计算防护 - Rolling Window Protection
# ============================================================

class RollingWindowGuard:
    """滚动窗口计算防护"""
    
    def __init__(self, guard: TemporalGuard):
        """初始化滚动窗口防护
        
        Args:
            guard: 时间防护实例
        """
        self.guard = guard
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # 窗口状态追踪
        self._window_states: Dict[str, Dict] = {}
    
    def create_rolling_window(self, 
                            window_id: str,
                            window_size: int,
                            min_periods: Optional[int] = None) -> 'RollingWindow':
        """创建滚动窗口
        
        Args:
            window_id: 窗口唯一标识
            window_size: 窗口大小
            min_periods: 最小期数要求
            
        Returns:
            RollingWindow: 滚动窗口实例
        """
        return RollingWindow(
            window_id=window_id,
            window_size=window_size,
            min_periods=min_periods or window_size,
            guard=self.guard
        )


class RollingWindow:
    """时间感知的滚动窗口"""
    
    def __init__(self, 
                 window_id: str,
                 window_size: int,
                 min_periods: int,
                 guard: TemporalGuard):
        """初始化滚动窗口
        
        Args:
            window_id: 窗口标识
            window_size: 窗口大小
            min_periods: 最小期数
            guard: 时间防护
        """
        self.window_id = window_id
        self.window_size = window_size
        self.min_periods = min_periods
        self.guard = guard
        
        # 数据缓冲区
        self._data_buffer: List[Dict] = []
        self._timestamps: List[datetime] = []
    
    def add_data_point(self, data: Dict, timestamp: datetime) -> None:
        """添加数据点
        
        Args:
            data: 数据字典
            timestamp: 时间戳
        """
        # 验证时间戳
        if self.guard.context:
            self.guard.validate_data_timestamp(timestamp, f"rolling_window_{self.window_id}")
        
        # 维护时间顺序
        if self._timestamps and timestamp <= self._timestamps[-1]:
            violation = TemporalViolation(
                violation_type=TemporalViolationType.BACKWARD_TIME_TRAVEL,
                timestamp=timestamp,
                description=f"滚动窗口 {self.window_id} 数据时间倒退",
                context={'window_id': self.window_id}
            )
            if self.guard.context:
                self.guard.context.violations.append(violation)
            return
        
        # 添加数据点
        self._data_buffer.append(data)
        self._timestamps.append(timestamp)
        
        # 维护窗口大小
        if len(self._data_buffer) > self.window_size:
            self._data_buffer.pop(0)
            self._timestamps.pop(0)
    
    def calculate(self, calc_func: Callable) -> Optional[Any]:
        """计算窗口结果
        
        Args:
            calc_func: 计算函数
            
        Returns:
            Any: 计算结果，数据不足时返回None
        """
        if len(self._data_buffer) < self.min_periods:
            return None
        
        try:
            return calc_func(self._data_buffer)
        except Exception as e:
            self.logger.error(f"滚动窗口 {self.window_id} 计算失败: {e}")
            return None
    
    def get_window_info(self) -> Dict[str, Any]:
        """获取窗口信息
        
        Returns:
            Dict: 窗口状态信息
        """
        return {
            'window_id': self.window_id,
            'window_size': self.window_size,
            'min_periods': self.min_periods,
            'current_size': len(self._data_buffer),
            'is_ready': len(self._data_buffer) >= self.min_periods,
            'earliest_timestamp': self._timestamps[0].isoformat() if self._timestamps else None,
            'latest_timestamp': self._timestamps[-1].isoformat() if self._timestamps else None
        }


# ============================================================
# 工厂函数 - Factory Functions
# ============================================================

def create_temporal_guard(calendar: Optional[AShareTradingCalendar] = None) -> TemporalGuard:
    """创建时间防护实例
    
    Args:
        calendar: 交易日历
        
    Returns:
        TemporalGuard: 时间防护实例
    """
    return TemporalGuard(calendar)


def create_point_in_time_access(guard: Optional[TemporalGuard] = None) -> PointInTimeDataAccess:
    """创建时间点数据访问控制器
    
    Args:
        guard: 时间防护实例
        
    Returns:
        PointInTimeDataAccess: 数据访问控制器
    """
    if guard is None:
        guard = create_temporal_guard()
    return PointInTimeDataAccess(guard)


# 导出主要类型
__all__ = [
    'TemporalViolationType', 'TemporalViolation', 'TemporalContext',
    'TemporalGuard', 'PointInTimeDataAccess', 'RollingWindowGuard', 'RollingWindow',
    'create_temporal_guard', 'create_point_in_time_access'
]