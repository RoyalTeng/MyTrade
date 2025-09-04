"""
智能体编排引擎与完整流水线测试

测试TradingAgents企业级架构的完整决策流程：
分析师→研究员→交易员→风险管理→基金经理
"""

import sys
from pathlib import Path
from datetime import datetime
from decimal import Decimal

# 添加src到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mytrade.agents.protocols import (
    AgentRole, AgentOutput, AgentContext, AgentMetadata,
    DecisionAction, AgentDecision
)
from mytrade.agents.registry import AgentRegistry
from mytrade.agents.orchestrator import AgentOrchestrator, PipelineStage
from mytrade.agents.analysts.fundamental_analyst_v2 import FundamentalAnalyst
from mytrade.agents.researchers.bull_researcher import BullResearcher
from mytrade.agents.researchers.bear_researcher import BearResearcher
from mytrade.agents.risk_managers.aggressive_risk_manager import AggressiveRiskManager
from mytrade.agents.risk_managers.neutral_risk_manager import NeutralRiskManager
from mytrade.agents.risk_managers.conservative_risk_manager import ConservativeRiskManager


def test_agent_registration():
    """测试Agent注册"""
    print("="*60)
    print("           Agent注册测试")
    print("="*60)
    
    try:
        registry = AgentRegistry()
        
        # 注册各类Agent
        registry.register_agent(AgentRole.FUNDAMENTAL, FundamentalAnalyst)
        registry.register_agent(AgentRole.BULL, BullResearcher)
        registry.register_agent(AgentRole.BEAR, BearResearcher)
        registry.register_agent(AgentRole.RISK_SEEKING, AggressiveRiskManager)
        registry.register_agent(AgentRole.RISK_NEUTRAL, NeutralRiskManager)
        registry.register_agent(AgentRole.RISK_CONSERVATIVE, ConservativeRiskManager)
        
        print(f"[OK] Agent注册成功")
        
        # 测试Agent获取
        fundamental = registry.get_agent(AgentRole.FUNDAMENTAL)
        bull = registry.get_agent(AgentRole.BULL)
        
        print(f"   基本面分析师: {fundamental.__class__.__name__}")
        print(f"   多头研究员: {bull.__class__.__name__}")
        
        # 测试配置加载
        enabled_agents = registry.list_enabled_agents()
        print(f"   启用的Agent: {len(enabled_agents)} 个")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Agent注册测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_single_agent_execution():
    """测试单个Agent执行"""
    print("\n" + "="*60)
    print("           单Agent执行测试")
    print("="*60)
    
    try:
        # 创建执行上下文
        context = AgentContext(
            symbol="000001",
            date="2025-09-04",
            market_data={
                "current_price": 11.80,
                "volume": 1200000
            }
        )
        
        # 测试基本面分析师
        print("\n1. 测试基本面分析师...")
        fundamental = FundamentalAnalyst({
            'focus_metrics': ['pe', 'pb', 'roe'],
            'analysis_depth': 'standard'
        })
        
        result = fundamental.run(context)
        
        print(f"[OK] 基本面分析完成")
        print(f"   评分: {result.score}")
        print(f"   置信度: {result.confidence}")
        print(f"   推理: {result.rationale[:50]}...")
        
        # 测试研究员（需要分析师输出作为输入）
        print("\n2. 测试多头研究员...")
        context.previous_outputs = [result]
        
        bull = BullResearcher({
            'stance': 'optimistic',
            'debate_style': 'aggressive'
        })
        
        bull_result = bull.run(context)
        
        print(f"[OK] 多头研究完成")
        print(f"   评分: {bull_result.score}")
        print(f"   置信度: {bull_result.confidence}")
        print(f"   论据: {bull_result.rationale[:50]}...")
        
        # 测试空头研究员
        print("\n3. 测试空头研究员...")
        bear = BearResearcher({
            'stance': 'pessimistic',
            'debate_style': 'conservative'
        })
        
        bear_result = bear.run(context)
        
        print(f"[OK] 空头研究完成")
        print(f"   评分: {bear_result.score}")
        print(f"   置信度: {bear_result.confidence}")
        print(f"   论据: {bear_result.rationale[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] 单Agent执行测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_risk_management_trio():
    """测试三视角风险管理"""
    print("\n" + "="*60)
    print("           三视角风险管理测试")
    print("="*60)
    
    try:
        # 创建模拟交易员决策
        trader_decision = AgentOutput(
            role=AgentRole.TRADER,
            timestamp=datetime.now(),
            symbol="000001",
            score=0.75,
            confidence=0.8,
            decision=AgentDecision(
                action=DecisionAction.BUY,
                weight=0.1,
                confidence=0.8,
                reasoning="综合分析显示买入机会",
                risk_level="medium",
                expected_return=0.15,
                max_loss=0.08,
                time_horizon="3M"
            ),
            features={"signal_strength": 0.75},
            rationale="基于多因子分析的买入信号",
            metadata=AgentMetadata(
                agent_id="trader_test",
                version="2.0.0"
            )
        )
        
        context = AgentContext(
            symbol="000001",
            date="2025-09-04",
            previous_outputs=[trader_decision]
        )
        
        # 测试激进风险管理
        print("\n1. 测试激进风险管理...")
        aggressive_rm = AggressiveRiskManager({
            'risk_appetite': 'high',
            'max_drawdown': 0.15,
            'leverage_tolerance': 2.0
        })
        
        aggressive_result = aggressive_rm.run(context)
        
        print(f"[OK] 激进风险管理完成")
        print(f"   评分: {aggressive_result.score}")
        print(f"   建议动作: {aggressive_result.decision.action}")
        print(f"   建议仓位: {aggressive_result.decision.weight:.2%}")
        print(f"   推理: {aggressive_result.rationale[:50]}...")
        
        # 测试中性风险管理
        print("\n2. 测试中性风险管理...")
        neutral_rm = NeutralRiskManager({
            'risk_appetite': 'medium',
            'max_drawdown': 0.10,
            'target_sharpe': 1.0
        })
        
        neutral_result = neutral_rm.run(context)
        
        print(f"[OK] 中性风险管理完成")
        print(f"   评分: {neutral_result.score}")
        print(f"   建议动作: {neutral_result.decision.action}")
        print(f"   建议仓位: {neutral_result.decision.weight:.2%}")
        
        # 测试保守风险管理
        print("\n3. 测试保守风险管理...")
        conservative_rm = ConservativeRiskManager({
            'risk_appetite': 'low',
            'max_drawdown': 0.05,
            'min_confidence': 0.8
        })
        
        conservative_result = conservative_rm.run(context)
        
        print(f"[OK] 保守风险管理完成")
        print(f"   评分: {conservative_result.score}")
        print(f"   建议动作: {conservative_result.decision.action}")
        print(f"   建议仓位: {conservative_result.decision.weight:.2%}")
        
        # 对比三个风险管理的建议
        print(f"\n风险管理对比:")
        print(f"   激进: {aggressive_result.decision.weight:.2%} 仓位")
        print(f"   中性: {neutral_result.decision.weight:.2%} 仓位")
        print(f"   保守: {conservative_result.decision.weight:.2%} 仓位")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] 三视角风险管理测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_orchestrator_pipeline():
    """测试编排引擎完整流水线"""
    print("\n" + "="*60)
    print("           编排引擎流水线测试")
    print("="*60)
    
    try:
        # 创建注册中心和编排引擎
        registry = AgentRegistry()
        orchestrator = AgentOrchestrator(registry)
        
        # 注册必要的Agent
        registry.register_agent(AgentRole.FUNDAMENTAL, FundamentalAnalyst)
        registry.register_agent(AgentRole.BULL, BullResearcher)
        registry.register_agent(AgentRole.BEAR, BearResearcher)
        registry.register_agent(AgentRole.RISK_SEEKING, AggressiveRiskManager)
        registry.register_agent(AgentRole.RISK_NEUTRAL, NeutralRiskManager)
        registry.register_agent(AgentRole.RISK_CONSERVATIVE, ConservativeRiskManager)
        
        # 创建执行上下文
        context = AgentContext(
            symbol="000001",
            date="2025-09-04",
            market_data={
                "current_price": 11.80,
                "volume": 1200000
            },
            market_condition="neutral"
        )
        
        print(f"[OK] 开始执行完整决策流水线")
        print(f"   股票: {context.symbol}")
        print(f"   日期: {context.date}")
        
        # 执行分析师阶段
        print(f"\n执行阶段 1: 分析师并行分析")
        analysis_result = orchestrator._execute_analysis_stage(context)
        
        print(f"[OK] 分析师阶段完成")
        print(f"   成功: {analysis_result.success}")
        print(f"   输出数量: {len(analysis_result.outputs)}")
        print(f"   执行时间: {analysis_result.execution_time_ms:.1f}ms")
        
        if analysis_result.outputs:
            for role, output in analysis_result.outputs.items():
                print(f"   {role.value}: {output.score:.3f}")
        
        # 执行研究员阶段
        print(f"\n执行阶段 2: 研究员辩论")
        context.previous_outputs = list(analysis_result.outputs.values())
        research_result = orchestrator._execute_research_stage(context)
        
        print(f"[OK] 研究员阶段完成")
        print(f"   成功: {research_result.success}")
        print(f"   执行时间: {research_result.execution_time_ms:.1f}ms")
        
        if research_result.outputs:
            for role, output in research_result.outputs.items():
                print(f"   辩论结果: {output.score:.3f}")
                debate_features = output.features
                print(f"   辩论轮数: {debate_features.get('debate_rounds', 0)}")
                print(f"   最终立场: {debate_features.get('final_stance', 'unknown')}")
        
        # 执行风险管理阶段
        print(f"\n执行阶段 3: 多视角风险管理")
        # 添加模拟交易员决策
        mock_trader_output = AgentOutput(
            role=AgentRole.TRADER,
            timestamp=datetime.now(),
            symbol=context.symbol,
            score=0.72,
            confidence=0.78,
            decision=AgentDecision(
                action=DecisionAction.BUY,
                weight=0.08,
                confidence=0.78,
                reasoning="综合信号显示买入机会",
                risk_level="medium",
                expected_return=0.12,
                max_loss=0.06
            ),
            features={},
            rationale="模拟交易员决策",
            metadata=AgentMetadata(agent_id="mock_trader", version="1.0.0")
        )
        
        context.previous_outputs.append(mock_trader_output)
        risk_result = orchestrator._execute_risk_management_stage(context)
        
        print(f"[OK] 风险管理阶段完成")
        print(f"   成功: {risk_result.success}")
        print(f"   风险视角数量: {len(risk_result.outputs)}")
        
        if risk_result.outputs:
            for role, output in risk_result.outputs.items():
                decision = output.decision
                print(f"   {role.value}: {decision.action.value} {decision.weight:.2%}")
        
        # 获取执行统计
        print(f"\n执行统计:")
        stats = orchestrator.get_execution_statistics()
        print(f"   总流水线数: {stats['total_pipelines']}")
        print(f"   成功率: {stats['success_rate']:.1%}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] 编排引擎流水线测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_debate_mechanism():
    """测试辩论机制"""
    print("\n" + "="*60)
    print("           辩论机制测试")
    print("="*60)
    
    try:
        # 创建基础分析结果（作为辩论输入）
        fundamental_result = AgentOutput(
            role=AgentRole.FUNDAMENTAL,
            timestamp=datetime.now(),
            symbol="000001",
            score=0.65,
            confidence=0.75,
            features={
                'pe_ratio': 15.2,
                'roe': 0.12,
                'growth_rate': 0.08
            },
            rationale="基本面数据显示一定优势",
            metadata=AgentMetadata(agent_id="fundamental", version="2.0.0")
        )
        
        context = AgentContext(
            symbol="000001",
            date="2025-09-04",
            previous_outputs=[fundamental_result]
        )
        
        print(f"[OK] 开始Bull vs Bear辩论")
        
        # Bull研究员分析
        bull = BullResearcher()
        bull_result = bull.run(context)
        
        print(f"[OK] Bull研究员观点:")
        print(f"   评分: {bull_result.score:.3f}")
        print(f"   置信度: {bull_result.confidence:.3f}")
        print(f"   论据: {bull_result.rationale}")
        
        # Bear研究员分析
        bear = BearResearcher()
        bear_result = bear.run(context)
        
        print(f"[OK] Bear研究员观点:")
        print(f"   评分: {bear_result.score:.3f}")
        print(f"   置信度: {bear_result.confidence:.3f}")
        print(f"   论据: {bear_result.rationale}")
        
        # 分歧度分析
        score_diff = abs(bull_result.score - bear_result.score)
        print(f"\n[OK] 辩论分析:")
        print(f"   观点分歧: {score_diff:.3f}")
        print(f"   分歧程度: {'高' if score_diff > 0.3 else '中' if score_diff > 0.1 else '低'}")
        
        if score_diff > 0.1:
            print(f"   需要进一步辩论轮次")
        else:
            print(f"   观点基本一致，可达成共识")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] 辩论机制测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("开始P1完整功能测试...")
    
    tests = [
        ("Agent注册测试", test_agent_registration),
        ("单Agent执行测试", test_single_agent_execution),
        ("三视角风险管理测试", test_risk_management_trio),
        ("编排引擎流水线测试", test_orchestrator_pipeline),
        ("辩论机制测试", test_debate_mechanism),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n开始 {test_name}...")
        success = test_func()
        results.append((test_name, success))
    
    # 汇总结果
    print(f"\n" + "="*60)
    print("P1功能测试结果汇总")
    print("="*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"总测试数: {total}")
    print(f"通过测试: {passed}")
    print(f"失败测试: {total - passed}")
    
    for test_name, success in results:
        status = "[PASS]" if success else "[FAIL]"
        print(f"  {test_name}: {status}")
    
    if passed == total:
        print(f"\n[SUCCESS] P1功能系统工作正常！")
        print("TradingAgents企业级架构实现完成：")
        print("✅ Agent注册中心与编排系统")
        print("✅ Bull/Bear研究员辩论机制")
        print("✅ 三视角风险管理体系")
        return True
    else:
        print(f"\n[WARNING] 还有 {total - passed} 个测试需要修复")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)