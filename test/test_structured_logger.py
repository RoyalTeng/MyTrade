"""
测试结构化日志系统

验证JSON+Markdown双写功能：
- 不同日志级别的输出
- 智能体输出的结构化记录
- 流水线阶段的追踪
- 决策过程的记录
- 异步写入性能
"""

import unittest
import tempfile
import shutil
import json
import time
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from mytrade.logging.structured_logger import (
    DualFormatLogger, StructuredLogLevel, LogCategory,
    get_structured_logger, close_structured_logger,
    log_debug, log_info, log_analysis
)
from mytrade.agents.protocols import (
    AgentRole, AgentOutput, AgentDecision, DecisionAction, AgentMetadata
)


class TestStructuredLogger(unittest.TestCase):
    """测试结构化日志记录器"""
    
    def setUp(self):
        """设置测试环境"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.session_id = "test_session_001"
        
        self.logger = DualFormatLogger(
            log_dir=str(self.test_dir),
            session_id=self.session_id,
            enable_json=True,
            enable_markdown=True,
            enable_console=False,  # 测试时禁用控制台输出
            async_mode=False  # 同步模式便于测试验证
        )
    
    def tearDown(self):
        """清理测试环境"""
        self.logger.close()
        shutil.rmtree(self.test_dir)
        close_structured_logger()  # 清理全局实例
    
    def test_basic_logging(self):
        """测试基本日志记录功能"""
        # 记录不同级别的日志
        self.logger.log(
            level=StructuredLogLevel.INFO,
            category=LogCategory.SYSTEM,
            component="test_component",
            message="测试消息",
            data={"key": "value", "number": 42}
        )
        
        self.logger.log(
            level=StructuredLogLevel.WARNING,
            category=LogCategory.AGENT,
            component="agent_test",
            message="警告消息",
            data={"warning_type": "performance"}
        )
        
        # 验证JSON文件生成
        json_files = list(self.test_dir.glob(f"session_{self.session_id}_*.json"))
        self.assertEqual(len(json_files), 1)
        
        # 验证Markdown文件生成
        md_files = list(self.test_dir.glob(f"session_{self.session_id}_*.md"))
        self.assertEqual(len(md_files), 1)
        
        # 验证JSON内容
        with open(json_files[0], 'r', encoding='utf-8') as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 2)  # 两条日志
            
            # 解析第一条日志
            log_entry1 = json.loads(lines[0])
            self.assertEqual(log_entry1['level'], 'info')
            self.assertEqual(log_entry1['category'], 'system')
            self.assertEqual(log_entry1['component'], 'test_component')
            self.assertEqual(log_entry1['message'], '测试消息')
            self.assertEqual(log_entry1['data']['key'], 'value')
            self.assertEqual(log_entry1['data']['number'], 42)
            
        # 验证Markdown内容
        with open(md_files[0], 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('# TradingAgents 结构化日志', content)
            self.assertIn('INFO - test_component', content)
            self.assertIn('WARNING - agent_test', content)
            self.assertIn('测试消息', content)
            self.assertIn('警告消息', content)
    
    def test_agent_output_logging(self):
        """测试智能体输出记录"""
        # 创建模拟的智能体输出
        agent_output = AgentOutput(
            role=AgentRole.FUNDAMENTAL,
            timestamp=datetime.now(),
            symbol="000001.SZ",
            score=0.75,
            confidence=0.82,
            decision=AgentDecision(
                action=DecisionAction.BUY,
                weight=0.15,
                confidence=0.78,
                reasoning="基本面分析显示公司价值被低估",
                risk_level="medium",
                expected_return=0.12,
                max_loss=0.08
            ),
            features={
                "pe_ratio": 15.6,
                "pb_ratio": 1.8,
                "debt_ratio": 0.32
            },
            rationale="财务指标健康，业绩增长稳定",
            metadata=AgentMetadata(
                agent_id="fundamental_analyst_001",
                version="2.0.0",
                execution_time_ms=1250
            ),
            alerts=["关注行业政策风险"],
            tags=["value_stock", "defensive"]
        )
        
        # 记录智能体输出
        self.logger.log_agent_output(agent_output, "fundamental_analyst")
        
        # 验证JSON记录
        json_files = list(self.test_dir.glob(f"session_{self.session_id}_*.json"))
        with open(json_files[0], 'r', encoding='utf-8') as f:
            log_entry = json.loads(f.readline())
            
            self.assertEqual(log_entry['level'], 'analysis')
            self.assertEqual(log_entry['category'], 'agent')
            self.assertEqual(log_entry['component'], 'fundamental_analyst.fundamental')
            self.assertEqual(log_entry['data']['symbol'], '000001.SZ')
            self.assertEqual(log_entry['data']['score'], 0.75)
            self.assertEqual(log_entry['data']['confidence'], 0.82)
            self.assertEqual(log_entry['data']['decision']['action'], 'buy')
            self.assertEqual(log_entry['data']['features']['pe_ratio'], 15.6)
            self.assertIn('基本面分析显示公司价值被低估', log_entry['data']['decision']['reasoning'])
    
    def test_pipeline_stage_logging(self):
        """测试流水线阶段记录"""
        stage_results = {
            "analysts_count": 3,
            "success_rate": 0.67,
            "avg_confidence": 0.75,
            "consensus_score": 0.68
        }
        
        self.logger.log_pipeline_stage(
            stage="analysis",
            status="completed",
            results=stage_results,
            duration_ms=2150
        )
        
        # 验证日志记录
        json_files = list(self.test_dir.glob(f"session_{self.session_id}_*.json"))
        with open(json_files[0], 'r', encoding='utf-8') as f:
            log_entry = json.loads(f.readline())
            
            self.assertEqual(log_entry['level'], 'info')
            self.assertEqual(log_entry['category'], 'pipeline')
            self.assertEqual(log_entry['component'], 'orchestrator')
            self.assertEqual(log_entry['data']['stage'], 'analysis')
            self.assertEqual(log_entry['data']['status'], 'completed')
            self.assertEqual(log_entry['data']['duration_ms'], 2150)
            self.assertEqual(log_entry['data']['results']['consensus_score'], 0.68)
    
    def test_decision_logging(self):
        """测试决策记录"""
        decision = AgentDecision(
            action=DecisionAction.BUY,
            weight=0.12,
            confidence=0.85,
            reasoning="多项分析指标支持买入决策",
            risk_level="medium",
            expected_return=0.15,
            max_loss=0.06,
            time_horizon="3M"
        )
        
        self.logger.log_decision(
            decision=decision,
            context="综合分析后的最终交易决策",
            component="trading_engine"
        )
        
        # 验证决策日志
        json_files = list(self.test_dir.glob(f"session_{self.session_id}_*.json"))
        with open(json_files[0], 'r', encoding='utf-8') as f:
            log_entry = json.loads(f.readline())
            
            self.assertEqual(log_entry['level'], 'decision')
            self.assertEqual(log_entry['category'], 'trading')
            self.assertEqual(log_entry['component'], 'trading_engine')
            self.assertEqual(log_entry['data']['action'], 'buy')
            self.assertEqual(log_entry['data']['weight'], 0.12)
            self.assertEqual(log_entry['data']['confidence'], 0.85)
            self.assertEqual(log_entry['data']['time_horizon'], '3M')
    
    def test_error_logging(self):
        """测试错误记录"""
        try:
            # 故意制造异常
            raise ValueError("测试异常情况")
        except Exception as e:
            self.logger.log_error(
                component="test_component",
                error=e,
                context={"operation": "test_error_handling", "input_data": {"symbol": "000001"}}
            )
        
        # 验证错误日志
        json_files = list(self.test_dir.glob(f"session_{self.session_id}_*.json"))
        with open(json_files[0], 'r', encoding='utf-8') as f:
            log_entry = json.loads(f.readline())
            
            self.assertEqual(log_entry['level'], 'error')
            self.assertEqual(log_entry['category'], 'system')
            self.assertEqual(log_entry['component'], 'test_component')
            self.assertEqual(log_entry['data']['error_type'], 'ValueError')
            self.assertEqual(log_entry['data']['error_message'], '测试异常情况')
            self.assertIn('traceback', log_entry['data'])
            self.assertEqual(log_entry['data']['context']['operation'], 'test_error_handling')
    
    def test_performance_logging(self):
        """测试性能指标记录"""
        self.logger.log_performance(
            component="data_fetcher",
            metric="response_time",
            value=156.7,
            unit="ms",
            additional_data={
                "endpoint": "/api/stock/000001",
                "cache_hit": False,
                "data_size": 2048
            }
        )
        
        # 验证性能日志
        json_files = list(self.test_dir.glob(f"session_{self.session_id}_*.json"))
        with open(json_files[0], 'r', encoding='utf-8') as f:
            log_entry = json.loads(f.readline())
            
            self.assertEqual(log_entry['level'], 'info')
            self.assertEqual(log_entry['category'], 'performance')
            self.assertEqual(log_entry['component'], 'data_fetcher')
            self.assertEqual(log_entry['data']['metric'], 'response_time')
            self.assertEqual(log_entry['data']['value'], 156.7)
            self.assertEqual(log_entry['data']['unit'], 'ms')
            self.assertEqual(log_entry['data']['cache_hit'], False)
    
    def test_async_mode(self):
        """测试异步模式"""
        # 创建异步模式的日志记录器
        async_logger = DualFormatLogger(
            log_dir=str(self.test_dir / "async"),
            session_id="async_test",
            async_mode=True,
            enable_console=False
        )
        
        try:
            # 快速写入多条日志
            start_time = time.time()
            for i in range(100):
                async_logger.log(
                    level=StructuredLogLevel.INFO,
                    category=LogCategory.SYSTEM,
                    component="async_test",
                    message=f"异步日志消息 {i}",
                    data={"index": i, "batch": "performance_test"}
                )
            
            # 异步模式应该很快返回
            write_time = time.time() - start_time
            self.assertLess(write_time, 0.1)  # 应该在100ms内完成
            
            # 等待异步写入完成
            time.sleep(0.5)
            
            # 验证所有日志都被写入
            json_files = list((self.test_dir / "async").glob("session_async_test_*.json"))
            self.assertEqual(len(json_files), 1)
            
            with open(json_files[0], 'r', encoding='utf-8') as f:
                lines = f.readlines()
                self.assertEqual(len(lines), 100)
        
        finally:
            async_logger.close()
    
    def test_global_logger_functions(self):
        """测试全局日志记录函数"""
        # 测试便捷函数
        log_debug("test_component", "调试消息", {"debug_level": "verbose"})
        log_info("test_component", "信息消息", {"info_type": "status"})
        log_analysis("test_agent", "分析结果", {"confidence": 0.78})
        
        # 获取全局日志记录器验证
        global_logger = get_structured_logger()
        self.assertIsNotNone(global_logger)
        
        # 验证日志文件生成（全局记录器使用默认路径）
        default_log_dir = Path("logs/structured")
        if default_log_dir.exists():
            json_files = list(default_log_dir.glob("session_*.json"))
            self.assertGreater(len(json_files), 0)
    
    def test_markdown_format_quality(self):
        """测试Markdown格式质量"""
        # 记录复合日志条目
        self.logger.log(
            level=StructuredLogLevel.ANALYSIS,
            category=LogCategory.AGENT,
            component="technical_analyst",
            message="技术分析完成",
            data={
                "indicators": {
                    "sma_20": 15.67,
                    "sma_50": 14.89,
                    "rsi": 65.4,
                    "macd": 0.23
                },
                "signals": ["golden_cross", "breakout"],
                "trend": "bullish"
            },
            metadata={
                "model_version": "v2.1.0",
                "computation_time": 89.5
            }
        )
        
        # 验证Markdown格式
        md_files = list(self.test_dir.glob(f"session_{self.session_id}_*.md"))
        with open(md_files[0], 'r', encoding='utf-8') as f:
            content = f.read()
            
            # 验证标题和结构
            self.assertIn('# TradingAgents 结构化日志', content)
            self.assertIn('## 📊 ANALYSIS - technical_analyst', content)
            self.assertIn('**时间**:', content)
            self.assertIn('**类别**: `agent`', content)
            self.assertIn('**消息**: 技术分析完成', content)
            
            # 验证数据格式
            self.assertIn('**数据**:', content)
            self.assertIn('```json', content)
            self.assertIn('"sma_20": 15.67', content)
            self.assertIn('"signals": ["golden_cross", "breakout"]', content)
            
            # 验证元数据
            self.assertIn('**元数据**:', content)
            self.assertIn('"model_version": "v2.1.0"', content)
    
    def test_context_manager_usage(self):
        """测试上下文管理器用法"""
        test_log_dir = self.test_dir / "context_test"
        
        with DualFormatLogger(
            log_dir=str(test_log_dir),
            session_id="context_test",
            enable_console=False
        ) as logger:
            logger.log(
                level=StructuredLogLevel.INFO,
                category=LogCategory.SYSTEM,
                component="context_test",
                message="上下文管理器测试"
            )
        
        # 验证文件正常生成和关闭
        json_files = list(test_log_dir.glob("session_context_test_*.json"))
        md_files = list(test_log_dir.glob("session_context_test_*.md"))
        
        self.assertEqual(len(json_files), 1)
        self.assertEqual(len(md_files), 1)
        
        # 验证Markdown文件包含结束时间
        with open(md_files[0], 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('**结束时间**:', content)


class TestStructuredLoggerIntegration(unittest.TestCase):
    """测试结构化日志系统集成"""
    
    def test_agent_pipeline_logging_simulation(self):
        """模拟智能体流水线的完整日志记录"""
        test_dir = Path(tempfile.mkdtemp())
        
        try:
            with DualFormatLogger(
                log_dir=str(test_dir),
                session_id="pipeline_simulation",
                enable_console=False
            ) as logger:
                
                # 1. 流水线开始
                logger.log_pipeline_stage(
                    stage="initialization",
                    status="started",
                    results={"symbol": "000001.SZ", "context": "daily_analysis"}
                )
                
                # 2. 分析师阶段
                analyst_outputs = []
                for role in ["fundamental", "technical", "sentiment"]:
                    agent_output = AgentOutput(
                        role=getattr(AgentRole, role.upper()),
                        timestamp=datetime.now(),
                        symbol="000001.SZ",
                        score=0.6 + (hash(role) % 40) / 100,  # 模拟不同分数
                        confidence=0.7 + (hash(role) % 30) / 100,
                        features={f"{role}_score": 0.75, "data_quality": "high"},
                        rationale=f"{role}分析显示积极信号",
                        metadata=AgentMetadata(agent_id=f"{role}_agent_001")
                    )
                    analyst_outputs.append(agent_output)
                    logger.log_agent_output(agent_output, f"{role}_analyst")
                
                logger.log_pipeline_stage(
                    stage="analysis",
                    status="completed",
                    results={
                        "analysts_executed": len(analyst_outputs),
                        "avg_score": sum(o.score for o in analyst_outputs) / len(analyst_outputs),
                        "consensus": "bullish_lean"
                    },
                    duration_ms=1850
                )
                
                # 3. 交易决策
                final_decision = AgentDecision(
                    action=DecisionAction.BUY,
                    weight=0.08,
                    confidence=0.73,
                    reasoning="多数分析师看好，技术指标支持",
                    risk_level="medium",
                    expected_return=0.12,
                    max_loss=0.05
                )
                
                logger.log_decision(
                    decision=final_decision,
                    context="基于三维分析的综合决策",
                    component="decision_engine"
                )
                
                # 4. 性能统计
                logger.log_performance(
                    component="pipeline",
                    metric="total_execution_time",
                    value=3250,
                    unit="ms",
                    additional_data={
                        "stages_completed": 3,
                        "agents_executed": 3,
                        "decision_confidence": final_decision.confidence
                    }
                )
            
            # 验证完整的日志记录
            json_files = list(test_dir.glob("session_pipeline_simulation_*.json"))
            self.assertEqual(len(json_files), 1)
            
            with open(json_files[0], 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # 应该有：1个初始化 + 3个分析师 + 1个阶段完成 + 1个决策 + 1个性能 = 7条日志
                self.assertEqual(len(lines), 7)
                
                # 验证日志类型分布
                log_levels = [json.loads(line)['level'] for line in lines]
                self.assertIn('info', log_levels)  # 流水线和性能日志
                self.assertIn('analysis', log_levels)  # 智能体分析日志  
                self.assertIn('decision', log_levels)  # 决策日志
            
            # 验证Markdown格式的可读性
            md_files = list(test_dir.glob("session_pipeline_simulation_*.md"))
            with open(md_files[0], 'r', encoding='utf-8') as f:
                content = f.read()
                
                # 验证包含所有关键组件
                self.assertIn('fundamental_analyst.fundamental', content)
                self.assertIn('technical_analyst.technical', content)
                self.assertIn('sentiment_analyst.sentiment', content)
                self.assertIn('decision_engine', content)
                self.assertIn('orchestrator', content)
                
                # 验证决策信息的记录
                self.assertIn('交易决策: buy', content)
                self.assertIn('基于三维分析的综合决策', content)
        
        finally:
            shutil.rmtree(test_dir)


if __name__ == '__main__':
    unittest.main()