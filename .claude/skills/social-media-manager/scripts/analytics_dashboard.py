#!/usr/bin/env python3
"""
Social media analytics dashboard and reporting

Usage:
    # Daily analytics
    python analytics_dashboard.py --period today

    # Weekly summary
    python analytics_dashboard.py --period week

    # Platform comparison
    python analytics_dashboard.py --compare-platforms

    # Specific platform
    python analytics_dashboard.py --platform linkedin --period week

    # Export to file
    python analytics_dashboard.py --period month --export json --output report.json
"""

import argparse
import logging
from datetime import datetime, timedelta
from pathlib import Path
import json
import os
from typing import Dict, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mock data structure - replace with actual MCP calls
MOCK_DATA = {
    'linkedin': {
        'followers': 1250,
        'posts_this_period': 12,
        'impressions': 15000,
        'engagement': 450,
        'clicks': 120,
        'engagement_rate': 3.0,
        'top_post': {
            'id': 'LI_001',
            'content': 'Exciting news! We've reached 1000 customers...',
            'impressions': 3500,
            'likes': 85,
            'comments': 12,
            'shares': 8,
        }
    },
    'facebook': {
        'followers': 890,
        'posts_this_period': 10,
        'impressions': 12000,
        'engagement': 380,
        'clicks': 95,
        'engagement_rate': 3.2,
        'top_post': {
            'id': 'FB_001',
            'content': 'Big announcement from the team...',
            'impressions': 2800,
            'likes': 65,
            'comments': 18,
            'shares': 12,
        }
    },
    'instagram': {
        'followers': 2100,
        'posts_this_period': 15,
        'impressions': 25000,
        'engagement': 1250,
        'clicks': 220,
        'engagement_rate': 5.0,
        'top_post': {
            'id': 'IG_001',
            'content': 'Behind the scenes at our new office...',
            'impressions': 5000,
            'likes': 280,
            'comments': 45,
            'shares': 35,
        }
    },
    'twitter': {
        'followers': 750,
        'posts_this_period': 25,
        'impressions': 8000,
        'engagement': 240,
        'clicks': 60,
        'engagement_rate': 3.0,
        'top_post': {
            'id': 'TW_001',
            'content': '🚀 Launched: AutoFlow 2.0...',
            'impressions': 1200,
            'likes': 45,
            'comments': 8,
            'shares': 15,
        }
    }
}


def load_env():
    """Load environment variables"""
    env_file = Path(__file__).parent.parent.parent.parent / '.env'
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value


def get_period_dates(period: str) -> tuple:
    """Get start and end dates for period"""
    end_date = datetime.now()

    if period == 'today':
        start_date = end_date.replace(hour=0, minute=0, second=0)
    elif period == 'week':
        start_date = end_date - timedelta(days=7)
    elif period == 'month':
        start_date = end_date - timedelta(days=30)
    elif period == 'quarter':
        start_date = end_date - timedelta(days=90)
    else:
        raise ValueError(f"Unknown period: {period}")

    return start_date, end_date


def fetch_platform_analytics(platform: str, start_date: datetime, end_date: datetime) -> dict:
    """Fetch analytics for specific platform"""
    logger.info(f"Fetching {platform} analytics from {start_date.date()} to {end_date.date()}")

    # TODO: Replace with actual MCP calls
    # For now, return mock data
    data = MOCK_DATA.get(platform, {})

    return {
        'platform': platform,
        'period': {
            'start': start_date.isoformat(),
            'end': end_date.isoformat()
        },
        'metrics': data
    }


def calculate_totals(analytics: Dict[str, dict]) -> dict:
    """Calculate total metrics across all platforms"""
    totals = {
        'total_followers': 0,
        'total_posts': 0,
        'total_impressions': 0,
        'total_engagement': 0,
        'total_clicks': 0,
        'avg_engagement_rate': 0,
    }

    platform_count = len(analytics)

    for platform, data in analytics.items():
        metrics = data.get('metrics', {})
        totals['total_followers'] += metrics.get('followers', 0)
        totals['total_posts'] += metrics.get('posts_this_period', 0)
        totals['total_impressions'] += metrics.get('impressions', 0)
        totals['total_engagement'] += metrics.get('engagement', 0)
        totals['total_clicks'] += metrics.get('clicks', 0)
        totals['avg_engagement_rate'] += metrics.get('engagement_rate', 0)

    if platform_count > 0:
        totals['avg_engagement_rate'] /= platform_count

    return totals


def compare_platforms(analytics: Dict[str, dict]) -> List[dict]:
    """Compare performance across platforms"""
    comparison = []

    for platform, data in analytics.items():
        metrics = data.get('metrics', {})
        comparison.append({
            'platform': platform,
            'followers': metrics.get('followers', 0),
            'engagement_rate': metrics.get('engagement_rate', 0),
            'impressions': metrics.get('impressions', 0),
            'posts': metrics.get('posts_this_period', 0),
        })

    # Sort by engagement rate
    comparison.sort(key=lambda x: x['engagement_rate'], reverse=True)

    return comparison


