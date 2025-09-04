"""
结构化日志系统 - 支持JSON和Markdown双写格式

实现TradingAgents企业级日志架构：
- JSON格式：机器可读，便于分析和监控
- Markdown格式：人类可读，便于调试和报告
- 统一的日志模式和结构化字段
- 与现有InterpretableLogger集成
"""

import logging
import json
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import traceback
import threading
from concurrent.futures import ThreadPoolExecutor
import queue

from ..agents.protocols import AgentRole, AgentOutput, AgentDecision


class StructuredLogLevel(Enum):
    """结构化日志级别"""
    DEBUG = "debug"
    INFO = "info"
    ANALYSIS = "analysis"
    DECISION = "decision" 
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class LogCategory(Enum):
    """日志分类"""
    SYSTEM = "system"
    AGENT = "agent"
    PIPELINE = "pipeline"
    MARKET_DATA = "market_data"
    TRADING = "trading"
    RISK = "risk"
    PERFORMANCE = "performance"


@dataclass
class StructuredLogEntry:
    """结构化日志条目"""
    timestamp: str
    level: str
    category: str
    component: str
    message: str
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    parent_span_id: Optional[str] = None


class DualFormatLogger:
    """
    双格式结构化日志记录器
    
    功能：
    - JSON格式：结构化数据，便于程序解析和监控
    - Markdown格式：人类可读，便于调试和报告生成
    - 异步写入：提高性能，避免阻塞主线程
    - 线程安全：支持并发场景下的日志记录
    - 分类管理：按组件和类别组织日志
    """
    
    def __init__(
        self,
        log_dir: str = "logs/structured",
        session_id: Optional[str] = None,
        enable_json: bool = True,
        enable_markdown: bool = True,
        enable_console: bool = True,
        async_mode: bool = True,
        buffer_size: int = 1000
    ):
        """
        初始化双格式日志记录器
        
        Args:
            log_dir: 日志输出目录
            session_id: 会话ID
            enable_json: 是否启用JSON格式输出
            enable_markdown: 是否启用Markdown格式输出
            enable_console: 是否启用控制台输出
            async_mode: 是否启用异步模式
            buffer_size: 缓冲区大小
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.session_id = session_id or self._generate_session_id()
        self.enable_json = enable_json
        self.enable_markdown = enable_markdown
        self.enable_console = enable_console
        self.async_mode = async_mode
        
        # 创建输出文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.json_file = self.log_dir / f"session_{self.session_id}_{timestamp}.json"
        self.markdown_file = self.log_dir / f"session_{self.session_id}_{timestamp}.md"
        
        # 初始化Markdown文件头
        if self.enable_markdown:
            self._initialize_markdown_file()
        
        # 设置异步队列和写入器
        self.log_queue = queue.Queue(maxsize=buffer_size) if async_mode else None
        self.writer_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="LogWriter") if async_mode else None
        self.shutdown_flag = threading.Event()
        
        if async_mode:
            self.writer_executor.submit(self._async_writer_worker)
        
        # 日志计数器
        self.entry_counter = 0
        self.lock = threading.Lock()
        
        # 标准日志记录器
        self.logger = logging.getLogger(f"StructuredLogger.{self.session_id}")
        self.logger.setLevel(logging.DEBUG)
    
    def _generate_session_id(self) -> str:
        """生成会话ID"""
        return datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
    
    def _initialize_markdown_file(self):
        """初始化Markdown文件头"""
        header = f"""# TradingAgents 结构化日志

**会话ID**: `{self.session_id}`  
**开始时间**: `{datetime.now().isoformat()}`  
**日志级别**: DEBUG, INFO, ANALYSIS, DECISION, WARNING, ERROR, CRITICAL  

---

