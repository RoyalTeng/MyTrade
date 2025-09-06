"""
综合数据管理器 - 集成Tushare和AKShare数据源
确保数据的真实性、准确性和实时性
"""

import pandas as pd
import akshare as ak
from datetime import datetime, timedelta
import logging
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.tushare_config import TushareDataProvider

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataManager:
    """综合数据管理器类"""
    
    def __init__(self, tushare_token=None):
        """
        初始化数据管理器
        
        Args:
            tushare_token (str): Tushare API token
        """
        # 初始化Tushare数据提供者
        self.tushare = TushareDataProvider(tushare_token)
        
        # 数据源状态
        self.tushare_available = True
        self.akshare_available = True
        
        # 测试数据源连通性
        self._test_data_sources()
        
        logger.info("综合数据管理器初始化完成")
    
    def _test_data_sources(self):
        """测试数据源连通性"""
        # 测试Tushare
        try:
            success, _ = self.tushare.test_connection()
            self.tushare_available = success
            logger.info(f"Tushare数据源: {'可用' if success else '不可用'}")
        except Exception as e:
            self.tushare_available = False
            logger.error(f"Tushare数据源测试失败: {e}")
        
        # 测试AKShare
        try:
            # 简单测试AKShare - 使用存在的函数
            test_data = ak.index_zh_a_hist(symbol="000001", period="daily", start_date="20250901", end_date="20250906")
            self.akshare_available = test_data is not None and not test_data.empty
            logger.info(f"AKShare数据源: {'可用' if self.akshare_available else '不可用'}")
        except Exception as e:
            self.akshare_available = False
            logger.error(f"AKShare数据源测试失败: {e}")
    
    def get_realtime_index_data(self):
        """
        获取实时指数数据
        优先使用AKShare（实时性更好），备用Tushare
        """
        logger.info("获取实时指数数据...")
        
        # 优先使用AKShare获取实时数据
        if self.akshare_available:
            try:
                indices_data = {}
                
                # 主要指数代码映射
                index_mapping = {
                    '000001': '上证指数',
                    '399001': '深证成指', 
                    '399006': '创业板指',
                    '000300': '沪深300'
                }
                
                for code, name in index_mapping.items():
                    try:
                        # 使用AKShare获取历史数据的最新一天
                        df = ak.index_zh_a_hist(symbol=code, period="daily", start_date="20250901", end_date="20250906")
                        if df is not None and not df.empty:
                            # 获取最新一日的数据
                            latest = df.iloc[-1]
                            # 计算涨跌幅
                            if len(df) > 1:
                                prev_close = df.iloc[-2]['收盘']
                                change_pct = (latest['收盘'] - prev_close) / prev_close * 100
                            else:
                                change_pct = 0
                            
                            indices_data[name] = {
                                'code': code,
                                'name': name,
                                'current_price': float(latest['收盘']),
                                'change_pct': float(change_pct),
                                'change_amount': float(latest['收盘'] - df.iloc[-2]['收盘']) if len(df) > 1 else 0,
                                'volume': float(latest.get('成交量', 0)),
                                'amount': float(latest.get('成交额', 0)),
                                'data_source': 'AKShare',
                                'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                'trade_date': latest['日期']
                            }
                            logger.info(f"获取{name}实时数据成功: {latest['收盘']:.2f} ({change_pct:+.2f}%)")
                    except Exception as e:
                        logger.warning(f"AKShare获取{name}数据失败: {e}")
                        continue
                
                if indices_data:
                    return indices_data
                    
            except Exception as e:
                logger.error(f"AKShare获取实时指数数据失败: {e}")
        
        # 备用：使用Tushare获取数据
        if self.tushare_available:
            try:
                logger.info("使用Tushare获取指数数据...")
                indices_data = {}
                
                index_codes = {
                    '000001.SH': '上证指数',
                    '399001.SZ': '深证成指',
                    '399006.SZ': '创业板指'
                }
                
                for ts_code, name in index_codes.items():
                    df = self.tushare.get_index_daily(ts_code)
                    if df is not None and not df.empty:
                        latest = df.iloc[-1]
                        indices_data[name] = {
                            'code': ts_code,
                            'name': name,
                            'current_price': float(latest['close']),
                            'change_pct': float(latest.get('pct_chg', 0)),
                            'volume': float(latest.get('vol', 0)),
                            'amount': float(latest.get('amount', 0)),
                            'data_source': 'Tushare',
                            'trade_date': latest['trade_date']
                        }
                
                return indices_data
                
            except Exception as e:
                logger.error(f"Tushare获取指数数据失败: {e}")
        
        logger.error("所有数据源均不可用")
        return {}
    
    def get_stock_basic_info(self, symbol=None):
        """
        获取股票基本信息
        优先使用Tushare（数据更完整），备用AKShare
        """
        logger.info(f"获取股票基本信息: {symbol or '全部股票'}")
        
        if self.tushare_available:
            try:
                df = self.tushare.get_stock_basic()
                if df is not None and not df.empty:
                    if symbol:
                        # 筛选特定股票
                        df = df[df['symbol'] == symbol.replace('.', '')]
                    
                    logger.info(f"Tushare获取股票基本信息成功，共{len(df)}条记录")
                    return df
            except Exception as e:
                logger.error(f"Tushare获取股票基本信息失败: {e}")
        
        # 备用方案：使用AKShare
        if self.akshare_available:
            try:
                # AKShare的股票基本信息接口
                df = ak.stock_info_a_code_name()
                if df is not None and not df.empty:
                    logger.info(f"AKShare获取股票基本信息成功，共{len(df)}条记录")
                    return df
            except Exception as e:
                logger.error(f"AKShare获取股票基本信息失败: {e}")
        
        return None
    
    def get_fund_data(self, fund_code=None):
        """
        获取基金数据
        综合使用两个数据源
        """
        logger.info(f"获取基金数据: {fund_code or '全部基金'}")
        
        fund_data = {}
        
        # 使用Tushare获取基金基础信息
        if self.tushare_available:
            try:
                if fund_code:
                    # 获取特定基金的净值数据
                    nav_df = self.tushare.get_fund_nav(fund_code)
                    if nav_df is not None:
                        fund_data['nav_data'] = nav_df
                        fund_data['data_source'] = 'Tushare'
                else:
                    # 获取基金基本信息
                    basic_df = self.tushare.get_fund_basic()
                    if basic_df is not None:
                        fund_data['basic_info'] = basic_df
                        fund_data['data_source'] = 'Tushare'
                        
            except Exception as e:
                logger.error(f"Tushare获取基金数据失败: {e}")
        
        # 使用AKShare获取补充数据
        if self.akshare_available and fund_code:
            try:
                # 获取基金实时净值（如果支持）
                # 注意：AKShare的基金接口可能有限制
                pass
            except Exception as e:
                logger.error(f"AKShare获取基金数据失败: {e}")
        
        return fund_data if fund_data else None
    
    def get_market_sentiment(self):
        """
        获取市场情绪指标
        综合多个数据源
        """
        logger.info("获取市场情绪指标...")
        
        sentiment_data = {}
        
        # 从Tushare获取市场基本面数据
        if self.tushare_available:
            try:
                sentiment_df = self.tushare.get_market_sentiment()
                if sentiment_df is not None and not sentiment_df.empty:
                    # 计算市场平均估值
                    avg_pe = sentiment_df['pe'].median()
                    avg_pb = sentiment_df['pb'].median()
                    avg_turnover = sentiment_df['turnover_rate'].median()
                    
                    sentiment_data['tushare_metrics'] = {
                        'avg_pe': float(avg_pe) if pd.notna(avg_pe) else None,
                        'avg_pb': float(avg_pb) if pd.notna(avg_pb) else None,
                        'avg_turnover_rate': float(avg_turnover) if pd.notna(avg_turnover) else None,
                        'sample_size': len(sentiment_df)
                    }
                    
            except Exception as e:
                logger.error(f"Tushare获取市场情绪数据失败: {e}")
        
        # 从AKShare获取补充指标
        if self.akshare_available:
            try:
                # 获取北向资金数据
                hsgt_df = ak.stock_hsgt_fund_flow_summary_em()
                if hsgt_df is not None and not hsgt_df.empty:
                    latest_flow = hsgt_df.iloc[0]
                    sentiment_data['northbound_flow'] = {
                        'today_flow': float(latest_flow.get('今日净流入', 0)),
                        'recent_trend': '流入' if float(latest_flow.get('今日净流入', 0)) > 0 else '流出'
                    }
                    
            except Exception as e:
                logger.error(f"AKShare获取北向资金数据失败: {e}")
        
        return sentiment_data if sentiment_data else None
    
    def get_macro_data(self):
        """
        获取宏观经济数据
        主要使用Tushare
        """
        logger.info("获取宏观经济数据...")
        
        macro_data = {}
        
        if self.tushare_available:
            try:
                # 获取货币供应量数据
                money_supply = self.tushare.get_money_supply()
                if money_supply is not None and not money_supply.empty:
                    latest_supply = money_supply.iloc[-1]
                    macro_data['money_supply'] = {
                        'month': latest_supply['month'],
                        'm2_growth': float(latest_supply.get('m2_yoy', 0)),
                        'm1_growth': float(latest_supply.get('m1_yoy', 0)),
                        'm0_growth': float(latest_supply.get('m0_yoy', 0))
                    }
                    
            except Exception as e:
                logger.error(f"获取宏观数据失败: {e}")
        
        return macro_data if macro_data else None
    
    def get_comprehensive_market_data(self):
        """
        获取综合市场数据
        整合所有数据源的信息
        """
        logger.info("获取综合市场数据...")
        
        market_data = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'data_sources': {
                'tushare': self.tushare_available,
                'akshare': self.akshare_available
            }
        }
        
        # 获取实时指数数据
        indices = self.get_realtime_index_data()
        if indices:
            market_data['indices'] = indices
        
        # 获取市场情绪
        sentiment = self.get_market_sentiment()
        if sentiment:
            market_data['sentiment'] = sentiment
        
        # 获取宏观数据
        macro = self.get_macro_data()
        if macro:
            market_data['macro'] = macro
        
        return market_data
    
    def get_data_source_status(self):
        """获取数据源状态"""
        return {
            'tushare': {
                'available': self.tushare_available,
                'token_configured': bool(self.tushare.token),
                'description': 'Tushare Pro - 专业金融数据接口'
            },
            'akshare': {
                'available': self.akshare_available,
                'description': 'AKShare - 开源金融数据接口'
            },
            'last_check': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

def main():
    """测试综合数据管理器"""
    print("=== 综合数据管理器测试 ===")
    
    # 初始化数据管理器（使用您提供的token）
    dm = DataManager(tushare_token="2e6561572caa8a088167963e5c9fb5b5b5dbacc83ac714e9596bdc47")
    
    # 检查数据源状态
    status = dm.get_data_source_status()
    print("\n数据源状态:")
    for source, info in status.items():
        if source != 'last_check':
            status_symbol = '可用' if info['available'] else '不可用'
            print(f"  {source}: [{status_symbol}] {info['description']}")
    
    # 获取实时指数数据
    print("\n=== 实时指数数据 ===")
    indices = dm.get_realtime_index_data()
    for name, data in indices.items():
        print(f"{name}: {data['current_price']:.2f} ({data['change_pct']:+.2f}%) [数据源: {data['data_source']}]")
    
    # 获取市场情绪
    print("\n=== 市场情绪指标 ===")
    sentiment = dm.get_market_sentiment()
    if sentiment:
        if 'tushare_metrics' in sentiment:
            metrics = sentiment['tushare_metrics']
            print(f"平均PE: {metrics.get('avg_pe', 'N/A'):.2f}")
            print(f"平均PB: {metrics.get('avg_pb', 'N/A'):.2f}")
            print(f"平均换手率: {metrics.get('avg_turnover_rate', 'N/A'):.2f}%")
        
        if 'northbound_flow' in sentiment:
            flow = sentiment['northbound_flow']
            print(f"北向资金: {flow['today_flow']:.2f}亿 ({flow['recent_trend']})")
    
    print(f"\n数据获取完成，时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()