def generate_recommendations(analytics: Dict[str, dict], totals: dict) -> List[str]:
    """Generate recommendations based on analytics"""
    recommendations = []

    # Overall engagement
    avg_engagement = totals['avg_engagement_rate']
    if avg_engagement < 2.0:
        recommendations.append("⚠️ Low engagement rate (< 2%). Consider posting more engaging content or at optimal times.")
    elif avg_engagement > 5.0:
        recommendations.append("✅ Excellent engagement rate (> 5%)! Keep up the good work.")

    # Platform-specific
    for platform, data in analytics.items():
        metrics = data.get('metrics', {})
        engagement_rate = metrics.get('engagement_rate', 0)

        if engagement_rate < 1.5:
            recommendations.append(f"📉 {platform.capitalize()} engagement is low. Review content strategy.")
        elif engagement_rate > 5.0:
            recommendations.append(f"📈 {platform.capitalize()} performing excellently! Analyze what's working.")

    # Posting frequency
    total_posts = totals['total_posts']
    if total_posts < 10:
        recommendations.append("📅 Low posting frequency. Consider increasing to 3-5 posts per platform per week.")

    # Top platform
    comparison = compare_platforms(analytics)
    if comparison:
        top_platform = comparison[0]
        recommendations.append(f"🏆 Top performer: {top_platform['platform'].capitalize()} with {top_platform['engagement_rate']:.1f}% engagement")

    return recommendations


def generate_text_report(analytics: Dict[str, dict], totals: dict, comparison: List[dict], recommendations: List[str]) -> str:
    """Generate text report"""
    report = """
╔════════════════════════════════════════════════════════════╗
║          SOCIAL MEDIA ANALYTICS DASHBOARD                 ║
╚════════════════════════════════════════════════════════════╝

"""

    # Summary
    report += "## SUMMARY\n\n"
    report += f"Total Followers:      {totals['total_followers']:,}\n"
    report += f"Posts Published:      {totals['total_posts']}\n"
    report += f"Total Impressions:    {totals['total_impressions']:,}\n"
    report += f"Total Engagement:     {totals['total_engagement']:,}\n"
    report += f"Avg Engagement Rate:  {totals['avg_engagement_rate']:.2f}%\n"
    report += f"Total Clicks:         {totals['total_clicks']:,}\n\n"

    # Platform comparison
    report += "## PLATFORM COMPARISON\n\n"
    report += f"{'Platform':<12} {'Followers':<12} {'Posts':<8} {'Engagement':<12} {'Impressions':<12}\n"
    report += "-" * 60 + "\n"
    for item in comparison:
        report += f"{item['platform'].capitalize():<12} "
        report += f"{item['followers']:<12,} "
        report += f"{item['posts']:<8} "
        report += f"{item['engagement_rate']:.1f}%{'':<8} "
        report += f"{item['impressions']:<12,}\n"

    report += "\n"

    # Top posts
    report += "## TOP PERFORMING POSTS\n\n"
    for platform, data in analytics.items():
        metrics = data.get('metrics', {})
        top_post = metrics.get('top_post', {})

        if top_post:
            report += f"{platform.capitalize()}:\n"
            content = top_post.get('content', 'N/A')[:60]
            report += f"  Content: \"{content}...\"\n"
            report += f"  Impressions: {top_post.get('impressions', 0):,}\n"
            report += f"  Likes: {top_post.get('likes', 0)} | "
            report += f"Comments: {top_post.get('comments', 0)} | "
            report += f"Shares: {top_post.get('shares', 0)}\n\n"

    # Recommendations
    report += "## RECOMMENDATIONS\n\n"
    for rec in recommendations:
        report += f"• {rec}\n"

    report += "\n"
    report += "─" * 60 + "\n"
    report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    report += "─" * 60 + "\n"

    return report


