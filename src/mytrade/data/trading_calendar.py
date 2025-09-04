"""
A股交易日历模块

基于TradingAgents企业级架构：
- 支持中国股市交易日历计算
- 处理节假日、停牌、特殊交易时段
- 提供前视泄漏防护的时间验证
"""

from typing import List, Dict, Set, Optional, Tuple
from datetime import date, datetime, timedelta
import json
import logging
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

import pandas as pd


class MarketStatus(Enum):
    """市场状态"""
    TRADING = "trading"           # 正常交易
    CLOSED = "closed"            # 休市
    PRE_MARKET = "pre_market"    # 盘前
    POST_MARKET = "post_market"  # 盘后
    SUSPENDED = "suspended"      # 临时停市


class HolidayType(Enum):
    """节假日类型"""
    NEW_YEAR = "new_year"        # 元旦
    SPRING_FESTIVAL = "spring_festival"  # 春节
    TOMB_SWEEPING = "tomb_sweeping"      # 清明节
    LABOR_DAY = "labor_day"      # 劳动节
    DRAGON_BOAT = "dragon_boat"  # 端午节
    MID_AUTUMN = "mid_autumn"    # 中秋节
    NATIONAL_DAY = "national_day" # 国庆节
    WEEKEND = "weekend"          # 周末
    OTHER = "other"              # 其他


@dataclass
class MarketHoliday:
    """市场假期数据"""
    start_date: date
    end_date: date
    holiday_type: HolidayType
    name: str
    description: Optional[str] = None


@dataclass  
class TradingSession:
    """交易时段"""
    name: str
    start_time: str  # HH:MM格式
    end_time: str    # HH:MM格式
    
    def contains_time(self, time_str: str) -> bool:
        """判断时间是否在交易时段内"""
        return self.start_time <= time_str <= self.end_time


