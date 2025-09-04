"""
增强的TradingAgents核心引擎

集成优化的多智能体交易决策系统
参考TradingAgents架构，融合中文本地化和MyTrade系统
"""

import os
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
import asyncio

from .llm_adapters import LLMAdapterFactory, LLMConfig
from .base_agent import BaseAgent
from .analysts import TechnicalAnalyst, FundamentalAnalyst, SentimentAnalyst, MarketAnalyst
from .workflow import TradingWorkflow, WorkflowResult


class EnhancedTradingAgents:
    """增强的交易智能体引擎"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """初始化智能体引擎
        
        Args:
            config: 引擎配置
        """
        self.config = config or self._get_default_config()
        self.llm_adapter = None
        self.workflow = None
        self.agents: Dict[str, BaseAgent] = {}
        
        # 设置日志
        self.logger = logging.getLogger("agents.core")
        self._setup_logging()
        
        # 初始化组件
        self._initialize_llm_adapter()
        self._initialize_workflow()
        self._initialize_agents()
        
        self.logger.info("增强的TradingAgents引擎初始化完成")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            # LLM配置 - 默认使用DeepSeek
            'llm_provider': 'deepseek',
            'llm_model': 'deepseek-chat',
            'llm_temperature': 0.3,
            'llm_max_tokens': 2000,
            
            # Agent配置
            'agents': {
                'technical_analyst': True,
                'fundamental_analyst': True,   # 基本面分析师
                'sentiment_analyst': True,     # 情感分析师
                'market_analyst': True         # 市场分析师
            },
            
            # 工作流配置
            'workflow': {
                'enable_parallel': True,
                'enable_debate': False,  # 暂时禁用辩论功能
                'max_execution_time': 300
            },
            
            # 日志配置
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            }
        }
    
    def _setup_logging(self):
        """设置日志"""
        log_config = self.config.get('logging', {})
        level = log_config.get('level', 'INFO')
        format_str = log_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # 配置根日志记录器
        logging.basicConfig(
            level=getattr(logging, level),
            format=format_str,
            handlers=[logging.StreamHandler()]
        )
    
    def _initialize_llm_adapter(self):
        """初始化LLM适配器"""
        try:
            self.llm_adapter = LLMAdapterFactory.create_adapter(
                provider=self.config['llm_provider'],
                model=self.config['llm_model'],
                temperature=self.config['llm_temperature'],
                max_tokens=self.config.get('llm_max_tokens', 2000),  # 使用get方法设置默认值
                api_key='sk-7166ee16119846b09e687b2690e8de51'  # 直接设置DeepSeek API密钥
            )
            self.logger.info(f"LLM适配器初始化成功: {self.config['llm_provider']} - {self.config['llm_model']}")
            
        except Exception as e:
            self.logger.error(f"LLM适配器初始化失败: {e}")
            raise
    
    def _initialize_workflow(self):
        """初始化工作流"""
        workflow_config = self.config.get('workflow', {})
        self.workflow = TradingWorkflow(workflow_config)
        self.logger.info("工作流初始化成功")
    
    def _initialize_agents(self):
        """初始化所有Agent"""
        agents_config = self.config.get('agents', {})
        
        # 初始化技术分析师
        if agents_config.get('technical_analyst', True):
            technical_analyst = TechnicalAnalyst(
                agent_id='technical_analyst_001',
                llm_adapter=self.llm_adapter,
                config=self.config
            )
            self.agents['technical_analyst'] = technical_analyst
            self.workflow.register_agent(technical_analyst)
        
        # 初始化基本面分析师
        if agents_config.get('fundamental_analyst', False):
            fundamental_analyst = FundamentalAnalyst(
                agent_id='fundamental_analyst_001',
                llm_adapter=self.llm_adapter,
                config=self.config
            )
            self.agents['fundamental_analyst'] = fundamental_analyst
            self.workflow.register_agent(fundamental_analyst)
        
        # 初始化情感分析师
        if agents_config.get('sentiment_analyst', False):
            sentiment_analyst = SentimentAnalyst(
                agent_id='sentiment_analyst_001',
                llm_adapter=self.llm_adapter,
                config=self.config
            )
            self.agents['sentiment_analyst'] = sentiment_analyst
            self.workflow.register_agent(sentiment_analyst)
        
        # 初始化市场分析师
        if agents_config.get('market_analyst', False):
            market_analyst = MarketAnalyst(
                agent_id='market_analyst_001',
                llm_adapter=self.llm_adapter,
                config=self.config
            )
            self.agents['market_analyst'] = market_analyst
            self.workflow.register_agent(market_analyst)
        
        self.logger.info(f"已初始化 {len(self.agents)} 个Agent")
    
    async def analyze_stock(self, symbol: str, market_data: Dict[str, Any] = None) -> WorkflowResult:
        """分析股票并生成交易建议
        
        Args:
            symbol: 股票代码
            market_data: 市场数据
            
        Returns:
            WorkflowResult: 分析结果
        """
        if not symbol:
            raise ValueError("股票代码不能为空")
        
        self.logger.info(f"开始分析股票: {symbol}")
        
        # 准备输入数据
        input_data = {
            'symbol': symbol,
            'timestamp': datetime.now(),
            'market_data': market_data or {},
        }
        
        # 如果有价格数据，添加到输入中
        if market_data:
            if 'price_data' in market_data:
                input_data['price_data'] = market_data['price_data']
            if 'volume_data' in market_data:
                input_data['volume_data'] = market_data['volume_data']
        
        try:
            # 执行工作流
            result = await self.workflow.execute(symbol, input_data)
            
            self.logger.info(f"股票分析完成: {symbol}, 建议: {result.action}, 置信度: {result.confidence:.2f}")
            return result
            
        except Exception as e:
            self.logger.error(f"股票分析失败: {symbol}, 错误: {e}")
            raise
    
    def analyze_stock_sync(self, symbol: str, market_data: Dict[str, Any] = None) -> WorkflowResult:
        """同步版本的股票分析"""
        return asyncio.run(self.analyze_stock(symbol, market_data))
    
    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        status = {
            'timestamp': datetime.now().isoformat(),
            'llm_adapter': False,
            'agents_count': len(self.agents),
            'agents_status': {}
        }
        
        # 检查LLM适配器
        if self.llm_adapter:
            try:
                status['llm_adapter'] = self.llm_adapter.health_check()
            except:
                status['llm_adapter'] = False
        
        # 检查各个Agent状态
        for agent_id, agent in self.agents.items():
            try:
                # 简单的状态检查
                status['agents_status'][agent_id] = {
                    'agent_type': agent.agent_type,
                    'healthy': True  # 简化的健康检查
                }
            except:
                status['agents_status'][agent_id] = {
                    'agent_type': agent.agent_type,
                    'healthy': False
                }
        
        return status
    
    def get_agent_info(self) -> Dict[str, Any]:
        """获取Agent信息"""
        info = {
            'total_agents': len(self.agents),
            'agents': {}
        }
        
        for agent_id, agent in self.agents.items():
            info['agents'][agent_id] = {
                'agent_type': agent.agent_type,
                'role_description': agent.get_role_description(),
                'required_inputs': agent.get_required_inputs()
            }
        
        return info
    
    def update_config(self, new_config: Dict[str, Any]):
        """更新配置"""
        self.config.update(new_config)
        self.logger.info("配置已更新")
        
        # 重新初始化受影响的组件
        if any(key.startswith('llm_') for key in new_config.keys()):
            self._initialize_llm_adapter()
            self._initialize_agents()  # 重新初始化所有Agent
    
    def add_custom_agent(self, agent: BaseAgent):
        """添加自定义Agent"""
        self.agents[agent.agent_id] = agent
        self.workflow.register_agent(agent)
        self.logger.info(f"已添加自定义Agent: {agent.agent_id} ({agent.agent_type})")
    
    def remove_agent(self, agent_id: str):
        """移除Agent"""
        if agent_id in self.agents:
            del self.agents[agent_id]
            self.logger.info(f"已移除Agent: {agent_id}")
        else:
            self.logger.warning(f"Agent不存在: {agent_id}")
    
    def get_supported_llm_providers(self) -> List[str]:
        """获取支持的LLM提供商"""
        return LLMAdapterFactory.list_providers()
    
    def shutdown(self):
        """关闭引擎"""
        self.logger.info("正在关闭TradingAgents引擎...")
        
        # 清理资源
        self.agents.clear()
        self.llm_adapter = None
        self.workflow = None
        
        self.logger.info("TradingAgents引擎已关闭")