"""
可解释性思路日志记录器

记录TradingAgents的分析过程，提供人类可读的决策解释。
"""

import logging
import json
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

import pandas as pd
from pydantic import BaseModel


class LogLevel(Enum):
    """日志级别"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    ANALYSIS = "ANALYSIS"
    DECISION = "DECISION"
    WARNING = "WARNING"
    ERROR = "ERROR"


class AgentType(Enum):
    """智能体类型"""
    TECHNICAL_ANALYST = "技术分析师"
    FUNDAMENTAL_ANALYST = "基本面分析师"
    SENTIMENT_ANALYST = "情绪分析师"
    BULLISH_RESEARCHER = "多头研究员"
    BEARISH_RESEARCHER = "空头研究员"
    TRADER = "交易员"
    RISK_MANAGER = "风控经理"


@dataclass
class AnalysisStep:
    """分析步骤记录"""
    step_id: str
    agent_type: AgentType
    timestamp: str
    input_data: Dict[str, Any]
    analysis_process: str
    conclusion: str
    confidence: float
    reasoning: List[str]
    supporting_data: Dict[str, Any]


@dataclass
class DecisionPoint:
    """决策点记录"""
    decision_id: str
    timestamp: str
    context: str
    options: List[Dict[str, Any]]
    chosen_option: Dict[str, Any]
    rationale: str
    risk_assessment: Dict[str, Any]
    confidence: float


@dataclass
class TradingSession:
    """交易会话记录"""
    session_id: str
    symbol: str
    date: str
    start_time: str
    end_time: str
    analysis_steps: List[AnalysisStep]
    decision_points: List[DecisionPoint]
    final_decision: Dict[str, Any]
    performance_data: Dict[str, Any]


class InterpretableLogger:
    """
    可解释性日志记录器
    
    功能：
    - 记录TradingAgents的完整分析过程
    - 生成人类可读的决策解释
    - 提供多种输出格式（文本、JSON、HTML）
    - 支持决策路径回溯和分析
    """
    
    def __init__(
        self, 
        log_dir: str = "logs/interpretable",
        session_id: Optional[str] = None,
        enable_console_output: bool = True,
        enable_file_output: bool = True
    ):
        """
        初始化可解释性日志记录器
        
        Args:
            log_dir: 日志输出目录
            session_id: 会话ID，如果为None则自动生成
            enable_console_output: 是否启用控制台输出
            enable_file_output: 是否启用文件输出
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.session_id = session_id or self._generate_session_id()
        self.enable_console_output = enable_console_output
        self.enable_file_output = enable_file_output
        
        # 当前交易会话
        self.current_session: Optional[TradingSession] = None
        self.step_counter = 0
        self.decision_counter = 0
        
        # 设置标准日志记录器
        self.logger = logging.getLogger(f"InterpretableLogger.{self.session_id}")
        
        # 配置文件处理器
        self.file_handler = None
        if enable_file_output:
            log_file = self.log_dir / f"session_{self.session_id}.log"
            self.file_handler = logging.FileHandler(log_file, encoding='utf-8')
            self.file_handler.setLevel(logging.INFO)
            
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            self.file_handler.setFormatter(formatter)
            self.logger.addHandler(self.file_handler)
        
        self.logger.setLevel(logging.INFO)
        self.logger.info(f"InterpretableLogger initialized for session {self.session_id}")
    
    def start_trading_session(
        self, 
        symbol: str, 
        date: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        开始新的交易会话
        
        Args:
            symbol: 股票代码
            date: 交易日期
            context: 上下文信息
        
        Returns:
            会话ID
        """
        session_id = f"{symbol}_{date}_{self._generate_timestamp()}"
        
        self.current_session = TradingSession(
            session_id=session_id,
            symbol=symbol,
            date=date,
            start_time=datetime.now().isoformat(),
            end_time="",
            analysis_steps=[],
            decision_points=[],
            final_decision={},
            performance_data={}
        )
        
        self.step_counter = 0
        self.decision_counter = 0
        
        self._log_message(
            LogLevel.INFO,
            f"开始交易会话: {symbol} ({date})",
            {"session_id": session_id, "context": context or {}}
        )
        
        return session_id
    
    def log_analysis_step(
        self,
        agent_type: Union[AgentType, str],
        input_data: Dict[str, Any],
        analysis_process: str,
        conclusion: str,
        confidence: float,
        reasoning: List[str],
        supporting_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        记录分析步骤
        
        Args:
            agent_type: 智能体类型
            input_data: 输入数据
            analysis_process: 分析过程描述
            conclusion: 分析结论
            confidence: 置信度
            reasoning: 推理过程
            supporting_data: 支撑数据
        
        Returns:
            步骤ID
        """
        if not self.current_session:
            raise ValueError("没有活跃的交易会话，请先调用 start_trading_session()")
        
        self.step_counter += 1
        step_id = f"step_{self.step_counter:03d}"
        
        if isinstance(agent_type, str):
            agent_type = self._parse_agent_type(agent_type)
        
        step = AnalysisStep(
            step_id=step_id,
            agent_type=agent_type,
            timestamp=datetime.now().isoformat(),
            input_data=input_data,
            analysis_process=analysis_process,
            conclusion=conclusion,
            confidence=confidence,
            reasoning=reasoning,
            supporting_data=supporting_data or {}
        )
        
        self.current_session.analysis_steps.append(step)
        
        # 生成可读的日志消息
        readable_log = self._format_analysis_step(step)
        self._log_message(LogLevel.ANALYSIS, readable_log)
        
        return step_id
    
    def log_decision_point(
        self,
        context: str,
        options: List[Dict[str, Any]],
        chosen_option: Dict[str, Any],
        rationale: str,
        risk_assessment: Optional[Dict[str, Any]] = None,
        confidence: float = 0.5
    ) -> str:
        """
        记录决策点
        
        Args:
            context: 决策上下文
            options: 可选方案
            chosen_option: 选择的方案
            rationale: 选择理由
            risk_assessment: 风险评估
            confidence: 置信度
        
        Returns:
            决策点ID
        """
        if not self.current_session:
            raise ValueError("没有活跃的交易会话，请先调用 start_trading_session()")
        
        self.decision_counter += 1
        decision_id = f"decision_{self.decision_counter:03d}"
        
        decision_point = DecisionPoint(
            decision_id=decision_id,
            timestamp=datetime.now().isoformat(),
            context=context,
            options=options,
            chosen_option=chosen_option,
            rationale=rationale,
            risk_assessment=risk_assessment or {},
            confidence=confidence
        )
        
        self.current_session.decision_points.append(decision_point)
        
        # 生成可读的日志消息
        readable_log = self._format_decision_point(decision_point)
        self._log_message(LogLevel.DECISION, readable_log)
        
        return decision_id
    
    def end_trading_session(
        self, 
        final_decision: Dict[str, Any],
        performance_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        结束交易会话
        
        Args:
            final_decision: 最终决策
            performance_data: 性能数据
        
        Returns:
            会话摘要
        """
        if not self.current_session:
            raise ValueError("没有活跃的交易会话")
        
        self.current_session.end_time = datetime.now().isoformat()
        self.current_session.final_decision = final_decision
        self.current_session.performance_data = performance_data or {}
        
        # 生成会话摘要
        summary = self._generate_session_summary()
        
        # 保存会话记录
        if self.enable_file_output:
            self._save_session_record()
            self._generate_readable_report()
        
        self._log_message(
            LogLevel.INFO,
            f"交易会话结束: {self.current_session.symbol}",
            {
                "final_decision": final_decision,
                "total_steps": len(self.current_session.analysis_steps),
                "total_decisions": len(self.current_session.decision_points)
            }
        )
        
        # 关闭文件句柄
        self._cleanup_handlers()
        
        # 重置当前会话
        completed_session = self.current_session
        self.current_session = None
        
        return summary
    
    def _cleanup_handlers(self) -> None:
        """清理文件处理器"""
        if self.file_handler:
            try:
                # 刷新并关闭文件句柄
                self.file_handler.flush()
                self.file_handler.close()
                # 从logger中移除处理器
                self.logger.removeHandler(self.file_handler)
                self.file_handler = None
            except Exception as e:
                pass  # 忽略清理错误
    
    def _generate_session_id(self) -> str:
        """生成会话ID"""
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _generate_timestamp(self) -> str:
        """生成时间戳"""
        return datetime.now().strftime("%H%M%S")
    
    def _parse_agent_type(self, agent_type_str: str) -> AgentType:
        """解析智能体类型字符串"""
        type_mapping = {
            "technical_analyst": AgentType.TECHNICAL_ANALYST,
            "fundamental_analyst": AgentType.FUNDAMENTAL_ANALYST,
            "sentiment_analyst": AgentType.SENTIMENT_ANALYST,
            "bullish_researcher": AgentType.BULLISH_RESEARCHER,
            "bearish_researcher": AgentType.BEARISH_RESEARCHER,
            "trader": AgentType.TRADER,
            "risk_manager": AgentType.RISK_MANAGER,
        }
        return type_mapping.get(agent_type_str.lower(), AgentType.TECHNICAL_ANALYST)
    
    def _format_analysis_step(self, step: AnalysisStep) -> str:
        """格式化分析步骤为可读文本"""
        lines = [
            f"📊 {step.agent_type.value} 分析 (置信度: {step.confidence:.2f})",
            f"分析过程: {step.analysis_process}",
            f"结论: {step.conclusion}",
            "推理过程:"
        ]
        
        for i, reason in enumerate(step.reasoning, 1):
            lines.append(f"  {i}. {reason}")
        
        if step.supporting_data:
            lines.append("支撑数据:")
            for key, value in step.supporting_data.items():
                lines.append(f"  {key}: {value}")
        
        return "\n".join(lines)
    
    def _format_decision_point(self, decision: DecisionPoint) -> str:
        """格式化决策点为可读文本"""
        lines = [
            f"⚡ 决策点: {decision.context}",
            f"可选方案: {len(decision.options)} 个",
            f"选择: {decision.chosen_option.get('action', 'Unknown')}",
            f"理由: {decision.rationale}",
            f"置信度: {decision.confidence:.2f}"
        ]
        
        if decision.risk_assessment:
            lines.append("风险评估:")
            for key, value in decision.risk_assessment.items():
                lines.append(f"  {key}: {value}")
        
        return "\n".join(lines)
    
    def _log_message(
        self, 
        level: LogLevel, 
        message: str, 
        data: Optional[Dict[str, Any]] = None
    ) -> None:
        """记录日志消息"""
        # 控制台输出
        if self.enable_console_output:
            print(f"[{level.value}] {message}")
            if data:
                print(f"数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
        
        # 标准日志记录
        log_level_mapping = {
            LogLevel.DEBUG: logging.DEBUG,
            LogLevel.INFO: logging.INFO,
            LogLevel.ANALYSIS: logging.INFO,
            LogLevel.DECISION: logging.INFO,
            LogLevel.WARNING: logging.WARNING,
            LogLevel.ERROR: logging.ERROR
        }
        
        self.logger.log(log_level_mapping[level], message)
        if data:
            self.logger.log(log_level_mapping[level], f"Data: {json.dumps(data, ensure_ascii=False)}")
    
    def _generate_session_summary(self) -> Dict[str, Any]:
        """生成会话摘要"""
        if not self.current_session:
            return {}
        
        session = self.current_session
        
        # 计算分析统计
        agent_stats = {}
        for step in session.analysis_steps:
            agent_type = step.agent_type.value
            if agent_type not in agent_stats:
                agent_stats[agent_type] = {"count": 0, "avg_confidence": 0.0}
            agent_stats[agent_type]["count"] += 1
            agent_stats[agent_type]["avg_confidence"] += step.confidence
        
        # 计算平均置信度
        for agent_type, stats in agent_stats.items():
            stats["avg_confidence"] /= stats["count"]
        
        return {
            "session_id": session.session_id,
            "symbol": session.symbol,
            "date": session.date,
            "duration_minutes": self._calculate_duration_minutes(),
            "total_analysis_steps": len(session.analysis_steps),
            "total_decision_points": len(session.decision_points),
            "agent_statistics": agent_stats,
            "final_decision": session.final_decision,
            "average_confidence": sum(step.confidence for step in session.analysis_steps) / len(session.analysis_steps) if session.analysis_steps else 0.0
        }
    
    def _calculate_duration_minutes(self) -> float:
        """计算会话持续时间（分钟）"""
        if not self.current_session or not self.current_session.end_time:
            return 0.0
        
        start = datetime.fromisoformat(self.current_session.start_time)
        end = datetime.fromisoformat(self.current_session.end_time)
        return (end - start).total_seconds() / 60.0
    
    def _save_session_record(self) -> None:
        """保存会话记录到JSON文件"""
        if not self.current_session:
            return
        
        filename = f"session_{self.current_session.session_id}.json"
        filepath = self.log_dir / filename
        
        try:
            # 转换为可序列化的字典
            session_dict = asdict(self.current_session)
            
            # 处理枚举类型
            for step in session_dict["analysis_steps"]:
                step["agent_type"] = step["agent_type"].value if hasattr(step["agent_type"], 'value') else str(step["agent_type"])
            
            # 确保目录存在
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            # 使用临时文件写入，然后原子性移动
            temp_filepath = filepath.with_suffix('.tmp')
            
            with open(temp_filepath, 'w', encoding='utf-8') as f:
                json.dump(session_dict, f, ensure_ascii=False, indent=2)
                f.flush()  # 确保数据写入磁盘
            
            # 原子性移动到最终位置
            temp_filepath.replace(filepath)
            
        except Exception as e:
            self.logger.warning(f"Failed to save session record: {e}")
            # 清理临时文件
            temp_filepath = filepath.with_suffix('.tmp')
            if temp_filepath.exists():
                try:
                    temp_filepath.unlink()
                except:
                    pass
    
    def _generate_readable_report(self) -> None:
        """生成可读的报告文件"""
        if not self.current_session:
            return
        
        filename = f"report_{self.current_session.session_id}.md"
        filepath = self.log_dir / filename
        
        lines = [
            f"# 交易分析报告",
            f"",
            f"**股票代码**: {self.current_session.symbol}",
            f"**分析日期**: {self.current_session.date}",
            f"**会话ID**: {self.current_session.session_id}",
            f"**开始时间**: {self.current_session.start_time}",
            f"**结束时间**: {self.current_session.end_time}",
            f"",
            f"## 分析过程",
            f""
        ]
        
        # 添加分析步骤
        for i, step in enumerate(self.current_session.analysis_steps, 1):
            lines.extend([
                f"### {i}. {step.agent_type.value}",
                f"",
                f"**置信度**: {step.confidence:.2f}",
                f"",
                f"**分析过程**: {step.analysis_process}",
                f"",
                f"**结论**: {step.conclusion}",
                f"",
                f"**推理过程**:",
            ])
            
            for j, reason in enumerate(step.reasoning, 1):
                lines.append(f"{j}. {reason}")
            
            lines.append("")
        
        # 添加决策点
        if self.current_session.decision_points:
            lines.extend([
                f"## 决策过程",
                f""
            ])
            
            for i, decision in enumerate(self.current_session.decision_points, 1):
                lines.extend([
                    f"### 决策 {i}: {decision.context}",
                    f"",
                    f"**选择**: {decision.chosen_option.get('action', 'Unknown')}",
                    f"",
                    f"**理由**: {decision.rationale}",
                    f"",
                    f"**置信度**: {decision.confidence:.2f}",
                    f""
                ])
        
        # 添加最终决策
        lines.extend([
            f"## 最终决策",
            f"",
            f"```json",
            json.dumps(self.current_session.final_decision, ensure_ascii=False, indent=2),
            f"```",
            f""
        ])
        
        try:
            # 确保目录存在
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            # 使用临时文件写入，然后原子性移动
            temp_filepath = filepath.with_suffix('.tmp')
            
            with open(temp_filepath, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
                f.flush()  # 确保数据写入磁盘
            
            # 原子性移动到最终位置
            temp_filepath.replace(filepath)
            
        except Exception as e:
            self.logger.warning(f"Failed to generate readable report: {e}")
            # 清理临时文件
            temp_filepath = filepath.with_suffix('.tmp')
            if temp_filepath.exists():
                try:
                    temp_filepath.unlink()
                except:
                    pass
    
    def get_session_history(self) -> List[Dict[str, Any]]:
        """获取历史会话记录"""
        history = []
        
        # 扫描日志目录中的JSON文件
        for json_file in self.log_dir.glob("session_*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                    history.append({
                        "session_id": session_data.get("session_id"),
                        "symbol": session_data.get("symbol"),
                        "date": session_data.get("date"),
                        "file_path": str(json_file)
                    })
            except Exception as e:
                self.logger.warning(f"Failed to load session file {json_file}: {e}")
        
        return sorted(history, key=lambda x: x.get("date", ""), reverse=True)