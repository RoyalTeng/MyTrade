"""
测试可解释性日志记录模块
"""

import sys
import logging
from pathlib import Path
from datetime import datetime, timedelta

# 添加src到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mytrade.logging import InterpretableLogger, AgentType, LogLevel
from mytrade.config import get_config_manager


def test_interpretable_logger():
    """测试可解释性日志记录功能"""
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("=== 测试可解释性日志记录功能 ===")
    
    # 初始化配置（使用默认配置）
    config_manager = get_config_manager("../config.yaml")
    
    # 1. 测试创建日志记录器
    print("\n1. 创建可解释性日志记录器...")
    
    logger = InterpretableLogger(
        log_dir="test/interpretable_logs",
        enable_console_output=True,
        enable_file_output=True
    )
    
    print(f"日志记录器创建成功，会话ID: {logger.session_id}")
    
    # 2. 测试开始交易会话
    print("\n2. 开始交易会话...")
    
    symbol = "600519"
    date = datetime.now().strftime("%Y-%m-%d")
    
    session_id = logger.start_trading_session(
        symbol=symbol,
        date=date,
        context={
            "market_condition": "震荡市",
            "strategy": "价值投资",
            "risk_level": "中等"
        }
    )
    
    print(f"交易会话已开始，会话ID: {session_id}")
    
    # 3. 测试记录分析步骤
    print("\n3. 记录分析步骤...")
    
    # 技术分析步骤
    step1_id = logger.log_analysis_step(
        agent_type=AgentType.TECHNICAL_ANALYST,
        input_data={
            "price_data": "最近20天价格数据",
            "volume_data": "成交量数据",
            "indicators": ["MA5", "MA20", "RSI", "MACD"]
        },
        analysis_process="基于技术指标进行技术面分析，重点关注价格趋势和成交量变化",
        conclusion="技术面显示股价处于上升通道，但RSI指标显示轻微超买",
        confidence=0.75,
        reasoning=[
            "MA5上穿MA20形成金叉，显示短期上涨趋势",
            "MACD柱状图转正，动能增强",
            "RSI值达到72，接近超买区域",
            "成交量相比前期有所放大，资金关注度提升"
        ],
        supporting_data={
            "MA5": 45.67,
            "MA20": 44.23,
            "RSI": 72.1,
            "MACD": 0.85,
            "volume_ratio": 1.35
        }
    )
    
    print(f"技术分析步骤记录完成，步骤ID: {step1_id}")
    
    # 基本面分析步骤
    step2_id = logger.log_analysis_step(
        agent_type=AgentType.FUNDAMENTAL_ANALYST,
        input_data={
            "financial_data": "最新财报数据",
            "industry_data": "行业对比数据",
            "valuation_metrics": ["PE", "PB", "ROE"]
        },
        analysis_process="分析公司基本面，包括财务状况、盈利能力和估值水平",
        conclusion="基本面良好，财务稳健，但估值偏高需要谨慎",
        confidence=0.82,
        reasoning=[
            "营收增长率保持在15%以上，盈利能力稳定",
            "ROE达到18.5%，高于行业平均水平",
            "负债率控制在合理范围内，财务风险较低",
            "当前PE为35倍，略高于历史平均水平"
        ],
        supporting_data={
            "revenue_growth": 0.156,
            "roe": 0.185,
            "debt_ratio": 0.35,
            "pe_ratio": 35.2,
            "industry_avg_pe": 28.5
        }
    )
    
    print(f"基本面分析步骤记录完成，步骤ID: {step2_id}")
    
    # 情绪分析步骤
    step3_id = logger.log_analysis_step(
        agent_type=AgentType.SENTIMENT_ANALYST,
        input_data={
            "news_data": "最近7天相关新闻",
            "social_media": "社交媒体讨论热度",
            "analyst_reports": "券商研报"
        },
        analysis_process="分析市场情绪和投资者预期，结合新闻面和社媒热度",
        conclusion="市场情绪偏向乐观，但需要注意短期波动风险",
        confidence=0.68,
        reasoning=[
            "相关新闻整体偏正面，公司发展前景被看好",
            "社交媒体讨论热度上升，投资者关注度提高",
            "多家券商维持买入评级，目标价上调",
            "市场整体情绪谨慎，需要关注外部环境影响"
        ],
        supporting_data={
            "news_sentiment_score": 0.72,
            "social_media_mentions": 1250,
            "analyst_rating": "买入",
            "target_price": 52.0,
            "current_price": 45.8
        }
    )
    
    print(f"情绪分析步骤记录完成，步骤ID: {step3_id}")
    
    # 4. 测试记录决策点
    print("\n4. 记录决策点...")
    
    decision1_id = logger.log_decision_point(
        context="综合三个分析师的意见，需要做出买卖决策",
        options=[
            {"action": "BUY", "volume": 1000, "reason": "技术面和基本面均支持上涨"},
            {"action": "HOLD", "volume": 0, "reason": "等待更好的入场时机"},
            {"action": "SELL", "volume": 500, "reason": "估值偏高，获利了结"}
        ],
        chosen_option={"action": "BUY", "volume": 800, "price": 45.8},
        rationale="虽然估值略高，但基本面良好且技术面显示上涨趋势，适量买入",
        risk_assessment={
            "market_risk": "中等",
            "company_risk": "低",
            "liquidity_risk": "低",
            "max_loss": "-8%",
            "expected_return": "12%"
        },
        confidence=0.73
    )
    
    print(f"决策点记录完成，决策ID: {decision1_id}")
    
    # 风险管理决策
    decision2_id = logger.log_decision_point(
        context="风控检查：评估仓位风险和止损策略",
        options=[
            {"action": "SET_STOP_LOSS", "level": 0.05, "reason": "设置5%止损"},
            {"action": "SET_STOP_LOSS", "level": 0.08, "reason": "设置8%止损"},
            {"action": "NO_STOP_LOSS", "reason": "长期持有，不设止损"}
        ],
        chosen_option={"action": "SET_STOP_LOSS", "level": 0.06, "price": 43.15},
        rationale="考虑到当前市场波动性，设置6%的止损位较为合理",
        risk_assessment={
            "position_size_pct": 8.0,
            "portfolio_risk": "可控",
            "correlation_risk": "低",
            "stop_loss_price": 43.15
        },
        confidence=0.85
    )
    
    print(f"风控决策点记录完成，决策ID: {decision2_id}")
    
    # 5. 测试结束交易会话
    print("\n5. 结束交易会话...")
    
    final_decision = {
        "action": "BUY",
        "symbol": symbol,
        "volume": 800,
        "price": 45.8,
        "stop_loss": 43.15,
        "target_price": 52.0,
        "holding_period": "1-3个月",
        "confidence": 0.73,
        "overall_rationale": "综合技术面、基本面和情绪面分析，该股票具有上涨潜力，适合中短期投资"
    }
    
    performance_data = {
        "analysis_time_minutes": 15.5,
        "data_quality_score": 0.88,
        "model_consensus": 0.73,
        "risk_score": 0.42
    }
    
    session_summary = logger.end_trading_session(
        final_decision=final_decision,
        performance_data=performance_data
    )
    
    print("交易会话结束，生成摘要:")
    print(f"  会话ID: {session_summary['session_id']}")
    print(f"  股票代码: {session_summary['symbol']}")
    print(f"  分析时长: {session_summary['duration_minutes']:.1f} 分钟")
    print(f"  分析步骤数: {session_summary['total_analysis_steps']}")
    print(f"  决策点数: {session_summary['total_decision_points']}")
    print(f"  平均置信度: {session_summary['average_confidence']:.2f}")
    print(f"  智能体统计: {session_summary['agent_statistics']}")
    
    # 6. 测试历史记录获取
    print("\n6. 获取历史会话记录...")
    
    try:
        history = logger.get_session_history()
        print(f"找到 {len(history)} 个历史会话:")
        for record in history[:3]:  # 只显示前3个
            print(f"  {record['session_id']} - {record['symbol']} ({record['date']})")
    except Exception as e:
        print(f"获取历史记录失败: {e}")
    
    # 7. 测试新会话
    print("\n7. 测试创建新会话...")
    
    new_session_id = logger.start_trading_session("000001", date)
    print(f"新会话创建成功: {new_session_id}")
    
    # 简单记录一个分析步骤
    logger.log_analysis_step(
        agent_type=AgentType.TRADER,
        input_data={"signal": "买入信号"},
        analysis_process="快速交易信号分析",
        conclusion="建议买入",
        confidence=0.65,
        reasoning=["价格突破阻力位", "成交量放大确认"],
        supporting_data={"breakout_price": 12.5, "volume": 1500000}
    )
    
    # 结束新会话
    logger.end_trading_session(
        final_decision={"action": "BUY", "volume": 1000},
        performance_data={"quick_analysis": True}
    )
    
    print("新会话测试完成")
    
    print("\n可解释性日志记录器测试完成!")


if __name__ == "__main__":
    test_interpretable_logger()