def generate_markdown_report(analytics: Dict[str, dict], totals: dict, comparison: List[dict], recommendations: List[str], period: str) -> str:
    """Generate markdown report"""
    start_date, end_date = get_period_dates(period)

    report = f"""# Social Media Analytics Report

**Period:** {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Executive Summary

| Metric | Value |
|--------|-------|
| Total Followers | {totals['total_followers']:,} |
| Posts Published | {totals['total_posts']} |
| Total Impressions | {totals['total_impressions']:,} |
| Total Engagement | {totals['total_engagement']:,} |
| Avg Engagement Rate | {totals['avg_engagement_rate']:.2f}% |
| Total Clicks | {totals['total_clicks']:,} |

---

## Platform Performance

| Platform | Followers | Posts | Engagement Rate | Impressions |
|----------|-----------|-------|-----------------|-------------|
"""

    for item in comparison:
        report += f"| {item['platform'].capitalize()} | {item['followers']:,} | {item['posts']} | {item['engagement_rate']:.1f}% | {item['impressions']:,} |\n"

    report += "\n---\n\n## Top Performing Posts\n\n"

    for platform, data in analytics.items():
        metrics = data.get('metrics', {})
        top_post = metrics.get('top_post', {})

        if top_post:
            report += f"### {platform.capitalize()}\n\n"
            report += f"**Content:** \"{top_post.get('content', 'N/A')[:100]}...\"\n\n"
            report += f"- **Impressions:** {top_post.get('impressions', 0):,}\n"
            report += f"- **Likes:** {top_post.get('likes', 0)}\n"
            report += f"- **Comments:** {top_post.get('comments', 0)}\n"
            report += f"- **Shares:** {top_post.get('shares', 0)}\n\n"

    report += "---\n\n## Recommendations\n\n"

    for rec in recommendations:
        report += f"- {rec}\n"

    report += "\n---\n\n*Generated by social-media-manager skill*\n"

    return report


def export_json(analytics: Dict[str, dict], totals: dict, comparison: List[dict], recommendations: List[str], output_path: Path):
    """Export analytics as JSON"""
    data = {
        'generated_at': datetime.now().isoformat(),
        'summary': totals,
        'platforms': analytics,
        'comparison': comparison,
        'recommendations': recommendations,
    }

    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)

    logger.info(f"Exported JSON to: {output_path}")


def export_csv(comparison: List[dict], output_path: Path):
    """Export comparison as CSV"""
    import csv

    with open(output_path, 'w', newline='') as f:
        fieldnames = ['platform', 'followers', 'posts', 'engagement_rate', 'impressions']
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()
        for row in comparison:
            writer.writerow(row)

    logger.info(f"Exported CSV to: {output_path}")


def save_report_to_vault(report: str, period: str):
    """Save report to Obsidian vault"""
    vault_path = Path(os.getenv('VAULT_PATH', 'C:/Users/Najma-LP/Desktop/My Vault/AI_Employee_Vault'))
    logs_dir = vault_path / 'Logs'
    logs_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime('%Y-%m-%d')
    filename = f"Social_Media_Summary_{timestamp}_{period}.md"
    filepath = logs_dir / filename

    filepath.write_text(report)
    logger.info(f"Report saved to: {filepath}")

    return filepath


def main():
    parser = argparse.ArgumentParser(description='Social media analytics dashboard')
    parser.add_argument('--period', default='week',
                       choices=['today', 'week', 'month', 'quarter'],
                       help='Time period for analytics')
    parser.add_argument('--platform', help='Specific platform to analyze')
    parser.add_argument('--compare-platforms', action='store_true',
                       help='Compare all platforms')
    parser.add_argument('--export', choices=['json', 'csv', 'md'],
                       help='Export format')
    parser.add_argument('--output', help='Output file path')

    args = parser.parse_args()

    load_env()

    # Get date range
    start_date, end_date = get_period_dates(args.period)

    # Determine platforms to analyze
    if args.platform:
        platforms = [args.platform]
    else:
        platforms = ['linkedin', 'facebook', 'instagram', 'twitter']

    # Fetch analytics
    logger.info(f"Fetching analytics for {args.period}...")
    analytics = {}
    for platform in platforms:
        data = fetch_platform_analytics(platform, start_date, end_date)
        analytics[platform] = data

    # Calculate metrics
    totals = calculate_totals(analytics)
    comparison = compare_platforms(analytics)
    recommendations = generate_recommendations(analytics, totals)

    # Generate report
    if args.export == 'json':
        if not args.output:
            args.output = f"analytics_{args.period}_{datetime.now().strftime('%Y%m%d')}.json"
        export_json(analytics, totals, comparison, recommendations, Path(args.output))
    elif args.export == 'csv':
        if not args.output:
            args.output = f"analytics_{args.period}_{datetime.now().strftime('%Y%m%d')}.csv"
        export_csv(comparison, Path(args.output))
    elif args.export == 'md':
        report = generate_markdown_report(analytics, totals, comparison, recommendations, args.period)
        if args.output:
            Path(args.output).write_text(report)
            logger.info(f"Report saved to: {args.output}")
        else:
            filepath = save_report_to_vault(report, args.period)
            logger.info(f"Report saved to vault: {filepath}")
    else:
        # Display text report
        report = generate_text_report(analytics, totals, comparison, recommendations)
        print(report)

        # Also save to vault
        md_report = generate_markdown_report(analytics, totals, comparison, recommendations, args.period)
        save_report_to_vault(md_report, args.period)


if __name__ == '__main__':
    main()