"""
        with open(self.markdown_file, 'w', encoding='utf-8') as f:
            f.write(header)
    
    def log(
        self,
        level: Union[StructuredLogLevel, str],
        category: Union[LogCategory, str],
        component: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        trace_id: Optional[str] = None,
        span_id: Optional[str] = None,
        parent_span_id: Optional[str] = None
    ):
        """
        记录结构化日志
        
        Args:
            level: 日志级别
            category: 日志分类
            component: 组件名称
            message: 日志消息
            data: 结构化数据
            metadata: 元数据
            trace_id: 追踪ID
            span_id: 跨度ID
            parent_span_id: 父跨度ID
        """
        with self.lock:
            self.entry_counter += 1
        
        # 标准化参数
        if isinstance(level, str):
            level = StructuredLogLevel(level.lower())
        if isinstance(category, str):
            category = LogCategory(category.lower())
        
        # 创建日志条目
        entry = StructuredLogEntry(
            timestamp=datetime.now().isoformat(),
            level=level.value,
            category=category.value,
            component=component,
            message=message,
            data=data or {},
            metadata={
                "entry_id": self.entry_counter,
                "session_id": self.session_id,
                "thread_id": threading.current_thread().name,
                **(metadata or {})
            },
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=parent_span_id
        )
        
        # 输出到不同格式
        if self.async_mode:
            try:
                self.log_queue.put(entry, timeout=1.0)
            except queue.Full:
                # 队列满时同步写入
                self._write_entry_sync(entry)
        else:
            self._write_entry_sync(entry)
        
        # 控制台输出
        if self.enable_console:
            self._console_output(entry)
    
    def log_agent_output(self, agent_output: AgentOutput, component: str = "agent"):
        """记录智能体输出"""
        self.log(
            level=StructuredLogLevel.ANALYSIS,
            category=LogCategory.AGENT,
            component=f"{component}.{agent_output.role.lower()}",
            message=f"智能体 {agent_output.role} 完成分析",
            data={
                "symbol": agent_output.symbol,
                "score": agent_output.score,
                "confidence": agent_output.confidence,
                "decision": agent_output.decision.model_dump(mode='json') if agent_output.decision else None,
                "features": agent_output.features,
                "rationale": agent_output.rationale,
                "alerts": agent_output.alerts,
                "tags": agent_output.tags
            },
            metadata={
                "agent_id": agent_output.metadata.agent_id if agent_output.metadata else None,
                "execution_time_ms": agent_output.metadata.execution_time_ms if agent_output.metadata else None
            }
        )
    
    def log_pipeline_stage(
        self,
        stage: str,
        status: str,
        results: Dict[str, Any],
        duration_ms: Optional[int] = None
    ):
        """记录流水线阶段"""
        self.log(
            level=StructuredLogLevel.INFO,
            category=LogCategory.PIPELINE,
            component="orchestrator",
            message=f"流水线阶段 {stage} {status}",
            data={
                "stage": stage,
                "status": status,
                "results": results,
                "duration_ms": duration_ms
            }
        )
    
    def log_decision(
        self,
        decision: AgentDecision,
        context: str,
        component: str = "decision_engine"
    ):
        """记录决策"""
        self.log(
            level=StructuredLogLevel.DECISION,
            category=LogCategory.TRADING,
            component=component,
            message=f"交易决策: {decision.action.value}",
            data={
                "action": decision.action.value,
                "weight": decision.weight,
                "confidence": decision.confidence,
                "reasoning": decision.reasoning,
                "risk_level": decision.risk_level,
                "expected_return": decision.expected_return,
                "max_loss": decision.max_loss,
                "time_horizon": decision.time_horizon,
                "context": context
            }
        )
    
    def log_error(
        self,
        component: str,
        error: Exception,
        context: Optional[Dict[str, Any]] = None
    ):
        """记录错误"""
        self.log(
            level=StructuredLogLevel.ERROR,
            category=LogCategory.SYSTEM,
            component=component,
            message=f"错误: {str(error)}",
            data={
                "error_type": type(error).__name__,
                "error_message": str(error),
                "traceback": traceback.format_exc(),
                "context": context or {}
            }
        )
    
    def log_performance(
        self,
        component: str,
        metric: str,
        value: float,
        unit: str = "",
        additional_data: Optional[Dict[str, Any]] = None
    ):
        """记录性能指标"""
        self.log(
            level=StructuredLogLevel.INFO,
            category=LogCategory.PERFORMANCE,
            component=component,
            message=f"性能指标: {metric} = {value}{unit}",
            data={
                "metric": metric,
                "value": value,
                "unit": unit,
                **(additional_data or {})
            }
        )
    
    def _write_entry_sync(self, entry: StructuredLogEntry):
        """同步写入日志条目"""
        try:
            # 写入JSON格式
            if self.enable_json:
                self._write_json_entry(entry)
            
            # 写入Markdown格式
            if self.enable_markdown:
                self._write_markdown_entry(entry)
                
        except Exception as e:
            # 记录写入错误（避免无限递归）
            print(f"日志写入错误: {e}")
    
    def _write_json_entry(self, entry: StructuredLogEntry):
        """写入JSON格式日志"""
        entry_dict = asdict(entry)
        json_line = json.dumps(entry_dict, ensure_ascii=False) + '\n'
        
        with open(self.json_file, 'a', encoding='utf-8') as f:
            f.write(json_line)
            f.flush()
    
    def _write_markdown_entry(self, entry: StructuredLogEntry):
        """写入Markdown格式日志"""
        # 根据日志级别选择图标
        level_icons = {
            "debug": "🔍",
            "info": "ℹ️",
            "analysis": "📊",
            "decision": "⚡",
            "warning": "⚠️",
            "error": "❌",
            "critical": "🚨"
        }
        
        icon = level_icons.get(entry.level, "📝")
        timestamp = datetime.fromisoformat(entry.timestamp).strftime("%H:%M:%S")
        
        markdown_content = f"""
## {icon} {entry.level.upper()} - {entry.component}

