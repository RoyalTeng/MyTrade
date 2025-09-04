#!/usr/bin/env python3
"""
Tushare数据源集成模块

使用Tushare获取高质量的A股市场数据
需要申请Tushare API Token: https://tushare.pro/register
"""

import sys
import os
import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import warnings

# 添加src到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from test_encoding_fix import safe_print

warnings.filterwarnings('ignore')


class TushareDataSource:
    """Tushare数据源类"""
    
    def __init__(self, token=None):
        self.token = token
        self.pro = None
        self.init_tushare()
    
    def init_tushare(self):
        """初始化Tushare"""
        try:
            import tushare as ts
            
            # 如果没有提供token，尝试从环境变量获取
            if not self.token:
                self.token = os.environ.get('TUSHARE_TOKEN')
            
            if not self.token:
                safe_print("⚠️ 请提供Tushare API Token")
                safe_print("📝 获取步骤:")
                safe_print("   1. 访问 https://tushare.pro/register")
                safe_print("   2. 注册账号并实名认证")
                safe_print("   3. 获取API Token")
                safe_print("   4. 设置环境变量: TUSHARE_TOKEN=你的token")
                safe_print("   或在代码中直接提供token")
                return False
            
            # 设置token
            ts.set_token(self.token)
            self.pro = ts.pro_api()
            safe_print("✅ Tushare初始化成功")
            return True
            
        except ImportError:
            safe_print("❌ 请先安装tushare: pip install tushare")
            return False
        except Exception as e:
            safe_print(f"❌ Tushare初始化失败: {e}")
            return False
    
    def get_stock_basic(self):
        """获取股票基本信息"""
        if not self.pro:
            return pd.DataFrame()
        
        try:
            safe_print("📊 获取股票基本信息...")
            
            # 获取股票基本信息
            stock_basic = self.pro.stock_basic(
                exchange='',  # 交易所 SSE上交所 SZSE深交所
                list_status='L',  # 上市状态 L上市 D退市 P暂停上市
                fields='ts_code,symbol,name,area,industry,market,list_date'
            )
            
            safe_print(f"  ✅ 获取{len(stock_basic)}只股票基本信息")
            return stock_basic
            
        except Exception as e:
            safe_print(f"❌ 获取股票基本信息失败: {e}")
            return pd.DataFrame()
    
    def get_daily_data(self, ts_code, start_date=None, end_date=None, days=120):
        """获取日线数据"""
        if not self.pro:
            return pd.DataFrame()
        
        try:
            # 设置日期范围
            if not end_date:
                end_date = datetime.now().strftime('%Y%m%d')
            if not start_date:
                start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
            
            safe_print(f"📈 获取{ts_code}日线数据 ({start_date} - {end_date})")
            
            # 获取日线数据
            df = self.pro.daily(
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date
            )
            
            if not df.empty:
                # 按日期排序
                df = df.sort_values('trade_date')
                safe_print(f"  ✅ 获取{len(df)}天交易数据")
                return df
            else:
                safe_print(f"  ⚠️ 未获取到{ts_code}的数据")
                return pd.DataFrame()
                
        except Exception as e:
            safe_print(f"❌ 获取日线数据失败: {e}")
            return pd.DataFrame()
    
    def get_realtime_quotes(self, ts_codes):
        """获取实时行情"""
        if not self.pro:
            return pd.DataFrame()
        
        try:
            safe_print("📊 获取实时行情数据...")
            
            # Tushare的实时行情接口
            if isinstance(ts_codes, str):
                ts_codes = [ts_codes]
            
            # 获取最新交易日数据（模拟实时）
            trade_date = datetime.now().strftime('%Y%m%d')
            
            all_quotes = []
            for ts_code in ts_codes:
                try:
                    # 获取最近的交易数据
                    df = self.pro.daily(
                        ts_code=ts_code,
                        start_date=trade_date,
                        end_date=trade_date
                    )
                    
                    if not df.empty:
                        all_quotes.append(df.iloc[0])
                    else:
                        # 如果当天没有数据，获取最近一个交易日
                        df = self.pro.daily(
                            ts_code=ts_code,
                            start_date='',
                            end_date=''
                        )
                        if not df.empty:
                            df = df.sort_values('trade_date', ascending=False)
                            all_quotes.append(df.iloc[0])
                            
                except Exception as e:
                    safe_print(f"  ⚠️ 获取{ts_code}行情失败: {e}")
                    continue
            
            if all_quotes:
                result = pd.DataFrame(all_quotes)
                safe_print(f"  ✅ 获取{len(result)}只股票行情")
                return result
            else:
                return pd.DataFrame()
                
        except Exception as e:
            safe_print(f"❌ 获取实时行情失败: {e}")
            return pd.DataFrame()
    
    def get_financial_data(self, ts_code, period='20240630'):
        """获取财务数据"""
        if not self.pro:
            return {}
        
        try:
            safe_print(f"💰 获取{ts_code}财务数据...")
            
            financial_data = {}
            
            # 获取利润表数据
            income = self.pro.income(ts_code=ts_code, period=period)
            if not income.empty:
                income_data = income.iloc[0]
                financial_data['income'] = {
                    'revenue': float(income_data.get('revenue', 0)),  # 营业收入
                    'operate_profit': float(income_data.get('operate_profit', 0)),  # 营业利润
                    'total_profit': float(income_data.get('total_profit', 0)),  # 利润总额
                    'n_income': float(income_data.get('n_income', 0)),  # 净利润
                    'basic_eps': float(income_data.get('basic_eps', 0)),  # 基本每股收益
                }
            
            # 获取资产负债表数据
            balancesheet = self.pro.balancesheet(ts_code=ts_code, period=period)
            if not balancesheet.empty:
                balance_data = balancesheet.iloc[0]
                financial_data['balance'] = {
                    'total_assets': float(balance_data.get('total_assets', 0)),  # 总资产
                    'total_liab': float(balance_data.get('total_liab', 0)),  # 总负债
                    'total_hldr_eqy_exc_min_int': float(balance_data.get('total_hldr_eqy_exc_min_int', 0)),  # 股东权益
                }
            
            # 获取现金流量表数据
            cashflow = self.pro.cashflow(ts_code=ts_code, period=period)
            if not cashflow.empty:
                cash_data = cashflow.iloc[0]
                financial_data['cashflow'] = {
                    'n_cashflow_act': float(cash_data.get('n_cashflow_act', 0)),  # 经营活动现金流
                    'n_cashflow_inv_act': float(cash_data.get('n_cashflow_inv_act', 0)),  # 投资活动现金流
                    'n_cashflow_fin_act': float(cash_data.get('n_cashflow_fin_act', 0)),  # 筹资活动现金流
                }
            
            # 获取主要财务指标
            fina_indicator = self.pro.fina_indicator(ts_code=ts_code, period=period)
            if not fina_indicator.empty:
                indicator_data = fina_indicator.iloc[0]
                financial_data['indicators'] = {
                    'roe': float(indicator_data.get('roe', 0)),  # 净资产收益率
                    'roa': float(indicator_data.get('roa', 0)),  # 总资产收益率
                    'gross_margin': float(indicator_data.get('gross_margin', 0)),  # 销售毛利率
                    'debt_to_assets': float(indicator_data.get('debt_to_assets', 0)),  # 资产负债率
                    'current_ratio': float(indicator_data.get('current_ratio', 0)),  # 流动比率
                    'quick_ratio': float(indicator_data.get('quick_ratio', 0)),  # 速动比率
                }
            
            safe_print(f"  ✅ 获取财务数据成功")
            return financial_data
            
        except Exception as e:
            safe_print(f"❌ 获取财务数据失败: {e}")
            return {}
    
    def get_index_daily(self, ts_code, start_date=None, end_date=None, days=30):
        """获取指数数据"""
        if not self.pro:
            return pd.DataFrame()
        
        try:
            # 设置日期范围
            if not end_date:
                end_date = datetime.now().strftime('%Y%m%d')
            if not start_date:
                start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
            
            safe_print(f"📊 获取指数{ts_code}数据...")
            
            # 获取指数数据
            df = self.pro.index_daily(
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date
            )
            
            if not df.empty:
                df = df.sort_values('trade_date')
                safe_print(f"  ✅ 获取指数数据{len(df)}天")
                return df
            else:
                safe_print(f"  ⚠️ 未获取到指数数据")
                return pd.DataFrame()
                
        except Exception as e:
            safe_print(f"❌ 获取指数数据失败: {e}")
            return pd.DataFrame()
    
    def get_industry_classify(self):
        """获取行业分类"""
        if not self.pro:
            return pd.DataFrame()
        
        try:
            safe_print("🏭 获取行业分类数据...")
            
            # 获取申万行业分类
            industry = self.pro.index_classify(level='L2', src='SW2021')
            
            safe_print(f"  ✅ 获取{len(industry)}个行业分类")
            return industry
            
        except Exception as e:
            safe_print(f"❌ 获取行业分类失败: {e}")
            return pd.DataFrame()
    
    def calculate_technical_indicators(self, df):
        """计算技术指标"""
        if df.empty:
            return {}
        
        try:
            safe_print("🔍 计算技术指标...")
            
            # 确保数据按日期排序
            df = df.sort_values('trade_date')
            closes = df['close'].values
            volumes = df['vol'].values
            
            indicators = {
                'ma5': float(np.mean(closes[-5:])) if len(closes) >= 5 else 0,
                'ma10': float(np.mean(closes[-10:])) if len(closes) >= 10 else 0,
                'ma20': float(np.mean(closes[-20:])) if len(closes) >= 20 else 0,
                'ma60': float(np.mean(closes[-60:])) if len(closes) >= 60 else 0,
                'volatility': float(np.std(closes[-20:])) if len(closes) >= 20 else 0,
                'highest_20d': float(np.max(closes[-20:])) if len(closes) >= 20 else 0,
                'lowest_20d': float(np.min(closes[-20:])) if len(closes) >= 20 else 0,
                'highest_60d': float(np.max(closes[-60:])) if len(closes) >= 60 else 0,
                'lowest_60d': float(np.min(closes[-60:])) if len(closes) >= 60 else 0,
                'avg_volume_20d': float(np.mean(volumes[-20:])) if len(volumes) >= 20 else 0,
                'current_price': float(closes[-1]) if len(closes) > 0 else 0,
                'latest_date': str(df.iloc[-1]['trade_date']) if len(df) > 0 else '',
            }
            
            safe_print(f"  ✅ 技术指标计算完成")
            return indicators
            
        except Exception as e:
            safe_print(f"❌ 技术指标计算失败: {e}")
            return {}