class AShareTradingCalendar:
    """A股交易日历"""
    
    # A股标准交易时段
    TRADING_SESSIONS = [
        TradingSession("morning", "09:30", "11:30"),
        TradingSession("afternoon", "13:00", "15:00")
    ]
    
    def __init__(self, data_path: Optional[str] = None):
        """初始化交易日历
        
        Args:
            data_path: 自定义节假日数据路径
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.data_path = Path(data_path) if data_path else None
        
        # 缓存数据
        self._holidays_cache: Dict[int, List[MarketHoliday]] = {}
        self._trading_days_cache: Dict[Tuple[date, date], Set[date]] = {}
        
        # 加载预定义节假日数据
        self._load_holidays()
    
    def _load_holidays(self):
        """加载节假日数据"""
        try:
            # 如果提供了自定义数据路径，优先使用
            if self.data_path and self.data_path.exists():
                with open(self.data_path, 'r', encoding='utf-8') as f:
                    holidays_data = json.load(f)
                self._parse_holidays_data(holidays_data)
                return
            
            # 使用内置的2023-2025年节假日数据
            self._load_builtin_holidays()
            
        except Exception as e:
            self.logger.warning(f"节假日数据加载失败，使用基础规则: {e}")
    
    def _load_builtin_holidays(self):
        """加载内置节假日数据（2023-2025年）"""
        # 2024年节假日（根据国务院办公厅通知）
        holidays_2024 = [
            # 元旦: 12月30日至1月1日
            MarketHoliday(date(2024, 1, 1), date(2024, 1, 1), HolidayType.NEW_YEAR, "元旦"),
            
            # 春节: 2月10日至17日
            MarketHoliday(date(2024, 2, 10), date(2024, 2, 17), HolidayType.SPRING_FESTIVAL, "春节"),
            
            # 清明节: 4月4日至6日
            MarketHoliday(date(2024, 4, 4), date(2024, 4, 6), HolidayType.TOMB_SWEEPING, "清明节"),
            
            # 劳动节: 5月1日至5日
            MarketHoliday(date(2024, 5, 1), date(2024, 5, 5), HolidayType.LABOR_DAY, "劳动节"),
            
            # 端午节: 6月10日
            MarketHoliday(date(2024, 6, 10), date(2024, 6, 10), HolidayType.DRAGON_BOAT, "端午节"),
            
            # 中秋节: 9月15日至17日
            MarketHoliday(date(2024, 9, 15), date(2024, 9, 17), HolidayType.MID_AUTUMN, "中秋节"),
            
            # 国庆节: 10月1日至7日
            MarketHoliday(date(2024, 10, 1), date(2024, 10, 7), HolidayType.NATIONAL_DAY, "国庆节"),
        ]
        
        # 2025年节假日（预估，实际以国务院通知为准）
        holidays_2025 = [
            MarketHoliday(date(2025, 1, 1), date(2025, 1, 1), HolidayType.NEW_YEAR, "元旦"),
            MarketHoliday(date(2025, 1, 28), date(2025, 2, 3), HolidayType.SPRING_FESTIVAL, "春节（预估）"),
            MarketHoliday(date(2025, 4, 4), date(2025, 4, 6), HolidayType.TOMB_SWEEPING, "清明节（预估）"),
            MarketHoliday(date(2025, 5, 1), date(2025, 5, 5), HolidayType.LABOR_DAY, "劳动节（预估）"),
            MarketHoliday(date(2025, 5, 31), date(2025, 5, 31), HolidayType.DRAGON_BOAT, "端午节（预估）"),
            MarketHoliday(date(2025, 10, 1), date(2025, 10, 7), HolidayType.NATIONAL_DAY, "国庆节（预估）"),
        ]
        
        self._holidays_cache[2024] = holidays_2024
        self._holidays_cache[2025] = holidays_2025
        
        self.logger.info("内置节假日数据加载完成 (2024-2025)")
    
    def _parse_holidays_data(self, holidays_data: Dict):
        """解析节假日数据"""
        for year_str, year_holidays in holidays_data.items():
            year = int(year_str)
            parsed_holidays = []
            
            for holiday in year_holidays:
                parsed_holidays.append(MarketHoliday(
                    start_date=date.fromisoformat(holiday['start_date']),
                    end_date=date.fromisoformat(holiday['end_date']),
                    holiday_type=HolidayType(holiday['holiday_type']),
                    name=holiday['name'],
                    description=holiday.get('description')
                ))
            
            self._holidays_cache[year] = parsed_holidays
    
    def is_trading_day(self, check_date: date) -> bool:
        """判断是否为交易日
        
        Args:
            check_date: 检查日期
            
        Returns:
            bool: True表示交易日，False表示非交易日
        """
        # 周末不是交易日
        if check_date.weekday() >= 5:  # 5=周六, 6=周日
            return False
        
        # 检查是否为法定节假日
        if self.is_holiday(check_date):
            return False
        
        return True
    
    def is_holiday(self, check_date: date) -> bool:
        """判断是否为节假日
        
        Args:
            check_date: 检查日期
            
        Returns:
            bool: True表示节假日，False表示工作日
        """
        year = check_date.year
        
        if year not in self._holidays_cache:
            self.logger.warning(f"年份 {year} 的节假日数据未加载，仅检查周末")
            return check_date.weekday() >= 5
        
        for holiday in self._holidays_cache[year]:
            if holiday.start_date <= check_date <= holiday.end_date:
                return True
        
        return False
    
    def get_trading_days(self, start_date: date, end_date: date) -> List[date]:
        """获取指定期间的交易日列表
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            List[date]: 交易日列表
        """
        cache_key = (start_date, end_date)
        if cache_key in self._trading_days_cache:
            return sorted(list(self._trading_days_cache[cache_key]))
        
        trading_days = set()
        current_date = start_date
        
        while current_date <= end_date:
            if self.is_trading_day(current_date):
                trading_days.add(current_date)
            current_date += timedelta(days=1)
        
        self._trading_days_cache[cache_key] = trading_days
        return sorted(list(trading_days))
    
    def get_next_trading_day(self, from_date: date) -> date:
        """获取下一个交易日
        
        Args:
            from_date: 起始日期
            
        Returns:
            date: 下一个交易日
        """
        next_date = from_date + timedelta(days=1)
        
        # 最多查找30天
        for _ in range(30):
            if self.is_trading_day(next_date):
                return next_date
            next_date += timedelta(days=1)
        
        raise ValueError(f"从 {from_date} 开始30天内未找到交易日")
    
    def get_previous_trading_day(self, from_date: date) -> date:
        """获取上一个交易日
        
        Args:
            from_date: 起始日期
            
        Returns:
            date: 上一个交易日
        """
        prev_date = from_date - timedelta(days=1)
        
        # 最多查找30天
        for _ in range(30):
            if self.is_trading_day(prev_date):
                return prev_date
            prev_date -= timedelta(days=1)
        
        raise ValueError(f"从 {from_date} 开始30天内未找到交易日")
    
    def get_market_status(self, check_datetime: datetime) -> MarketStatus:
        """获取市场状态
        
        Args:
            check_datetime: 检查时间
            
        Returns:
            MarketStatus: 市场状态
        """
        check_date = check_datetime.date()
        check_time = check_datetime.time().strftime("%H:%M")
        
        # 非交易日
        if not self.is_trading_day(check_date):
            return MarketStatus.CLOSED
        
        # 检查是否在交易时段内
        for session in self.TRADING_SESSIONS:
            if session.contains_time(check_time):
                return MarketStatus.TRADING
        
        # 盘前时间
        if check_time < "09:30":
            return MarketStatus.PRE_MARKET
        
        # 午休时间
        if "11:30" < check_time < "13:00":
            return MarketStatus.CLOSED
        
        # 盘后时间
        if check_time > "15:00":
            return MarketStatus.POST_MARKET
        
        return MarketStatus.CLOSED
    
    def validate_market_data_time(self, data_datetime: datetime) -> Tuple[bool, str]:
        """验证市场数据时间的合理性（防止前视泄漏）
        
        Args:
            data_datetime: 数据时间戳
            
        Returns:
            Tuple[bool, str]: (是否有效, 验证消息)
        """
        data_date = data_datetime.date()
        data_time = data_datetime.time()
        current_datetime = datetime.now()
        
        # 1. 数据不能来自未来
        if data_datetime > current_datetime:
            return False, f"数据时间 {data_datetime} 晚于当前时间 {current_datetime}"
        
        # 2. 数据日期必须是交易日
        if not self.is_trading_day(data_date):
            return False, f"数据日期 {data_date} 不是交易日"
        
        # 3. 数据时间必须在交易时段内
        market_status = self.get_market_status(data_datetime)
        if market_status != MarketStatus.TRADING:
            return False, f"数据时间 {data_datetime} 不在交易时段内，市场状态: {market_status.value}"
        
        return True, "数据时间验证通过"
    
    def get_trading_calendar_summary(self, year: int) -> Dict:
        """获取交易日历摘要信息
        
        Args:
            year: 年份
            
        Returns:
            Dict: 日历摘要
        """
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
        
        trading_days = self.get_trading_days(start_date, end_date)
        holidays = self._holidays_cache.get(year, [])
        
        # 按类型统计节假日
        holiday_stats = {}
        total_holiday_days = 0
        for holiday in holidays:
            holiday_type = holiday.holiday_type.value
            days_count = (holiday.end_date - holiday.start_date).days + 1
            
            if holiday_type not in holiday_stats:
                holiday_stats[holiday_type] = {'count': 0, 'days': 0, 'holidays': []}
            
            holiday_stats[holiday_type]['count'] += 1
            holiday_stats[holiday_type]['days'] += days_count
            holiday_stats[holiday_type]['holidays'].append({
                'name': holiday.name,
                'start_date': holiday.start_date.isoformat(),
                'end_date': holiday.end_date.isoformat(),
                'days': days_count
            })
            
            total_holiday_days += days_count
        
        return {
            'year': year,
            'total_days': 366 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 365,
            'trading_days': len(trading_days),
            'non_trading_days': 365 - len(trading_days) if year != 2024 else 366 - len(trading_days),
            'holidays_count': len(holidays),
            'holiday_days': total_holiday_days,
            'weekend_days': 52 * 2,  # 大致估算
            'holiday_stats': holiday_stats,
            'first_trading_day': trading_days[0].isoformat() if trading_days else None,
            'last_trading_day': trading_days[-1].isoformat() if trading_days else None
        }


# ============================================================
# 停牌检测模块 - Suspension Detection
# ============================================================

class SuspensionDetector:
    """停牌检测器"""
    
    def __init__(self, calendar: AShareTradingCalendar):
        self.calendar = calendar
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # 停牌检测参数
        self.max_zero_volume_days = 5      # 连续零成交量天数阈值
        self.min_price_change_threshold = 0.001  # 最小价格变化阈值
    
    def detect_suspension(
        self, 
        symbol: str, 
        market_data: List[Dict], 
        check_date: Optional[date] = None
    ) -> Tuple[bool, Optional[str], Dict]:
        """检测股票是否停牌
        
        Args:
            symbol: 股票代码
            market_data: 最近的市场数据列表
            check_date: 检查日期，默认为今天
            
        Returns:
            Tuple[bool, Optional[str], Dict]: (是否停牌, 停牌原因, 检测详情)
        """
        if not market_data:
            return True, "无市场数据", {'reason': 'no_data'}
        
        check_date = check_date or date.today()
        detection_details = {
            'check_date': check_date.isoformat(),
            'data_points': len(market_data),
            'analysis': {}
        }
        
        try:
            # 1. 检查是否有当日数据
            latest_data = market_data[-1]
            latest_date = datetime.fromisoformat(latest_data['timestamp']).date()
            
            if latest_date < check_date:
                # 检查之间是否都是非交易日
                missing_trading_days = []
                current = latest_date + timedelta(days=1)
                while current <= check_date:
                    if self.calendar.is_trading_day(current):
                        missing_trading_days.append(current)
                    current += timedelta(days=1)
                
                if missing_trading_days:
                    detection_details['analysis']['missing_trading_days'] = [
                        d.isoformat() for d in missing_trading_days
                    ]
                    return True, "缺少交易日数据，疑似停牌", detection_details
            
            # 2. 检查连续零成交量
            zero_volume_count = 0
            for data in reversed(market_data[-self.max_zero_volume_days:]):
                if data.get('volume', 0) == 0:
                    zero_volume_count += 1
                else:
                    break
            
            detection_details['analysis']['zero_volume_days'] = zero_volume_count
            
            if zero_volume_count >= self.max_zero_volume_days:
                return True, f"连续{zero_volume_count}天零成交量", detection_details
            
            # 3. 检查价格异常（一字板）
            recent_data = market_data[-3:]  # 检查最近3天
            one_price_days = 0
            
            for data in recent_data:
                open_p = data.get('open_price', 0)
                high_p = data.get('high_price', 0) 
                low_p = data.get('low_price', 0)
                close_p = data.get('close_price', 0)
                
                if abs(high_p - low_p) < self.min_price_change_threshold:
                    one_price_days += 1
            
            detection_details['analysis']['one_price_days'] = one_price_days
            
            # 4. 综合判断
            if zero_volume_count >= 3 and one_price_days >= 2:
                return True, "低成交量且价格异常，疑似停牌", detection_details
            
            # 5. 正常交易
            detection_details['analysis']['status'] = 'normal_trading'
            return False, None, detection_details
            
        except Exception as e:
            self.logger.error(f"停牌检测失败 {symbol}: {e}")
            return True, f"检测异常: {str(e)}", detection_details


# ============================================================
# 工厂函数 - Factory Functions  
# ============================================================

def create_ashare_calendar(data_path: Optional[str] = None) -> AShareTradingCalendar:
    """创建A股交易日历实例
    
    Args:
        data_path: 自定义节假日数据路径
        
    Returns:
        AShareTradingCalendar: 交易日历实例
    """
    return AShareTradingCalendar(data_path)


def create_suspension_detector(calendar: Optional[AShareTradingCalendar] = None) -> SuspensionDetector:
    """创建停牌检测器实例
    
    Args:
        calendar: 交易日历实例，如果为None则创建新的
        
    Returns:
        SuspensionDetector: 停牌检测器实例  
    """
    if calendar is None:
        calendar = create_ashare_calendar()
    return SuspensionDetector(calendar)


# 导出主要类型
__all__ = [
    'MarketStatus', 'HolidayType', 'MarketHoliday', 'TradingSession',
    'AShareTradingCalendar', 'SuspensionDetector',
    'create_ashare_calendar', 'create_suspension_detector'
]