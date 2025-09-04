"""
市场数据采集器模块

负责从数据源获取A股市场行情数据，并实现本地缓存机制。
支持日线、分钟线等多种频率数据的获取和缓存。
"""

import os
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, Literal

import pandas as pd
import akshare as ak
import tushare as ts
from pydantic import BaseModel, Field


class DataSourceConfig(BaseModel):
    """数据源配置"""
    source: Literal["akshare", "tushare"] = "akshare"
    tushare_token: Optional[str] = None
    cache_dir: Path = Field(default_factory=lambda: Path("./data/cache"))
    cache_days: int = 7  # 缓存有效天数


class MarketDataFetcher:
    """
    市场数据采集器
    
    功能：
    - 支持从AkShare和Tushare获取A股历史行情数据
    - 实现本地文件缓存机制，避免重复请求
    - 支持日线、分钟线等多种数据频率
    - 提供统一的数据接口和异常处理
    """

    def __init__(self, config: DataSourceConfig):
        """
        初始化数据采集器
        
        Args:
            config: 数据源配置
        """
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # 确保缓存目录存在
        self.config.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化Tushare（如果使用）
        if config.source == "tushare" and config.tushare_token:
            ts.set_token(config.tushare_token)
            self.ts_pro = ts.pro_api()
        else:
            self.ts_pro = None
            
        self.logger.info(f"MarketDataFetcher initialized with source: {config.source}")

    def fetch_history(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        freq: Literal["daily", "1min", "5min", "15min", "30min", "60min"] = "daily",
        force_update: bool = False
    ) -> pd.DataFrame:
        """
        获取历史行情数据
        
        Args:
            symbol: 股票代码，如 "600519" 或 "000001"
            start_date: 开始日期，格式 "YYYY-MM-DD"
            end_date: 结束日期，格式 "YYYY-MM-DD"
            freq: 数据频率
            force_update: 是否强制更新缓存
            
        Returns:
            包含OHLCV数据的DataFrame
        """
        # 标准化股票代码
        normalized_symbol = self._normalize_symbol(symbol)
        
        # 生成缓存文件路径
        cache_file = self._get_cache_file_path(normalized_symbol, freq)
        
        # 检查缓存
        if not force_update and self._is_cache_valid(cache_file):
            self.logger.info(f"Loading cached data for {normalized_symbol}")
            try:
                cached_data = pd.read_csv(cache_file, index_col=0, parse_dates=True)
                # 筛选时间范围
                mask = (cached_data.index >= start_date) & (cached_data.index <= end_date)
                return cached_data[mask].copy()
            except Exception as e:
                self.logger.warning(f"Failed to load cache: {e}, fetching new data")
        
        # 从数据源获取数据
        self.logger.info(f"Fetching {freq} data for {normalized_symbol} from {self.config.source}")
        
        try:
            if self.config.source == "akshare":
                data = self._fetch_from_akshare(normalized_symbol, start_date, end_date, freq)
            elif self.config.source == "tushare":
                data = self._fetch_from_tushare(normalized_symbol, start_date, end_date, freq)
            else:
                raise ValueError(f"Unsupported data source: {self.config.source}")
            
            # 数据标准化处理
            data = self._standardize_data(data)
            
            # 缓存数据
            self._cache_data(data, cache_file)
            
            self.logger.info(f"Successfully fetched {len(data)} records for {normalized_symbol}")
            return data
            
        except Exception as e:
            self.logger.error(f"Failed to fetch data for {normalized_symbol}: {e}")
            raise

    def fetch_recent(self, symbol: str, days: int = 5) -> pd.DataFrame:
        """
        获取最近几天的数据
        
        Args:
            symbol: 股票代码
            days: 天数
            
        Returns:
            最近的行情数据
        """
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        return self.fetch_history(symbol, start_date, end_date)

    def get_stock_list(self, market: str = "all") -> pd.DataFrame:
        """
        获取股票列表
        
        Args:
            market: 市场类型，"all", "sh", "sz"
            
        Returns:
            股票代码和名称的DataFrame
        """
        try:
            if self.config.source == "akshare":
                if market == "all":
                    return ak.stock_info_a_code_name()
                elif market == "sh":
                    df = ak.stock_info_a_code_name()
                    return df[df['code'].str.startswith(('60', '68'))]
                elif market == "sz":
                    df = ak.stock_info_a_code_name()
                    return df[df['code'].str.startswith(('00', '30'))]
            elif self.config.source == "tushare" and self.ts_pro:
                return self.ts_pro.stock_basic(
                    exchange='', 
                    list_status='L',
                    fields='ts_code,symbol,name,area,industry,list_date'
                )
        except Exception as e:
            self.logger.error(f"Failed to get stock list: {e}")
            return pd.DataFrame()

    def _normalize_symbol(self, symbol: str) -> str:
        """标准化股票代码"""
        # 移除常见的后缀
        symbol = symbol.replace(".SH", "").replace(".SZ", "")
        
        # 确保是6位数字
        if len(symbol) == 6 and symbol.isdigit():
            return symbol
        else:
            raise ValueError(f"Invalid symbol format: {symbol}")

    def _get_cache_file_path(self, symbol: str, freq: str) -> Path:
        """生成缓存文件路径"""
        filename = f"{symbol}_{freq}.csv"
        return self.config.cache_dir / filename

    def _is_cache_valid(self, cache_file: Path) -> bool:
        """检查缓存是否有效"""
        if not cache_file.exists():
            return False
            
        # 检查文件修改时间
        file_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
        return (datetime.now() - file_time).days < self.config.cache_days

    def _fetch_from_akshare(
        self, 
        symbol: str, 
        start_date: str, 
        end_date: str, 
        freq: str
    ) -> pd.DataFrame:
        """从AkShare获取数据"""
        try:
            if freq == "daily":
                # 获取日线数据
                data = ak.stock_zh_a_hist(
                    symbol=symbol,
                    period="daily",
                    start_date=start_date.replace("-", ""),
                    end_date=end_date.replace("-", ""),
                    adjust=""  # 不复权
                )
            elif freq.endswith("min"):
                # 获取分钟数据
                data = ak.stock_zh_a_hist_min_em(
                    symbol=symbol,
                    start_date=f"{start_date} 09:30:00",
                    end_date=f"{end_date} 15:00:00",
                    period=freq
                )
            else:
                raise ValueError(f"Unsupported frequency: {freq}")
                
            # 添加延迟避免频繁请求
            time.sleep(0.1)
            return data
            
        except Exception as e:
            self.logger.error(f"AkShare fetch failed: {e}")
            raise

    def _fetch_from_tushare(
        self, 
        symbol: str, 
        start_date: str, 
        end_date: str, 
        freq: str
    ) -> pd.DataFrame:
        """从Tushare获取数据"""
        if not self.ts_pro:
            raise ValueError("Tushare not initialized")
            
        try:
            # 转换股票代码格式
            if symbol.startswith(('60', '68')):
                ts_code = f"{symbol}.SH"
            else:
                ts_code = f"{symbol}.SZ"
            
            if freq == "daily":
                data = self.ts_pro.daily(
                    ts_code=ts_code,
                    start_date=start_date.replace("-", ""),
                    end_date=end_date.replace("-", "")
                )
            else:
                # Tushare 分钟数据需要不同的接口
                data = self.ts_pro.stk_mins(
                    ts_code=ts_code,
                    start_date=f"{start_date} 09:30:00",
                    end_date=f"{end_date} 15:00:00",
                    freq=freq
                )
                
            time.sleep(0.1)  # API限制
            return data
            
        except Exception as e:
            self.logger.error(f"Tushare fetch failed: {e}")
            raise

    def _standardize_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """标准化数据格式"""
        if data.empty:
            return data
            
        # 根据数据源调整列名
        column_mapping = {
            # AkShare 格式
            '日期': 'date',
            '开盘': 'open',
            '收盘': 'close', 
            '最高': 'high',
            '最低': 'low',
            '成交量': 'volume',
            '成交额': 'amount',
            # Tushare 格式
            'trade_date': 'date',
            'ts_code': 'symbol',
            'vol': 'volume',
        }
        
        # 重命名列
        data = data.rename(columns=column_mapping)
        
        # 确保必要列存在
        required_cols = ['date', 'open', 'high', 'low', 'close', 'volume']
        available_cols = [col for col in required_cols if col in data.columns]
        
        if 'date' not in available_cols:
            raise ValueError("Date column not found")
            
        # 选择需要的列
        data = data[available_cols].copy()
        
        # 设置日期为索引
        data['date'] = pd.to_datetime(data['date'])
        data.set_index('date', inplace=True)
        
        # 确保数值列为数字类型
        numeric_cols = ['open', 'high', 'low', 'close', 'volume']
        for col in numeric_cols:
            if col in data.columns:
                data[col] = pd.to_numeric(data[col], errors='coerce')
        
        # 删除空值行
        data = data.dropna()
        
        # 按日期排序
        data = data.sort_index()
        
        return data

    def _cache_data(self, data: pd.DataFrame, cache_file: Path) -> None:
        """缓存数据到本地文件"""
        try:
            data.to_csv(cache_file)
            self.logger.debug(f"Data cached to {cache_file}")
        except Exception as e:
            self.logger.warning(f"Failed to cache data: {e}")

    def clear_cache(self, symbol: Optional[str] = None) -> None:
        """清理缓存文件"""
        try:
            if symbol:
                # 清理特定股票的缓存
                pattern = f"{self._normalize_symbol(symbol)}_*.csv"
                for cache_file in self.config.cache_dir.glob(pattern):
                    cache_file.unlink()
                    self.logger.info(f"Deleted cache file: {cache_file}")
            else:
                # 清理所有缓存
                for cache_file in self.config.cache_dir.glob("*.csv"):
                    cache_file.unlink()
                    self.logger.info(f"Deleted cache file: {cache_file}")
        except Exception as e:
            self.logger.error(f"Failed to clear cache: {e}")

    def get_cache_info(self) -> Dict[str, Any]:
        """获取缓存信息"""
        cache_files = list(self.config.cache_dir.glob("*.csv"))
        total_size = sum(f.stat().st_size for f in cache_files)
        
        return {
            "cache_dir": str(self.config.cache_dir),
            "file_count": len(cache_files),
            "total_size_mb": round(total_size / 1024 / 1024, 2),
            "files": [f.name for f in cache_files]
        }