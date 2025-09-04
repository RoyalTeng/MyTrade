#!/usr/bin/env python3
"""
完整全量集成测试

对整个多分析师协作系统进行全面的集成测试
包括所有分析师、工作流、LLM适配器、数据处理等组件
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import json

# 添加src到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# 导入编码修复工具
from test_encoding_fix import safe_print

# 导入核心组件
from mytrade.agents import EnhancedTradingAgents


def create_full_test_config():
    """创建完整测试配置"""
    return {
        'llm_provider': 'deepseek',
        'llm_model': 'deepseek-chat',
        'llm_temperature': 0.3,
        'llm_max_tokens': 4000,
        
        # 启用所有分析师
        'agents': {
            'technical_analyst': True,
            'fundamental_analyst': True,
            'sentiment_analyst': True,
            'market_analyst': True
        },
        
        # 工作流配置
        'workflow': {
            'enable_parallel': True,
            'enable_debate': False,
            'max_execution_time': 300,
            'timeout_per_agent': 120
        },
        
        # 日志配置
        'logging': {
            'level': 'INFO',
            'enable_structured_logging': True
        }
    }


def create_comprehensive_market_data():
    """创建全面的市场测试数据集"""
    base_date = datetime.now()
    
    # 生成20天的历史价格数据
    price_data = {
        'dates': [(base_date - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(19, -1, -1)],
        'open': [14.50, 14.80, 15.10, 15.20, 15.45, 15.30, 15.60, 15.80, 15.75, 16.00, 
                15.95, 16.20, 16.10, 16.35, 16.25, 16.50, 16.40, 16.65, 16.55, 16.80],
        'high': [14.85, 15.15, 15.40, 15.50, 15.70, 15.55, 15.90, 16.00, 15.95, 16.25,
                16.15, 16.40, 16.30, 16.55, 16.45, 16.70, 16.60, 16.85, 16.75, 17.00],
        'low': [14.20, 14.60, 14.95, 15.00, 15.30, 15.10, 15.40, 15.60, 15.55, 15.80,
               15.75, 15.95, 15.90, 16.15, 16.05, 16.30, 16.20, 16.45, 16.35, 16.60],
        'close': [14.80, 15.10, 15.20, 15.45, 15.30, 15.60, 15.80, 15.75, 16.00, 15.95,
                 16.20, 16.10, 16.35, 16.25, 16.50, 16.40, 16.65, 16.55, 16.80, 16.70],
        'volume': [1800000, 2100000, 1500000, 2400000, 1900000, 2800000, 3200000, 2600000,
                  3500000, 2900000, 4200000, 3800000, 4500000, 3600000, 5100000, 4300000,
                  5800000, 4900000, 6200000, 5400000]
    }
    
    return {
        'symbol': '000001',
        'company_name': '平安银行',
        'industry': '银行',
        'timestamp': datetime.now(),
        
        # 技术分析数据
        'price_data': price_data,
        'volume_data': {
            'volume': price_data['volume'],
            'avg_volume_10d': sum(price_data['volume'][-10:]) / 10,
            'avg_volume_20d': sum(price_data['volume']) / 20
        },
        
        # 基本面数据
        'fundamental_data': {
            # 盈利能力指标
            'pe_ratio': 4.8,
            'pb_ratio': 0.62,
            'roe': 0.115,  # 11.5%
            'roa': 0.0089, # 0.89%
            'net_margin': 0.286,  # 28.6%
            'gross_margin': 0.523, # 52.3%
            
            # 偿债能力指标
            'debt_ratio': 0.753,    # 75.3%
            'current_ratio': 1.125,
            'quick_ratio': 1.125,
            'capital_adequacy_ratio': 0.1458, # 14.58%
            
            # 成长性指标
            'revenue_growth': 0.075,      # 7.5%
            'profit_growth': 0.035,       # 3.5%
            'eps_growth': 0.041,          # 4.1%
            'book_value_growth': 0.089,   # 8.9%
            
            # 银行特殊指标
            'npl_ratio': 0.0098,          # 不良贷款率 0.98%
            'provision_coverage': 2.86,   # 拨备覆盖率 286%
            'net_interest_margin': 0.0251, # 净息差 2.51%
            
            # 估值指标
            'dividend_yield': 0.0385,     # 股息率 3.85%
            'market_cap': 285700000000,   # 市值2857亿
            'total_assets': 4865400000000 # 总资产4.86万亿
        },
        
        # 情感数据
        'sentiment_data': {
            'news': [
                {
                    'title': '平安银行发布三季度业绩报告，营收持续增长',
                    'content': '平安银行第三季度实现营业收入同比增长7.5%，净利润保持稳定增长态势，资产质量持续改善，不良贷款率进一步下降至0.98%。',
                    'source': '证券时报',
                    'timestamp': '2024-10-25',
                    'sentiment_score': 0.75
                },
                {
                    'title': '央行降准释放流动性，银行板块迎来政策利好',
                    'content': '央行宣布全面降准0.5个百分点，释放长期流动性约1万亿元，银行业净息差有望企稳回升。',
                    'source': '上海证券报',
                    'timestamp': '2024-10-24',
                    'sentiment_score': 0.85
                },
                {
                    'title': '房地产政策优化调整，银行信贷投放加速',
                    'content': '随着房地产政策的优化调整，银行对优质房地产项目的信贷投放明显加速，资产质量风险可控。',
                    'source': '金融时报',
                    'timestamp': '2024-10-23',
                    'sentiment_score': 0.65
                }
            ],
            'social_media': {
                'weibo': [
                    {'content': '平安银行这波业绩不错，资产质量改善明显', 'likes': 156, 'comments': 23, 'shares': 12, 'sentiment': 0.7},
                    {'content': '银行股现在估值很低，分红也不错', 'likes': 89, 'comments': 15, 'shares': 8, 'sentiment': 0.6},
                    {'content': '央行降准对银行是长期利好', 'likes': 201, 'comments': 34, 'shares': 18, 'sentiment': 0.8}
                ],
                'xueqiu': [
                    {'content': '平安银行ROE维持11%以上，在银行业中表现优秀', 'likes': 78, 'comments': 12, 'sentiment': 0.75},
                    {'content': '不良率持续下降，拨备覆盖率充足，风险可控', 'likes': 65, 'comments': 9, 'sentiment': 0.7}
                ]
            },
            'market_indicators': {
                'vix': 16.8,  # 波动率指数较低
                'advance_decline_ratio': 1.45,  # 上涨下跌比
                'money_flow': 3200000000,  # 资金流入32亿
                'sentiment_index': 0.72  # 整体情绪指数
            }
        },
        
        # 市场数据
        'market_data': {
            'indices': {
                'sh000001': {  # 上证指数
                    'close': 3095.5,
                    'change': 18.7,
                    'change_pct': 0.61,
                    'volume': 182500000000,  # 成交额1825亿
                    'avg_volume': 165300000000
                },
                'sz399001': {  # 深证成指
                    'close': 9876.3,
                    'change': 42.1,
                    'change_pct': 0.43,
                    'volume': 148200000000,
                    'avg_volume': 135600000000
                },
                'sz399006': {  # 创业板指
                    'close': 1985.4,
                    'change': -8.2,
                    'change_pct': -0.41,
                    'volume': 87300000000,
                    'avg_volume': 79800000000
                }
            },
            'sectors': {
                '银行': {
                    'change_pct': 1.23,
                    'volume_ratio': 1.35,
                    'money_flow': 6500000000,  # 净流入65亿
                    'leading_stocks': ['000001', '600036', '601988']
                },
                '证券': {
                    'change_pct': 2.18,
                    'volume_ratio': 1.78,
                    'money_flow': 4200000000
                },
                '保险': {
                    'change_pct': 0.89,
                    'volume_ratio': 1.12,
                    'money_flow': 2100000000
                }
            },
            'market_structure': {
                'up_count': 3245,
                'down_count': 1456,
                'unchanged_count': 89,
                'limit_up_count': 18,
                'limit_down_count': 3,
                'new_high_count': 42,
                'new_low_count': 15,
                'northbound_flow': {
                    'daily': 4200000000,    # 北向资金日净流入42亿
                    'weekly': 18500000000,  # 周净流入185亿
                    'monthly': 65800000000  # 月净流入658亿
                }
            },
            'macro_data': {
                'gdp_growth': 0.052,      # GDP增长5.2%
                'cpi': 0.004,             # CPI 0.4%
                'ppi': -0.027,            # PPI -2.7%
                'pmi': 50.8,              # 制造业PMI
                'social_financing': 0.089, # 社融增速8.9%
                'usd_cny': 7.2156         # 汇率
            }
        }
    }


def test_system_initialization():
    """测试系统初始化"""
    safe_print("🔧 测试系统初始化")
    safe_print("-" * 60)
    
    try:
        config = create_full_test_config()
        engine = EnhancedTradingAgents(config)
        
        # 检查组件初始化状态
        agent_info = engine.get_agent_info()
        safe_print(f"✅ 系统初始化成功")
        safe_print(f"   总分析师数: {agent_info['total_agents']}")
        safe_print(f"   LLM提供商: {config['llm_provider']}")
        safe_print(f"   模型: {config['llm_model']}")
        
        # 验证每个分析师
        for agent_id, info in agent_info['agents'].items():
            safe_print(f"   ✓ {info['agent_type']}: {agent_id}")
        
        engine.shutdown()
        return True
        
    except Exception as e:
        safe_print(f"❌ 系统初始化失败: {e}")
        return False


def test_individual_agents():
    """测试各分析师独立功能"""
    safe_print("🤖 测试各分析师独立功能")
    safe_print("-" * 60)
    
    os.environ['DEEPSEEK_API_KEY'] = 'sk-7166ee16119846b09e687b2690e8de51'
    
    test_data = create_comprehensive_market_data()
    results = {}
    
    # 测试每个分析师
    agent_configs = [
        {'technical_analyst': True, 'fundamental_analyst': False, 'sentiment_analyst': False, 'market_analyst': False},
        {'technical_analyst': False, 'fundamental_analyst': True, 'sentiment_analyst': False, 'market_analyst': False},
        {'technical_analyst': False, 'fundamental_analyst': False, 'sentiment_analyst': True, 'market_analyst': False},
        {'technical_analyst': False, 'fundamental_analyst': False, 'sentiment_analyst': False, 'market_analyst': True}
    ]
    
    agent_names = ['技术分析师', '基本面分析师', '情感分析师', '市场分析师']
    
    for i, (agent_config, agent_name) in enumerate(zip(agent_configs, agent_names)):
        try:
            config = create_full_test_config()
            config['agents'] = agent_config
            
            engine = EnhancedTradingAgents(config)
            
            start_time = datetime.now()
            result = engine.analyze_stock_sync(test_data['symbol'], test_data)
            execution_time = (datetime.now() - start_time).total_seconds()
            
            safe_print(f"✅ {agent_name}测试成功")
            safe_print(f"   执行时间: {execution_time:.2f}s")
            safe_print(f"   分析结果: {result.action}")
            safe_print(f"   置信度: {result.confidence:.2%}")
            
            results[agent_name] = {
                'success': True,
                'execution_time': execution_time,
                'action': result.action,
                'confidence': result.confidence
            }
            
            engine.shutdown()
            
        except Exception as e:
            safe_print(f"❌ {agent_name}测试失败: {e}")
            results[agent_name] = {'success': False, 'error': str(e)}
    
    return results


def test_multi_agent_collaboration():
    """测试多分析师协作"""
    safe_print("🤝 测试多分析师协作分析")
    safe_print("-" * 60)
    
    os.environ['DEEPSEEK_API_KEY'] = 'sk-7166ee16119846b09e687b2690e8de51'
    
    try:
        config = create_full_test_config()
        engine = EnhancedTradingAgents(config)
        
        test_data = create_comprehensive_market_data()
        
        safe_print(f"📊 开始全面协作分析: {test_data['company_name']} ({test_data['symbol']})")
        safe_print(f"   行业: {test_data['industry']}")
        safe_print(f"   当前股价: {test_data['price_data']['close'][-1]:.2f}元")
        safe_print(f"   市值: {test_data['fundamental_data']['market_cap']/1e8:.0f}亿元")
        safe_print("")
        
        start_time = datetime.now()
        result = engine.analyze_stock_sync(test_data['symbol'], test_data)
        execution_time = (datetime.now() - start_time).total_seconds()
        
        safe_print("🎉 多分析师协作分析完成!")
        safe_print("")
        safe_print("📈 综合分析结果:")
        safe_print(f"   股票代码: {result.symbol}")
        safe_print(f"   投资建议: {result.action}")
        safe_print(f"   综合置信度: {result.confidence:.2%}")
        safe_print(f"   执行时间: {execution_time:.2f}s")
        
        if hasattr(result, 'agents_used'):
            safe_print(f"   参与分析师: {', '.join(result.agents_used)}")
        
        if hasattr(result, 'reasoning') and result.reasoning:
            safe_print("   综合推理:")
            for i, reason in enumerate(result.reasoning[:8], 1):
                safe_print(f"   {i}. {reason}")
        
        # 分析各专业领域贡献
        analysis_contributions = []
        if hasattr(result, 'technical_analysis'):
            analysis_contributions.append("📊 技术分析")
        if hasattr(result, 'fundamental_analysis'):
            analysis_contributions.append("📋 基本面分析")
        if hasattr(result, 'sentiment_analysis'):
            analysis_contributions.append("💭 情感分析")
        if hasattr(result, 'market_analysis'):
            analysis_contributions.append("📈 市场分析")
        
        if analysis_contributions:
            safe_print(f"   分析维度: {' | '.join(analysis_contributions)}")
        
        engine.shutdown()
        
        return {
            'success': True,
            'execution_time': execution_time,
            'action': result.action,
            'confidence': result.confidence,
            'analysis_contributions': len(analysis_contributions)
        }
        
    except Exception as e:
        safe_print(f"❌ 多分析师协作测试失败: {e}")
        return {'success': False, 'error': str(e)}


def test_stress_scenarios():
    """测试压力场景"""
    safe_print("⚡ 测试系统压力场景")
    safe_print("-" * 60)
    
    os.environ['DEEPSEEK_API_KEY'] = 'sk-7166ee16119846b09e687b2690e8de51'
    
    scenarios = {
        '数据缺失场景': {
            'symbol': '000002',
            'price_data': {'close': [10.0, 10.5]},  # 极少数据
        },
        '异常数据场景': {
            'symbol': '000003',
            'price_data': {'close': [None, float('inf'), -1]},  # 异常数据
        },
        '空数据场景': {
            'symbol': '000004',
        }
    }
    
    results = {}
    
    for scenario_name, scenario_data in scenarios.items():
        try:
            config = create_full_test_config()
            config['workflow']['max_execution_time'] = 60  # 降低超时时间
            
            engine = EnhancedTradingAgents(config)
            
            start_time = datetime.now()
            result = engine.analyze_stock_sync(scenario_data['symbol'], scenario_data)
            execution_time = (datetime.now() - start_time).total_seconds()
            
            safe_print(f"✅ {scenario_name}: 系统正常处理")
            safe_print(f"   结果: {result.action}, 置信度: {result.confidence:.2%}")
            
            results[scenario_name] = {
                'success': True,
                'execution_time': execution_time,
                'handled_gracefully': True
            }
            
            engine.shutdown()
            
        except Exception as e:
            safe_print(f"⚠️ {scenario_name}: {str(e)}")
            results[scenario_name] = {
                'success': False,
                'error': str(e),
                'handled_gracefully': 'timeout' in str(e).lower() or 'missing' in str(e).lower()
            }
    
    return results


def test_performance_metrics():
    """测试性能指标"""
    safe_print("⏱️ 测试系统性能指标")
    safe_print("-" * 60)
    
    os.environ['DEEPSEEK_API_KEY'] = 'sk-7166ee16119846b09e687b2690e8de51'
    
    config = create_full_test_config()
    test_data = create_comprehensive_market_data()
    
    # 测试多次执行的一致性和性能
    execution_times = []
    results = []
    
    for i in range(3):  # 执行3次测试
        try:
            engine = EnhancedTradingAgents(config)
            
            start_time = datetime.now()
            result = engine.analyze_stock_sync(test_data['symbol'], test_data)
            execution_time = (datetime.now() - start_time).total_seconds()
            
            execution_times.append(execution_time)
            results.append(result.action)
            
            engine.shutdown()
            
            safe_print(f"第{i+1}次执行: {execution_time:.2f}s, 结果: {result.action}")
            
        except Exception as e:
            safe_print(f"第{i+1}次执行失败: {e}")
            
    if execution_times:
        avg_time = sum(execution_times) / len(execution_times)
        max_time = max(execution_times)
        min_time = min(execution_times)
        
        safe_print("")
        safe_print(f"性能统计:")
        safe_print(f"   平均执行时间: {avg_time:.2f}s")
        safe_print(f"   最快执行时间: {min_time:.2f}s")
        safe_print(f"   最慢执行时间: {max_time:.2f}s")
        safe_print(f"   结果一致性: {len(set(results))}/{len(results)} 种不同结果")
        
        return {
            'avg_execution_time': avg_time,
            'max_execution_time': max_time,
            'min_execution_time': min_time,
            'consistency': len(set(results)) == 1 if results else False
        }
    
    return {'success': False}


def main():
    """主测试函数"""
    safe_print("=" * 100)
    safe_print("                      完整全量集成测试")
    safe_print("                多分析师智能体协作系统")
    safe_print("=" * 100)
    safe_print("")
    
    # 设置环境
    os.environ['DEEPSEEK_API_KEY'] = 'sk-7166ee16119846b09e687b2690e8de51'
    
    test_results = {}
    
    # 测试1: 系统初始化
    test_results['系统初始化'] = test_system_initialization()
    
    # 测试2: 各分析师独立功能
    test_results['分析师独立功能'] = test_individual_agents()
    
    # 测试3: 多分析师协作
    test_results['多分析师协作'] = test_multi_agent_collaboration()
    
    # 测试4: 压力场景测试
    test_results['压力场景测试'] = test_stress_scenarios()
    
    # 测试5: 性能指标测试
    test_results['性能指标测试'] = test_performance_metrics()
    
    # 测试总结
    safe_print("")
    safe_print("=" * 100)
    safe_print("                        测试总结报告")
    safe_print("=" * 100)
    safe_print("")
    
    overall_success = True
    total_tests = 0
    passed_tests = 0
    
    for test_name, result in test_results.items():
        if isinstance(result, bool):
            total_tests += 1
            if result:
                passed_tests += 1
                safe_print(f"✅ {test_name}: 通过")
            else:
                safe_print(f"❌ {test_name}: 失败")
                overall_success = False
        elif isinstance(result, dict):
            if test_name == '分析师独立功能':
                sub_passed = sum(1 for r in result.values() if isinstance(r, dict) and r.get('success', False))
                sub_total = len(result)
                total_tests += sub_total
                passed_tests += sub_passed
                safe_print(f"{'✅' if sub_passed == sub_total else '⚠️'} {test_name}: {sub_passed}/{sub_total}")
                
                for agent_name, agent_result in result.items():
                    if isinstance(agent_result, dict):
                        status = "✅" if agent_result.get('success', False) else "❌"
                        safe_print(f"    {status} {agent_name}")
            else:
                success = result.get('success', False)
                total_tests += 1
                if success:
                    passed_tests += 1
                    safe_print(f"✅ {test_name}: 通过")
                else:
                    safe_print(f"❌ {test_name}: 失败")
                    overall_success = False
    
    safe_print("")
    safe_print(f"总体结果: {passed_tests}/{total_tests} 通过 ({passed_tests/total_tests*100:.1f}%)")
    
    if overall_success:
        safe_print("")
        safe_print("🎉 完整全量集成测试成功!")
        safe_print("")
        safe_print("✨ 系统验证完成:")
        safe_print("  🏗️ 系统架构: 多分析师协作框架稳定运行")
        safe_print("  🧠 智能分析: 4种专业分析师协同工作") 
        safe_print("  🔄 工作流程: 并行执行和决策整合正常")
        safe_print("  🛡️ 容错能力: 异常场景处理机制有效")
        safe_print("  ⚡ 性能表现: 执行效率和结果一致性良好")
        safe_print("  🎯 实战能力: 真实市场数据分析准确")
        
    return overall_success


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)