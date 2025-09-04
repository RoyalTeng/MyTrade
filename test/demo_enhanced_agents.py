#!/usr/bin/env python3
"""
增强智能体引擎演示脚本

展示优化后的TradingAgents引擎功能，包括：
- DeepSeek API集成
- 多智能体协作
- 结构化分析输出
- 中文本地化
"""

import sys
import os
import asyncio
import json
from pathlib import Path
from datetime import datetime

# 添加src到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# 导入编码修复工具
from test_encoding_fix import safe_print

# 导入增强的智能体引擎
from mytrade.agents import EnhancedTradingAgents


def create_demo_config():
    """创建演示配置"""
    return {
        # LLM配置 - 使用DeepSeek
        'llm_provider': 'deepseek',
        'llm_model': 'deepseek-chat',
        'llm_temperature': 0.3,
        'llm_max_tokens': 3000,
        
        # Agent配置
        'agents': {
            'technical_analyst': True,
            'fundamental_analyst': False,  # 暂未实现
            'sentiment_analyst': False,    # 暂未实现
            'market_analyst': False        # 暂未实现
        },
        
        # 工作流配置
        'workflow': {
            'enable_parallel': True,
            'enable_debate': False,  # 简化演示
            'max_execution_time': 120
        },
        
        # 日志配置
        'logging': {
            'level': 'INFO',
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        }
    }


def create_demo_market_data():
    """创建演示市场数据"""
    return {
        'symbol': '000001',
        'timestamp': datetime.now(),
        'price_data': {
            'close': [15.20, 15.45, 15.30, 15.60, 15.80, 15.75, 16.00, 15.95, 16.20, 16.10],
            'high': [15.50, 15.70, 15.55, 15.90, 16.00, 15.95, 16.25, 16.15, 16.40, 16.30],
            'low': [15.00, 15.30, 15.10, 15.40, 15.60, 15.55, 15.80, 15.75, 15.95, 15.90],
            'volume': [1500000, 1800000, 1200000, 2100000, 2500000, 1900000, 2800000, 2200000, 3000000, 2600000],
            'open': [15.10, 15.40, 15.25, 15.50, 15.70, 15.65, 15.90, 15.85, 16.10, 16.05]
        },
        'volume_data': {
            'volume': [1500000, 1800000, 1200000, 2100000, 2500000, 1900000, 2800000, 2200000, 3000000, 2600000],
            'turnover': [22800000, 27810000, 18360000, 32760000, 39500000, 29925000, 44800000, 35090000, 48600000, 41860000]
        },
        'fundamental_data': {
            'pe_ratio': 12.5,
            'pb_ratio': 1.8,
            'roe': 0.15,
            'debt_ratio': 0.35,
            'revenue_growth': 0.08
        }
    }


