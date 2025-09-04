"""
配置管理模块
"""

from .config_manager import ConfigManager, Config, DataConfig

def get_config_manager(config_path: str) -> ConfigManager:
    """获取配置管理器实例"""
    return ConfigManager(config_path)

def get_config(config_path: str = "config.yaml") -> Config:
    """获取配置对象"""
    manager = ConfigManager(config_path)
    return manager.get_config()

__all__ = ["ConfigManager", "Config", "DataConfig", "get_config_manager", "get_config"]