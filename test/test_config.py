"""
测试配置管理模块
"""

import os
import sys
import tempfile
from pathlib import Path

# 添加src到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mytrade.config import ConfigManager, Config


def test_config_manager():
    """测试配置管理功能"""
    print("=== 测试配置管理功能 ===")
    
    # 1. 测试默认配置
    print("1. 测试默认配置...")
    config_manager = ConfigManager("non_existent_config.yaml")
    config = config_manager.config
    
    print(f"数据源: {config.data.source}")
    print(f"初始资金: {config.backtest.initial_cash}")
    print(f"日志级别: {config.logs.level}")
    print()
    
    # 2. 测试创建自定义配置文件
    print("2. 测试自定义配置...")
    test_config_content = """
data:
  source: "tushare"
  cache_dir: "./test_cache"
  tushare_token: "${TUSHARE_TOKEN:test_token}"

trading_agents:
  model_fast: "gpt-3.5-turbo"
  openai_api_key: "${OPENAI_API_KEY}"
  debate_rounds: 3

backtest:
  initial_cash: 500000.0
  commission: 0.002

logs:
  level: "DEBUG"
  keep_days: 7
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(test_config_content)
        temp_config_path = f.name
    
    try:
        # 设置测试环境变量
        os.environ['TUSHARE_TOKEN'] = 'my_test_token'
        os.environ['OPENAI_API_KEY'] = 'sk-test-key'
        
        test_config_manager = ConfigManager(temp_config_path)
        test_config = test_config_manager.config
        
        print(f"数据源: {test_config.data.source}")
        print(f"Tushare Token: {test_config.data.tushare_token}")
        print(f"OpenAI Key: {test_config.trading_agents.openai_api_key[:10]}...")
        print(f"辩论轮次: {test_config.trading_agents.debate_rounds}")
        print(f"初始资金: {test_config.backtest.initial_cash}")
        print(f"日志级别: {test_config.logs.level}")
        print()
        
    finally:
        os.unlink(temp_config_path)
        # 清理环境变量
        os.environ.pop('TUSHARE_TOKEN', None)
        os.environ.pop('OPENAI_API_KEY', None)
    
    # 3. 测试配置获取
    print("3. 测试配置项获取...")
    data_source = config_manager.get('data.source')
    initial_cash = config_manager.get('backtest.initial_cash')
    non_existent = config_manager.get('non.existent.key', 'default_value')
    
    print(f"data.source: {data_source}")
    print(f"backtest.initial_cash: {initial_cash}")
    print(f"non.existent.key: {non_existent}")
    print()
    
    # 4. 测试配置更新
    print("4. 测试配置更新...")
    old_cash = config_manager.config.backtest.initial_cash
    
    config_manager.update({
        'backtest': {
            'initial_cash': 2000000.0
        }
    })
    
    new_cash = config_manager.config.backtest.initial_cash
    print(f"更新前初始资金: {old_cash}")
    print(f"更新后初始资金: {new_cash}")
    print()
    
    # 5. 测试环境验证
    print("5. 测试环境验证...")
    validation_result = config_manager.validate_environment()
    print(f"验证通过: {validation_result['valid']}")
    if validation_result['warnings']:
        print("警告:")
        for warning in validation_result['warnings']:
            print(f"  - {warning}")
    if validation_result['errors']:
        print("错误:")
        for error in validation_result['errors']:
            print(f"  - {error}")
    print()
    
    # 6. 测试配置摘要
    print("6. 配置摘要:")
    summary = config_manager.get_config_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    test_config_manager()