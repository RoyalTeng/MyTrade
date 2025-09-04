"""
配置管理器模块

负责加载和管理系统配置，支持环境变量替换和配置验证。
"""

import os
import re
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union

import yaml
from pydantic import BaseModel, Field, validator


class DataConfig(BaseModel):
    """数据配置"""
    source: str = "akshare"
    cache_dir: str = "./data/cache"
    cache_days: int = 7
    max_retries: int = 3
    retry_delay: float = 1.0
    update_interval: str = "daily"
    tushare_token: Optional[str] = None


class TradingAgentsConfig(BaseModel):
    """TradingAgents配置"""
    model_fast: str = "gpt-3.5-turbo"
    model_deep: str = "gpt-4"
    use_online_data: bool = False
    debate_rounds: int = 2
    openai_api_key: Optional[str] = None
    
    @validator('debate_rounds')
    def validate_debate_rounds(cls, v):
        if v < 1 or v > 10:
            raise ValueError('debate_rounds must be between 1 and 10')
        return v


class BacktestConfig(BaseModel):
    """回测配置"""
    initial_cash: float = 1000000.0
    commission: float = 0.001
    slippage: float = 0.0005
    
    @validator('initial_cash')
    def validate_initial_cash(cls, v):
        if v <= 0:
            raise ValueError('initial_cash must be positive')
        return v
    
    @validator('commission', 'slippage')
    def validate_rates(cls, v):
        if v < 0 or v > 0.1:
            raise ValueError('Rate must be between 0 and 0.1')
        return v


class LogsConfig(BaseModel):
    """日志配置"""
    path: str = "./logs"
    keep_days: int = 30
    level: str = "INFO"
    enable_explain_logs: bool = True
    
    @validator('level')
    def validate_level(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'Level must be one of {valid_levels}')
        return v.upper()


class ExpertDialogueConfig(BaseModel):
    """专家对话配置"""
    mode: str = "CLI"
    use_local_llm: bool = False
    llm_model: str = "gpt-3.5-turbo"
    max_response_length: int = 500


class SystemConfig(BaseModel):
    """系统配置"""
    timezone: str = "Asia/Shanghai"
    market_hours: Dict[str, str] = Field(default_factory=lambda: {
        "start": "09:30",
        "end": "15:00"
    })
    trading_days_only: bool = True


class Config(BaseModel):
    """主配置类"""
    data: DataConfig = Field(default_factory=DataConfig)
    trading_agents: TradingAgentsConfig = Field(default_factory=TradingAgentsConfig)
    backtest: BacktestConfig = Field(default_factory=BacktestConfig)
    logs: LogsConfig = Field(default_factory=LogsConfig)
    expert_dialogue: ExpertDialogueConfig = Field(default_factory=ExpertDialogueConfig)
    system: SystemConfig = Field(default_factory=SystemConfig)