def create_tushare_config():
    """创建Tushare配置文件"""
    config_file = Path(__file__).parent / 'tushare_config.json'
    
    config = {
        "api_info": {
            "name": "Tushare",
            "website": "https://tushare.pro",
            "description": "专业金融数据接口，提供股票、基金、期货等多种金融数据"
        },
        "token_setup": {
            "method1": "环境变量设置",
            "command1": "set TUSHARE_TOKEN=你的token  (Windows)",
            "command2": "export TUSHARE_TOKEN=你的token  (Linux/Mac)",
            "method2": "代码中设置",
            "code": "TushareDataSource(token='你的token')"
        },
        "data_types": {
            "basic": "股票基本信息",
            "daily": "日线行情",
            "realtime": "实时行情",
            "financial": "财务数据",
            "index": "指数数据", 
            "industry": "行业分类"
        },
        "usage_limits": {
            "免费用户": "每分钟200次",
            "VIP用户": "每分钟400次",
            "专业版": "每分钟800次"
        }
    }
    
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    safe_print(f"📝 Tushare配置文件已创建: {config_file}")


def test_tushare_connection(token=None):
    """测试Tushare连接"""
    safe_print("🧪 测试Tushare连接...")
    
    tushare_source = TushareDataSource(token=token)
    
    if not tushare_source.pro:
        safe_print("❌ Tushare连接失败")
        return False
    
    try:
        # 测试获取股票基本信息
        basic_info = tushare_source.get_stock_basic()
        if not basic_info.empty:
            safe_print(f"✅ 基本信息测试成功，获取{len(basic_info)}只股票")
        
        # 测试获取紫金矿业数据
        zijin_data = tushare_source.get_daily_data('601899.SH', days=30)
        if not zijin_data.empty:
            safe_print(f"✅ 日线数据测试成功，获取紫金矿业{len(zijin_data)}天数据")
            
            # 计算技术指标
            indicators = tushare_source.calculate_technical_indicators(zijin_data)
            if indicators:
                safe_print(f"✅ 技术指标计算成功，当前价格: {indicators.get('current_price', 0):.2f}元")
        
        # 测试获取上证指数
        index_data = tushare_source.get_index_daily('000001.SH', days=10)
        if not index_data.empty:
            safe_print(f"✅ 指数数据测试成功，获取上证指数{len(index_data)}天数据")
        
        safe_print("🎉 Tushare连接测试全部通过！")
        return True
        
    except Exception as e:
        safe_print(f"❌ Tushare测试失败: {e}")
        return False


