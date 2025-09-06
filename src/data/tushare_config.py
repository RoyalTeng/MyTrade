"""
Tushare数据接口配置和数据获取模块
确保使用真实数据源，提供高质量的市场数据
"""

import tushare as ts
import pandas as pd
from datetime import datetime, timedelta
import logging
import os

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TushareDataProvider:
    """Tushare数据提供者类"""
    
    def __init__(self, token=None):
        """
        初始化Tushare数据接口
        
        Args:
            token (str): Tushare API token
        """
        # 使用提供的token
        self.token = token or "2e6561572caa8a088167963e5c9fb5b5b5dbacc83ac714e9596bdc47"
        
        # 设置token
        ts.set_token(self.token)
        self.pro = ts.pro_api()
        
        logger.info("Tushare API 初始化成功")
        
    def get_stock_basic(self):
        """获取股票基本信息"""
        try:
            df = self.pro.stock_basic(
                exchange='',
                list_status='L',
                fields='ts_code,symbol,name,area,industry,market,list_date'
            )
            logger.info(f"获取股票基本信息成功，共{len(df)}只股票")
            return df
        except Exception as e:
            logger.error(f"获取股票基本信息失败: {e}")
            return None
    
    def get_daily_data(self, ts_code, start_date=None, end_date=None):
        """
        获取股票日线数据
        
        Args:
            ts_code (str): 股票代码，如 '000001.SZ'
            start_date (str): 开始日期 'YYYYMMDD'
            end_date (str): 结束日期 'YYYYMMDD'
        """
        try:
            if not start_date:
                start_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y%m%d')
                
            df = self.pro.daily(
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date
            )
            
            if df is not None and not df.empty:
                # 按日期排序
                df = df.sort_values('trade_date')
                logger.info(f"获取{ts_code}日线数据成功，共{len(df)}条记录")
                return df
            else:
                logger.warning(f"未获取到{ts_code}的数据")
                return None
                
        except Exception as e:
            logger.error(f"获取{ts_code}日线数据失败: {e}")
            return None
    
    def get_index_daily(self, ts_code, start_date=None, end_date=None):
        """
        获取指数日线数据
        
        Args:
            ts_code (str): 指数代码，如 '000001.SH' (上证指数)
        """
        try:
            if not start_date:
                start_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y%m%d')
                
            df = self.pro.index_daily(
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date
            )
            
            if df is not None and not df.empty:
                df = df.sort_values('trade_date')
                logger.info(f"获取{ts_code}指数数据成功，共{len(df)}条记录")
                return df
            else:
                logger.warning(f"未获取到{ts_code}的指数数据")
                return None
                
        except Exception as e:
            logger.error(f"获取{ts_code}指数数据失败: {e}")
            return None
    
    def get_fund_basic(self):
        """获取基金基本信息"""
        try:
            df = self.pro.fund_basic(
                market='E',  # 交易所基金
                fields='ts_code,name,management,custodian,fund_type,found_date,due_date,list_date,invest_type,type,status'
            )
            
            if df is not None and not df.empty:
                logger.info(f"获取基金基本信息成功，共{len(df)}只基金")
                return df
            else:
                logger.warning("未获取到基金基本信息")
                return None
                
        except Exception as e:
            logger.error(f"获取基金基本信息失败: {e}")
            return None
    
    def get_fund_nav(self, ts_code, start_date=None, end_date=None):
        """
        获取基金净值数据
        
        Args:
            ts_code (str): 基金代码
            start_date (str): 开始日期
            end_date (str): 结束日期
        """
        try:
            if not start_date:
                start_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y%m%d')
                
            df = self.pro.fund_nav(
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date
            )
            
            if df is not None and not df.empty:
                df = df.sort_values('end_date')
                logger.info(f"获取{ts_code}基金净值成功，共{len(df)}条记录")
                return df
            else:
                logger.warning(f"未获取到{ts_code}的基金净值数据")
                return None
                
        except Exception as e:
            logger.error(f"获取{ts_code}基金净值失败: {e}")
            return None
    
    def get_money_supply(self):
        """获取货币供应量数据"""
        try:
            df = self.pro.money_supply(
                start_m=(datetime.now() - timedelta(days=365)).strftime('%Y%m'),
                end_m=datetime.now().strftime('%Y%m')
            )
            
            if df is not None and not df.empty:
                logger.info(f"获取货币供应量数据成功，共{len(df)}条记录")
                return df
            else:
                logger.warning("未获取到货币供应量数据")
                return None
                
        except Exception as e:
            logger.error(f"获取货币供应量数据失败: {e}")
            return None
    
    def get_market_sentiment(self, trade_date=None):
        """
        获取市场情绪指标
        
        Args:
            trade_date (str): 交易日期 'YYYYMMDD'
        """
        try:
            if not trade_date:
                trade_date = datetime.now().strftime('%Y%m%d')
                
            # 获取市场概况
            df = self.pro.daily_basic(
                trade_date=trade_date,
                fields='ts_code,trade_date,turnover_rate,volume_ratio,pe,pb'
            )
            
            if df is not None and not df.empty:
                logger.info(f"获取{trade_date}市场情绪数据成功，共{len(df)}只股票")
                return df
            else:
                logger.warning(f"未获取到{trade_date}的市场情绪数据")
                return None
                
        except Exception as e:
            logger.error(f"获取市场情绪数据失败: {e}")
            return None
    
    def get_top10_holders(self, ts_code, period=None):
        """
        获取基金十大股东
        
        Args:
            ts_code (str): 基金代码
            period (str): 报告期，格式YYYYMMDD
        """
        try:
            if not period:
                # 默认获取最近的报告期数据
                period = None
                
            df = self.pro.fund_top10(
                ts_code=ts_code,
                period=period
            )
            
            if df is not None and not df.empty:
                logger.info(f"获取{ts_code}十大重仓股成功，共{len(df)}条记录")
                return df
            else:
                logger.warning(f"未获取到{ts_code}的重仓股数据")
                return None
                
        except Exception as e:
            logger.error(f"获取{ts_code}重仓股数据失败: {e}")
            return None
    
    def test_connection(self):
        """测试Tushare连接状态"""
        try:
            # 获取少量测试数据
            df = self.pro.trade_cal(exchange='SSE', start_date='20250901', end_date='20250910')
            
            if df is not None and not df.empty:
                logger.info("Tushare API连接测试成功")
                return True, f"连接成功，获取到{len(df)}条交易日历记录"
            else:
                logger.warning("Tushare API连接测试失败：未获取到数据")
                return False, "连接失败：未获取到数据"
                
        except Exception as e:
            logger.error(f"Tushare API连接测试失败: {e}")
            return False, f"连接失败：{str(e)}"

def main():
    """测试Tushare数据接口"""
    print("=== Tushare数据接口测试 ===")
    
    # 初始化数据提供者
    provider = TushareDataProvider()
    
    # 测试连接
    success, message = provider.test_connection()
    print(f"连接测试: {'成功' if success else '失败'} - {message}")
    
    if success:
        # 测试获取主要指数数据
        print("\n=== 测试主要指数数据 ===")
        
        indices = {
            '000001.SH': '上证指数',
            '399001.SZ': '深证成指', 
            '399006.SZ': '创业板指'
        }
        
        for code, name in indices.items():
            df = provider.get_index_daily(code)
            if df is not None and not df.empty:
                latest = df.iloc[-1]
                print(f"{name}({code}): 最新收盘价 {latest['close']:.2f}, 涨跌幅 {latest.get('pct_chg', 0):.2f}%")
        
        print(f"\nTushare数据接口配置完成，token已设置")

if __name__ == "__main__":
    main()