class DemoRunner:
    """演示运行器"""
    
    def __init__(self):
        self.agents_engine = None
    
    def setup(self):
        """初始化演示环境"""
        safe_print("="*80)
        safe_print("           增强智能体引擎优化演示")
        safe_print("="*80)
        safe_print("")
        
        # 设置DeepSeek API密钥
        os.environ['DEEPSEEK_API_KEY'] = 'sk-7166ee16119846b09e687b2690e8de51'
        
        # 创建配置
        config = create_demo_config()
        safe_print("📋 演示配置:")
        safe_print(f"  LLM提供商: {config['llm_provider']}")
        safe_print(f"  LLM模型: {config['llm_model']}")
        safe_print(f"  启用的Agent: {[k for k, v in config['agents'].items() if v]}")
        safe_print("")
        
        # 初始化引擎
        try:
            safe_print("🚀 正在初始化增强智能体引擎...")
            self.agents_engine = EnhancedTradingAgents(config)
            safe_print("✅ 引擎初始化成功!")
            safe_print("")
        except Exception as e:
            safe_print(f"❌ 引擎初始化失败: {e}")
            return False
        
        return True
    
    def demonstrate_health_check(self):
        """演示健康检查功能"""
        safe_print("🏥 健康检查演示")
        safe_print("-" * 60)
        
        try:
            health_status = self.agents_engine.health_check()
            safe_print("健康检查结果:")
            safe_print(f"  📊 Agent数量: {health_status['agents_count']}")
            safe_print(f"  🔗 LLM适配器状态: {'正常' if health_status.get('llm_adapter') else '异常'}")
            safe_print(f"  ⏰ 检查时间: {health_status['timestamp']}")
            
            if 'agents_status' in health_status:
                safe_print("  🤖 Agent状态详情:")
                for agent_id, status in health_status['agents_status'].items():
                    status_text = "✅ 正常" if status.get('healthy') else "❌ 异常"
                    safe_print(f"    {agent_id}: {status_text} ({status.get('agent_type', 'Unknown')})")
            
            safe_print("")
            
        except Exception as e:
            safe_print(f"❌ 健康检查失败: {e}")
            safe_print("")
    
    def demonstrate_agent_info(self):
        """演示Agent信息获取"""
        safe_print("📋 Agent信息演示")
        safe_print("-" * 60)
        
        try:
            agent_info = self.agents_engine.get_agent_info()
            safe_print(f"Agent信息概览:")
            safe_print(f"  总Agent数: {agent_info['total_agents']}")
            safe_print("")
            
            if agent_info.get('agents'):
                safe_print("  详细信息:")
                for agent_id, info in agent_info['agents'].items():
                    safe_print(f"  🤖 {agent_id}:")
                    safe_print(f"    类型: {info.get('agent_type', 'Unknown')}")
                    safe_print(f"    角色: {info.get('role_description', 'No description')}")
                    safe_print(f"    所需输入: {info.get('required_inputs', [])}")
                    safe_print("")
            
        except Exception as e:
            safe_print(f"❌ Agent信息获取失败: {e}")
            safe_print("")
    
    def demonstrate_stock_analysis(self):
        """演示股票分析功能"""
        safe_print("📈 股票分析功能演示")
        safe_print("-" * 60)
        
        # 准备演示数据
        market_data = create_demo_market_data()
        symbol = market_data['symbol']
        
        safe_print(f"分析目标: {symbol} (平安银行)")
        safe_print(f"数据时间: {market_data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
        safe_print(f"最新价格: {market_data['price_data']['close'][-1]}")
        safe_print(f"价格区间: {min(market_data['price_data']['low'])} - {max(market_data['price_data']['high'])}")
        safe_print("")
        
        try:
            safe_print("🔍 开始智能体分析...")
            start_time = datetime.now()
            
            # 执行分析（使用同步版本以简化演示）
            result = self.agents_engine.analyze_stock_sync(symbol, market_data)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            safe_print("✅ 分析完成!")
            safe_print("")
            
            # 展示分析结果
            safe_print("📊 分析结果:")
            safe_print(f"  工作流ID: {result.workflow_id}")
            safe_print(f"  股票代码: {result.symbol}")
            safe_print(f"  建议操作: {result.action}")
            safe_print(f"  置信度: {result.confidence:.2%}")
            safe_print(f"  执行时间: {execution_time:.2f}s")
            safe_print("")
            
            if hasattr(result, 'reasoning') and result.reasoning:
                safe_print("🧠 分析推理:")
                for i, reason in enumerate(result.reasoning[:3], 1):  # 显示前3个推理
                    safe_print(f"  {i}. {reason}")
                safe_print("")
            
            if hasattr(result, 'agents_used') and result.agents_used:
                safe_print(f"👥 参与分析的Agent: {', '.join(result.agents_used)}")
                safe_print("")
            
            # 展示技术分析详情（如果有）
            if hasattr(result, 'technical_analysis') and result.technical_analysis:
                safe_print("📊 技术分析详情:")
                tech_data = result.technical_analysis
                if 'indicators' in tech_data:
                    indicators = tech_data['indicators']
                    safe_print(f"  SMA_5: {indicators.get('SMA_5', 'N/A')}")
                    safe_print(f"  SMA_20: {indicators.get('SMA_20', 'N/A')}")
                    safe_print(f"  RSI: {indicators.get('RSI', 'N/A')}")
                    safe_print(f"  MACD: {indicators.get('MACD', 'N/A')}")
                safe_print("")
                
        except Exception as e:
            safe_print(f"❌ 股票分析失败: {e}")
            safe_print("")
    
    async def demonstrate_async_analysis(self):
        """演示异步分析功能"""
        safe_print("⚡ 异步分析功能演示")
        safe_print("-" * 60)
        
        symbols = ['000001', '000002', '600519']
        safe_print(f"并行分析股票: {', '.join(symbols)}")
        safe_print("")
        
        try:
            tasks = []
            market_data = create_demo_market_data()
            
            for symbol in symbols:
                # 为每个股票创建略微不同的数据
                symbol_data = market_data.copy()
                symbol_data['symbol'] = symbol
                
                task = self.agents_engine.analyze_stock(symbol, symbol_data)
                tasks.append(task)
            
            safe_print("🔍 开始并行分析...")
            start_time = datetime.now()
            
            # 等待所有分析完成
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            safe_print(f"✅ 并行分析完成! 总耗时: {execution_time:.2f}s")
            safe_print("")
            
            # 展示结果概览
            safe_print("📊 并行分析结果概览:")
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    safe_print(f"  {symbols[i]}: ❌ 分析失败 - {result}")
                else:
                    safe_print(f"  {symbols[i]}: {result.action} (置信度: {result.confidence:.1%})")
            safe_print("")
            
        except Exception as e:
            safe_print(f"❌ 异步分析失败: {e}")
            safe_print("")
    
    def demonstrate_provider_support(self):
        """演示LLM提供商支持"""
        safe_print("🔌 LLM提供商支持演示")
        safe_print("-" * 60)
        
        try:
            providers = self.agents_engine.get_supported_llm_providers()
            safe_print("支持的LLM提供商:")
            for i, provider in enumerate(providers, 1):
                status = "🟢" if provider == 'deepseek' else "🟡"
                note = " (当前使用)" if provider == 'deepseek' else ""
                safe_print(f"  {i}. {status} {provider}{note}")
            
            safe_print("")
            safe_print("💡 提示: 可通过配置轻松切换不同的LLM提供商")
            safe_print("")
            
        except Exception as e:
            safe_print(f"❌ 提供商信息获取失败: {e}")
            safe_print("")
    
    def run_demo(self):
        """运行完整演示"""
        if not self.setup():
            return False
        
        try:
            # 1. 健康检查演示
            self.demonstrate_health_check()
            
            # 2. Agent信息演示
            self.demonstrate_agent_info()
            
            # 3. LLM提供商支持演示
            self.demonstrate_provider_support()
            
            # 4. 股票分析演示
            self.demonstrate_stock_analysis()
            
            # 5. 异步分析演示
            safe_print("⚡ 准备异步分析演示...")
            asyncio.run(self.demonstrate_async_analysis())
            
            # 演示总结
            safe_print("=" * 80)
            safe_print("                  演示总结")
            safe_print("=" * 80)
            safe_print("")
            safe_print("🎉 增强智能体引擎演示完成!")
            safe_print("")
            safe_print("✨ 主要优化亮点:")
            safe_print("  • 🤖 集成DeepSeek API，提供强大的AI分析能力")
            safe_print("  • 🏗️ 模块化架构，支持多种LLM提供商")
            safe_print("  • ⚡ 异步执行支持，提升分析效率")
            safe_print("  • 🧠 多智能体协作，提供全面的投资分析")
            safe_print("  • 🔧 灵活配置，易于扩展新的分析师类型")
            safe_print("  • 🌐 中文本地化，针对A股市场优化")
            safe_print("  • 📊 结构化输出，便于后续处理和展示")
            safe_print("")
            safe_print("📈 适用场景:")
            safe_print("  • 量化交易系统的智能分析模块")
            safe_print("  • 投资顾问AI助手")
            safe_print("  • 金融数据分析平台")
            safe_print("  • 交易决策支持系统")
            safe_print("")
            
            return True
            
        except KeyboardInterrupt:
            safe_print("\\n⚠️ 演示被用户中断")
            return False
        except Exception as e:
            safe_print(f"\\n❌ 演示执行出错: {e}")
            return False
        finally:
            # 清理资源
            if self.agents_engine:
                try:
                    self.agents_engine.shutdown()
                    safe_print("🧹 资源清理完成")
                except:
                    pass


def main():
    """主演示函数"""
    demo = DemoRunner()
    success = demo.run_demo()
    return success


if __name__ == "__main__":
    # 运行演示
    success = main()
    exit(0 if success else 1)