def main():
    """主函数"""
    safe_print("=" * 80)
    safe_print("              Tushare数据源集成系统")
    safe_print("=" * 80)
    safe_print("")
    
    # 创建配置文件
    create_tushare_config()
    
    # 检查token
    token = os.environ.get('TUSHARE_TOKEN')
    if not token:
        safe_print("⚠️ 未检测到TUSHARE_TOKEN环境变量")
        safe_print("")
        safe_print("📝 设置步骤:")
        safe_print("1. 访问 https://tushare.pro/register 注册账号")
        safe_print("2. 完成实名认证")
        safe_print("3. 获取API Token")
        safe_print("4. 设置环境变量:")
        safe_print("   Windows: set TUSHARE_TOKEN=你的token")
        safe_print("   Linux/Mac: export TUSHARE_TOKEN=你的token")
        safe_print("")
        safe_print("💡 或在代码中直接传入token参数")
        return False
    
    # 测试连接
    success = test_tushare_connection(token)
    
    if success:
        safe_print("")
        safe_print("✅ Tushare数据源集成成功！")
        safe_print("📊 可用数据类型:")
        safe_print("   • 股票基本信息")
        safe_print("   • 日线行情数据") 
        safe_print("   • 实时行情")
        safe_print("   • 财务数据")
        safe_print("   • 指数数据")
        safe_print("   • 行业分类")
        safe_print("")
        safe_print("🔧 使用方法:")
        safe_print("   from tushare_data_source import TushareDataSource")
        safe_print("   ts_source = TushareDataSource()")
        safe_print("   data = ts_source.get_daily_data('601899.SH')")
        
    return success


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)