class ConfigManager:
    """
    配置管理器
    
    功能：
    - 从YAML文件加载配置
    - 支持环境变量替换
    - 提供配置验证
    - 支持配置热重载
    """
    
    def __init__(self, config_path: Union[str, Path] = "config.yaml"):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = Path(config_path)
        self.logger = logging.getLogger(self.__class__.__name__)
        self._config: Optional[Config] = None
        self._file_mtime: Optional[float] = None
        
        # 加载配置
        self.reload()

    def reload(self) -> None:
        """重新加载配置"""
        try:
            if not self.config_path.exists():
                self.logger.warning(f"Config file not found: {self.config_path}, using defaults")
                self._config = Config()
                return
                
            # 检查文件是否有更新
            current_mtime = self.config_path.stat().st_mtime
            if self._file_mtime and current_mtime == self._file_mtime:
                return  # 文件未更新
                
            # 读取YAML文件
            with open(self.config_path, 'r', encoding='utf-8') as f:
                raw_config = yaml.safe_load(f)
                
            if raw_config is None:
                raw_config = {}
                
            # 环境变量替换
            processed_config = self._substitute_env_vars(raw_config)
            
            # 验证和创建配置对象
            self._config = Config(**processed_config)
            self._file_mtime = current_mtime
            
            self.logger.info(f"Configuration loaded from {self.config_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            if self._config is None:
                # 如果是首次加载失败，使用默认配置
                self._config = Config()
                self.logger.info("Using default configuration")

    def _substitute_env_vars(self, obj: Any) -> Any:
        """
        递归替换环境变量
        
        支持格式: ${VAR_NAME} 或 ${VAR_NAME:default_value}
        """
        if isinstance(obj, dict):
            return {key: self._substitute_env_vars(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._substitute_env_vars(item) for item in obj]
        elif isinstance(obj, str):
            return self._substitute_string_env_vars(obj)
        else:
            return obj
            
    def _substitute_string_env_vars(self, text: str) -> str:
        """替换字符串中的环境变量"""
        pattern = re.compile(r'\$\{([^}]+)\}')
        
        def replace_var(match):
            var_expr = match.group(1)
            if ':' in var_expr:
                var_name, default_value = var_expr.split(':', 1)
            else:
                var_name, default_value = var_expr, ''
                
            return os.getenv(var_name.strip(), default_value)
        
        return pattern.sub(replace_var, text)

    @property
    def config(self) -> Config:
        """获取当前配置"""
        if self._config is None:
            self.reload()
        return self._config
    
    def get_config(self) -> Config:
        """获取配置对象"""
        return self.config

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置项
        
        Args:
            key: 配置键，支持点分隔格式如 'data.source'
            default: 默认值
        """
        try:
            keys = key.split('.')
            obj = self.config
            
            for k in keys:
                if hasattr(obj, k):
                    obj = getattr(obj, k)
                else:
                    return default
                    
            return obj
        except Exception:
            return default

    def update(self, updates: Dict[str, Any]) -> None:
        """
        更新配置（运行时）
        
        Args:
            updates: 要更新的配置字典
        """
        try:
            # 将当前配置转为字典
            current_dict = self.config.dict()
            
            # 递归更新
            self._deep_update(current_dict, updates)
            
            # 重新验证配置
            self._config = Config(**current_dict)
            
            self.logger.info("Configuration updated")
            
        except Exception as e:
            self.logger.error(f"Failed to update configuration: {e}")
            raise

    def _deep_update(self, base_dict: Dict, update_dict: Dict) -> None:
        """递归深度更新字典"""
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value

    def save_to_file(self, file_path: Optional[Union[str, Path]] = None) -> None:
        """
        保存配置到文件
        
        Args:
            file_path: 保存路径，默认为原配置文件路径
        """
        if file_path is None:
            file_path = self.config_path
        else:
            file_path = Path(file_path)
            
        try:
            config_dict = self.config.dict()
            
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(config_dict, f, default_flow_style=False, allow_unicode=True)
                
            self.logger.info(f"Configuration saved to {file_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
            raise

    def validate_environment(self) -> Dict[str, Any]:
        """
        验证环境配置
        
        Returns:
            验证结果字典
        """
        validation_result = {
            "valid": True,
            "warnings": [],
            "errors": []
        }
        
        # 检查必要的环境变量
        if self.config.trading_agents.openai_api_key is None or not self.config.trading_agents.openai_api_key.strip():
            validation_result["warnings"].append("OPENAI_API_KEY not set, TradingAgents functionality may be limited")
        
        if self.config.data.source == "tushare" and (not self.config.data.tushare_token or not self.config.data.tushare_token.strip()):
            validation_result["warnings"].append("TUSHARE_TOKEN not set but tushare is selected as data source")
        
        # 检查路径
        try:
            Path(self.config.data.cache_dir).mkdir(parents=True, exist_ok=True)
            Path(self.config.logs.path).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            validation_result["errors"].append(f"Cannot create directories: {e}")
            validation_result["valid"] = False
        
        # 检查数值范围
        if self.config.backtest.initial_cash <= 0:
            validation_result["errors"].append("Backtest initial_cash must be positive")
            validation_result["valid"] = False
            
        return validation_result

    def get_config_summary(self) -> Dict[str, Any]:
        """获取配置摘要"""
        return {
            "config_file": str(self.config_path),
            "file_exists": self.config_path.exists(),
            "last_modified": self._file_mtime,
            "data_source": self.config.data.source,
            "cache_dir": self.config.data.cache_dir,
            "initial_cash": self.config.backtest.initial_cash,
            "log_level": self.config.logs.level,
            "openai_configured": bool(self.config.trading_agents.openai_api_key and self.config.trading_agents.openai_api_key.strip()),
            "tushare_configured": bool(self.config.data.tushare_token and self.config.data.tushare_token.strip())
        }


# 全局配置实例
_config_manager: Optional[ConfigManager] = None


def get_config_manager(config_path: Union[str, Path] = "config.yaml") -> ConfigManager:
    """获取全局配置管理器实例"""
    global _config_manager
    
    if _config_manager is None:
        _config_manager = ConfigManager(config_path)
    
    return _config_manager


def get_config() -> Config:
    """获取当前配置"""
    return get_config_manager().config