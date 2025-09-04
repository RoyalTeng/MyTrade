"""
Agent协议与注册中心测试

验证新的统一Agent协议是否正确工作
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# 添加src到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mytrade.agents.protocols import (
    AgentRole, AgentOutput, AgentContext, AgentMetadata,
    DecisionAction, AgentDecision
)
from mytrade.agents.registry import AgentRegistry, AgentOrchestrator
from mytrade.agents.analysts.fundamental_analyst_v2 import FundamentalAnalyst


def test_agent_protocols():
    """测试Agent协议"""
    print("="*60)
    print("           Agent协议测试")
    print("="*60)
    
    try:
        # 1. 测试AgentOutput协议
        print("\n1. 测试AgentOutput协议...")
        
        # 创建基本面分析师实例
        analyst = FundamentalAnalyst({
            'focus_metrics': ['pe', 'pb', 'roe'],
            'analysis_depth': 'standard'
        })
        
        # 创建分析上下文
        context = AgentContext(
            symbol="000001",
            date="2025-09-04",
            market_data={
                "current_price": 11.50,
                "volume": 1000000
            }
        )
        
        # 执行分析
        result = analyst.run(context)
        
        print(f"[OK] Agent执行成功")
        print(f"   角色: {result.role}")
        print(f"   股票: {result.symbol}")
        print(f"   评分: {result.score}")
        print(f"   置信度: {result.confidence}")
        print(f"   推理: {result.rationale[:80]}...")
        
        # 2. 测试协议验证
        print("\n2. 测试协议验证...")
        
        # 验证输出符合协议
        assert isinstance(result, AgentOutput)
        assert result.role == AgentRole.FUNDAMENTAL.value  # 现在role是字符串值
        assert result.symbol == "000001"
        assert result.score is not None
        assert 0 <= result.confidence <= 1
        assert len(result.rationale) <= 300
        
        print("[OK] 协议验证通过")
        
        # 3. 测试JSON序列化
        print("\n3. 测试JSON序列化...")
        
        result_dict = result.model_dump(mode='json')  # 使用Pydantic的JSON模式
        result_json = json.dumps(result_dict, ensure_ascii=False, indent=2)
        
        print(f"[OK] JSON序列化成功")
        print(f"   JSON长度: {len(result_json)} 字符")
        print(f"   包含字段: {len(result_dict)} 个")
        
        # 4. 测试Agent注册中心
        print("\n4. 测试Agent注册中心...")
        
        registry = AgentRegistry()
        
        # 注册分析师
        registry.register_agent(AgentRole.FUNDAMENTAL, FundamentalAnalyst)
        
        # 获取注册的Agent
        registered_agent = registry.get_agent(AgentRole.FUNDAMENTAL)
        
        print(f"[OK] Agent注册成功")
        print(f"   注册角色: {AgentRole.FUNDAMENTAL.value}")
        print(f"   Agent类: {registered_agent.__class__.__name__}")
        
        # 5. 测试健康检查
        print("\n5. 测试健康检查...")
        
        health_status = analyst.health_check()
        
        print(f"[OK] 健康检查完成")
        print(f"   状态: {health_status['status']}")
        print(f"   版本: {health_status['version']}")
        
        # 6. 测试特征提取
        print("\n6. 测试特征提取...")
        
        features = result.features
        print(f"[OK] 提取到 {len(features)} 个特征")
        for key, value in list(features.items())[:5]:  # 显示前5个特征
            print(f"   {key}: {value}")
        
        # 7. 测试标签和告警
        print("\n7. 测试标签和告警...")
        
        print(f"[OK] 生成标签: {len(result.tags)} 个")
        print(f"   标签: {', '.join(result.tags)}")
        
        if result.alerts:
            print(f"[OK] 生成告警: {len(result.alerts)} 个")
            for alert in result.alerts:
                print(f"   告警: {alert}")
        else:
            print("[OK] 无告警信息")
        
        print("\n" + "="*60)
        print("Agent协议测试通过")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"[ERROR] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_decision_protocol():
    """测试决策协议 - 模拟Trader角色"""
    print("\n" + "="*60)
    print("           决策协议测试")
    print("="*60)
    
    try:
        # 创建模拟的交易员决策
        decision = AgentDecision(
            action=DecisionAction.BUY,
            weight=0.08,
            confidence=0.72,
            reasoning="基本面分析显示估值合理，ROE良好，建议适度建仓",
            risk_level="medium",
            expected_return=0.15,
            max_loss=0.05,
            time_horizon="3M"
        )
        
        # 创建带决策的Agent输出
        trader_output = AgentOutput(
            role=AgentRole.TRADER,
            timestamp=datetime.now(),
            symbol="000001",
            score=0.75,
            confidence=0.72,
            decision=decision,
            features={
                "signal_strength": 0.68,
                "market_timing": 0.75,
                "risk_reward_ratio": 3.0
            },
            rationale="综合分析显示买入信号强烈，风险可控",
            metadata=AgentMetadata(
                agent_id="trader_test",
                version="2.0.0"
            )
        )
        
        print(f"[OK] 交易员决策创建成功")
        print(f"   动作: {decision.action}")
        print(f"   权重: {decision.weight:.2%}")
        print(f"   置信度: {decision.confidence:.2%}")
        print(f"   预期收益: {decision.expected_return:.1%}")
        print(f"   最大损失: {decision.max_loss:.1%}")
        
        # 验证决策协议
        trader_output.validate_role_decision()
        print("[OK] 决策协议验证通过")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] 决策协议测试失败: {e}")
        return False


def test_registry_config_loading():
    """测试配置文件加载"""
    print("\n" + "="*60)
    print("           配置加载测试")
    print("="*60)
    
    try:
        registry = AgentRegistry()
        
        # 尝试加载配置文件
        config_path = Path(__file__).parent.parent / "configs" / "agents_config.yaml"
        
        if config_path.exists():
            registry.load_config(str(config_path))
            
            enabled_agents = registry.list_enabled_agents()
            print(f"[OK] 配置加载成功")
            print(f"   启用的Agent: {len(enabled_agents)} 个")
            for role in enabled_agents[:5]:  # 显示前5个
                print(f"   - {role.value}")
        else:
            print("[WARNING] 配置文件不存在，跳过测试")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] 配置加载测试失败: {e}")
        return False


def main():
    """运行所有测试"""
    print("开始Agent协议与注册中心测试...")
    
    tests = [
        ("基础协议测试", test_agent_protocols),
        ("决策协议测试", test_decision_protocol),
        ("配置加载测试", test_registry_config_loading)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n开始 {test_name}...")
        success = test_func()
        results.append((test_name, success))
    
    # 汇总结果
    print(f"\n" + "="*60)
    print("测试结果汇总")
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
        print(f"\n[SUCCESS] Agent协议系统工作正常！")
        return True
    else:
        print(f"\n[WARNING] 还有 {total - passed} 个测试需要修复")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)