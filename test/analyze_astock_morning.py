#!/usr/bin/env python3
"""
A股上午行情分析（真实数据优先）
- 复用 test/analyze_astock_realtime.py 的 RealTimeAStockAnalyzer
- 生成 test/astock_morning_analysis.md 与 test/astock_morning_data.json
- 不改动项目源码，仅新增 test 脚本
"""

import sys
import json
from pathlib import Path
from datetime import datetime, time

# 允许从 test 目录内互相导入
sys.path.insert(0, str(Path(__file__).parent))

from analyze_astock_realtime import RealTimeAStockAnalyzer  # noqa: E402


def summarize(indices, sentiment):
    avg_chg = 0.0
    if indices:
        avg_chg = sum(v.get("change_pct", 0) for v in indices.values()) / len(indices)

    up_ratio = 0.0
    if sentiment and "market_structure" in sentiment:
        ms = sentiment["market_structure"]
        total = ms.get("total_stocks", 0) or 1
        up_ratio = ms.get("up_count", 0) / total

    net_sh = 0.0
    if sentiment and "northbound_flow" in sentiment:
        net_sh = float(sentiment["northbound_flow"].get("sh_net_flow", 0))

    trend = "震荡"
    if avg_chg > 0.2:
        trend = "上涨"
    elif avg_chg < -0.2:
        trend = "下跌"

    if avg_chg > 0.5 and up_ratio > 0.55 and net_sh > 0:
        advice = "适度加仓（分批，关注强势板块龙头）"
        pos = "60-70%"
    elif avg_chg < -0.5 and up_ratio < 0.45 and net_sh < 0:
        advice = "降仓防守（控制风险，观察反弹信号）"
        pos = "30-40%"
    else:
        advice = "中性观望（高抛低吸为主，控制单次风险）"
        pos = "45-55%"

    return {
        "avg_change_pct": avg_chg,
        "up_ratio": up_ratio,
        "northbound_sh": net_sh,
        "trend": trend,
        "advice": advice,
        "position_suggestion": pos,
    }


def main():
    now = datetime.now()
    am_flag = time(9, 15) <= now.time() <= time(12, 0)

    analyzer = RealTimeAStockAnalyzer()
    data = analyzer.generate_real_analysis_report()

    indices = data.get("indices_data", {})
    sectors = data.get("sectors_data", {})
    sentiment = data.get("sentiment_data", {})
    stock = data.get("stock_data", {})

    summary = summarize(indices, sentiment)

    report_path = Path(__file__).parent / "astock_morning_analysis.md"
    with report_path.open("w", encoding="utf-8") as f:
        f.write(f"# A股上午行情分析报告\n\n")
        f.write(f"**分析时间**: {now.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**时段**: {'上午(集合竞价+连续竞价)' if am_flag else '非上午时段，以下为最新实时快照'}\n\n")
        f.write("## 主要指数\n")
        for code, v in indices.items():
            icon = "📈" if v.get("change_pct", 0) > 0 else "📉" if v.get("change_pct", 0) < 0 else "➡️"
            f.write(
                f"- {v.get('name', code)}({code.upper()}): {icon} {v.get('change_pct', 0):+.2f}% "
                f" 收{v.get('close', 0):.2f} 开{v.get('open', 0):.2f} 高{v.get('high', 0):.2f} 低{v.get('low', 0):.2f}\n"
            )
        f.write("\n## 市场结构与资金\n")
        ms = sentiment.get("market_structure", {})
        f.write(
            f"- 上涨: {ms.get('up_count', 0)}  下跌: {ms.get('down_count', 0)}  总数: {ms.get('total_stocks', 0)}  "
            f"涨停: {ms.get('limit_up_count', 0)}  跌停: {ms.get('limit_down_count', 0)}\n"
        )
        nb = sentiment.get("northbound_flow", {})
        if nb:
            f.write(f"- 北向资金(沪): {nb.get('sh_net_flow', 0):,.0f} 万元（{nb.get('date','今日')}）\n")
        f.write(
            f"\n## 上午结论\n- 趋势: {summary['trend']}\n"
            f"- 指数平均涨跌: {summary['avg_change_pct']:+.2f}%\n"
            f"- 上涨占比: {summary['up_ratio']:.1%}\n"
            f"- 建议: {summary['advice']}\n"
            f"- 建议仓位: {summary['position_suggestion']}\n"
        )
        if sectors:
            f.write("\n## 关注板块（实时/快照）\n")
            top = sorted(sectors.items(), key=lambda kv: kv[1].get("change_pct", 0), reverse=True)[:6]
            for name, s in top:
                f.write(f"- {name}: {s.get('change_pct', 0):+.2f}%  成交额≈{s.get('turnover', 0)/1e8:.0f}亿\n")

        if stock:
            f.write(
                f"\n## 重点个股（样例） - {stock.get('name','N/A')}({stock.get('symbol','')})\n"
                f"- 现价: {stock.get('current_price',0):.2f}  涨跌: {stock.get('change_pct',0):+.2f}%\n"
            )

        f.write(
            "\n---\n"
            "免责声明：以上为基于可获取的实时/快照数据生成的上午盘参考，不构成任何投资建议，请根据自身风险承受能力决策。\n"
        )

    out_json = Path(__file__).parent / "astock_morning_data.json"
    with out_json.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "generated_at": now.isoformat(),
                "session": "AM" if am_flag else "LATEST",
                "indices": indices,
                "sectors": sectors,
                "sentiment": sentiment,
                "stock_sample": stock,
                "summary": summary,
            },
            f,
            ensure_ascii=False,
            indent=2,
            default=str,
        )

    print("✅ 上午分析完成")
    print(f"📄 报告: {report_path}")
    print(f"📊 数据:  {out_json}")


if __name__ == "__main__":
    main()


