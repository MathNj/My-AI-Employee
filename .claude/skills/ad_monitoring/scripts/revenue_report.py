#!/usr/bin/env python3
"""
Generate Revenue Impact Report

Analyzes ad monitoring logs to generate revenue impact reports.

Usage:
    python revenue_report.py --days 7 --conversion-rate 0.5
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add ad_management to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "ad_management"))

try:
    import pandas as pd
    from dashboard import calculate_enhanced_revenue_metrics
except ImportError as e:
    print(f"Error importing dependencies: {e}")
    print("Make sure you're running from the ad_management directory or dependencies are installed.")
    sys.exit(1)


def get_revenue_impact(days: int = 7, conversion_rate: float = 0.5, log_file: str = "global/Ad_Status_Log.xlsx") -> dict:
    """
    Generate revenue impact report for specified period.

    Args:
        days: Number of days to analyze
        conversion_rate: Daily conversion rate (default: 0.5)
        log_file: Path to log file

    Returns:
        {
            "period_days": int,
            "total_ads_monitored": int,
            "currently_offline": int,
            "total_revenue_loss": float,
            "top_impact_products": list,
            "recommendations": list
        }
    """
    try:
        df = pd.read_excel(log_file)
    except Exception as e:
        return {
            "error": f"Could not load log file: {e}",
            "log_file": log_file,
            "period_days": days,
            "total_ads_monitored": 0,
            "currently_offline": 0,
            "total_revenue_loss": 0.0,
            "top_impact_products": [],
            "recommendations": []
        }

    if df.empty:
        return {
            "period_days": days,
            "total_ads_monitored": 0,
            "currently_offline": 0,
            "total_revenue_loss": 0.0,
            "top_impact_products": [],
            "recommendations": []
        }

    # Filter by date
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    cutoff = datetime.now() - timedelta(days=days)
    df_filtered = df[df["Timestamp"] >= cutoff].copy()

    if df_filtered.empty:
        return {
            "period_days": days,
            "total_ads_monitored": 0,
            "currently_offline": 0,
            "total_revenue_loss": 0.0,
            "top_impact_products": [],
            "recommendations": []
        }

    # Calculate metrics
    try:
        count_oos, total_days, total_loss, current_oos_list, all_ad_metrics, *_ = calculate_enhanced_revenue_metrics(df_filtered, conversion_rate)
    except Exception as e:
        return {
            "error": f"Could not calculate metrics: {e}",
            "period_days": days,
            "total_ads_monitored": 0,
            "currently_offline": 0,
            "total_revenue_loss": 0.0,
            "top_impact_products": [],
            "recommendations": []
        }

    # Generate recommendations
    recommendations = []
    for m in all_ad_metrics[:5]:
        if m["status"] == "offline":
            recommendations.append(
                f"Pause {m['ad_name']} - ${m['revenue_loss']} loss, {m['days_out']}d downtime"
            )

    return {
        "period_days": days,
        "total_ads_monitored": len(all_ad_metrics),
        "currently_offline": count_oos,
        "total_revenue_loss": round(total_loss, 2),
        "top_impact_products": all_ad_metrics[:10],
        "recommendations": recommendations,
        "conversion_rate": conversion_rate,
        "log_file": log_file
    }


def main():
    parser = argparse.ArgumentParser(
        description="Generate revenue impact report"
    )

    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Number of days to analyze (default: 7)"
    )

    parser.add_argument(
        "--conversion-rate",
        type=float,
        default=0.5,
        help="Daily conversion rate (default: 0.5)"
    )

    parser.add_argument(
        "--log-file",
        default="global/Ad_Status_Log.xlsx",
        help="Path to log file (default: global/Ad_Status_Log.xlsx)"
    )

    args = parser.parse_args()

    # Generate report
    report = get_revenue_impact(
        days=args.days,
        conversion_rate=args.conversion_rate,
        log_file=args.log_file
    )

    # Output JSON
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