**时间**: `{timestamp}`  
**类别**: `{entry.category}`  
**消息**: {entry.message}  
"""
        
        # 添加结构化数据
        if entry.data:
            markdown_content += "\n**数据**:\n```json\n"
            markdown_content += json.dumps(entry.data, ensure_ascii=False, indent=2)
            markdown_content += "\n```\n"
        
        # 添加元数据
        if entry.metadata and any(k not in ["entry_id", "session_id", "thread_id"] for k in entry.metadata.keys()):
            filtered_metadata = {k: v for k, v in entry.metadata.items() 
                               if k not in ["entry_id", "session_id", "thread_id"]}
            if filtered_metadata:
                markdown_content += "\n**元数据**:\n```json\n"
                markdown_content += json.dumps(filtered_metadata, ensure_ascii=False, indent=2)
                markdown_content += "\n```\n"
        
        markdown_content += "\n---\n"
        
        with open(self.markdown_file, 'a', encoding='utf-8') as f:
            f.write(markdown_content)
            f.flush()
    
    def _console_output(self, entry: StructuredLogEntry):
        """控制台输出"""
        timestamp = datetime.fromisoformat(entry.timestamp).strftime("%H:%M:%S")
        level_colors = {
            "debug": "\033[36m",    # 青色
            "info": "\033[37m",     # 白色
            "analysis": "\033[32m", # 绿色
            "decision": "\033[33m", # 黄色
            "warning": "\033[93m",  # 亮黄色
            "error": "\033[91m",    # 亮红色
            "critical": "\033[95m"  # 亮紫色
        }
        reset = "\033[0m"
        
        color = level_colors.get(entry.level, "\033[37m")
        print(f"{color}[{timestamp}] {entry.level.upper()} {entry.component}: {entry.message}{reset}")
        
        if entry.data and entry.level in ["error", "critical"]:
            print(f"  数据: {json.dumps(entry.data, ensure_ascii=False, indent=2)}")
    
    def _async_writer_worker(self):
        """异步写入器工作线程"""
        while not self.shutdown_flag.is_set():
            try:
                entry = self.log_queue.get(timeout=1.0)
                if entry is None:  # 停止信号
                    break
                self._write_entry_sync(entry)
                self.log_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"异步日志写入错误: {e}")
    
    def close(self):
        """关闭日志记录器"""
        if self.async_mode:
            # 停止异步写入器
            self.shutdown_flag.set()
            if self.log_queue:
                self.log_queue.put(None)  # 发送停止信号
            
            # 等待队列清空
            if self.log_queue:
                self.log_queue.join()
            
            # 关闭执行器
            if self.writer_executor:
                self.writer_executor.shutdown(wait=True)
        
        # 写入Markdown文件尾
        if self.enable_markdown:
            with open(self.markdown_file, 'a', encoding='utf-8') as f:
                f.write(f"\n---\n**结束时间**: `{datetime.now().isoformat()}`\n")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# 全局结构化日志记录器实例
_global_structured_logger: Optional[DualFormatLogger] = None
_logger_lock = threading.Lock()


def get_structured_logger(
    session_id: Optional[str] = None,
    **kwargs
) -> DualFormatLogger:
    """获取全局结构化日志记录器"""
    global _global_structured_logger
    
    with _logger_lock:
        if _global_structured_logger is None:
            _global_structured_logger = DualFormatLogger(
                session_id=session_id,
                **kwargs
            )
    
    return _global_structured_logger


def close_structured_logger():
    """关闭全局结构化日志记录器"""
    global _global_structured_logger
    
    with _logger_lock:
        if _global_structured_logger is not None:
            _global_structured_logger.close()
            _global_structured_logger = None


# 便捷函数
def log_debug(component: str, message: str, data: Optional[Dict[str, Any]] = None, **kwargs):
    """记录调试日志"""
    get_structured_logger().log(StructuredLogLevel.DEBUG, LogCategory.SYSTEM, component, message, data, **kwargs)


def log_info(component: str, message: str, data: Optional[Dict[str, Any]] = None, **kwargs):
    """记录信息日志"""
    get_structured_logger().log(StructuredLogLevel.INFO, LogCategory.SYSTEM, component, message, data, **kwargs)


def log_analysis(component: str, message: str, data: Optional[Dict[str, Any]] = None, **kwargs):
    """记录分析日志"""
    get_structured_logger().log(StructuredLogLevel.ANALYSIS, LogCategory.AGENT, component, message, data, **kwargs)


def log_decision(component: str, message: str, data: Optional[Dict[str, Any]] = None, **kwargs):
    """记录决策日志"""
    get_structured_logger().log(StructuredLogLevel.DECISION, LogCategory.TRADING, component, message, data, **kwargs)


def log_warning(component: str, message: str, data: Optional[Dict[str, Any]] = None, **kwargs):
    """记录警告日志"""
    get_structured_logger().log(StructuredLogLevel.WARNING, LogCategory.SYSTEM, component, message, data, **kwargs)


def log_error(component: str, error: Union[str, Exception], data: Optional[Dict[str, Any]] = None, **kwargs):
    """记录错误日志"""
    if isinstance(error, Exception):
        get_structured_logger().log_error(component, error, data)
    else:
        get_structured_logger().log(StructuredLogLevel.ERROR, LogCategory.SYSTEM, component, str(error), data, **kwargs)