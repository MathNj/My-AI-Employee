#!/usr/bin/env python3
"""
Audit subscriptions for cost optimization

Usage:
    # Full subscription audit
    python audit_subscriptions.py

    # Check for unused (>30 days)
    python audit_subscriptions.py --unused-days 30

    # Generate recommendations
    python audit_subscriptions.py --recommend

    # Export to file
    python audit_subscriptions.py --export json --output subscriptions.json
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

# From Requirements.md - Subscription patterns
SUBSCRIPTION_PATTERNS = {
    'netflix.com': 'Netflix',
    'spotify.com': 'Spotify',
    'adobe.com': 'Adobe Creative Cloud',
    'notion.so': 'Notion',
    'slack.com': 'Slack',
    'github.com': 'GitHub',
    'zoom.us': 'Zoom',
    'dropbox.com': 'Dropbox',
    'google.com/workspace': 'Google Workspace',
    'microsoft.com/microsoft-365': 'Microsoft 365',
    'xero.com': 'Xero',
    'asana.com': 'Asana',
    'trello.com': 'Trello',
    'monday.com': 'Monday.com',
    'figma.com': 'Figma',
    'canva.com': 'Canva Pro',
    'mailchimp.com': 'Mailchimp',
    'hubspot.com': 'HubSpot',
}

# Duplicate functionality groups
DUPLICATE_GROUPS = [
    {
        'name': 'Project Management',
        'services': ['Asana', 'Monday.com', 'Trello', 'ClickUp'],
        'recommendation': 'Choose one primary tool'
    },
    {
        'name': 'Cloud Storage',
        'services': ['Dropbox', 'Box', 'Google Drive', 'OneDrive', 'iCloud+'],
        'recommendation': 'Consolidate to one or two services'
    },
    {
        'name': 'Communication',
        'services': ['Slack', 'Microsoft Teams', 'Discord'],
        'recommendation': 'Use one primary communication platform'
    },
    {
        'name': 'Video Conferencing',
        'services': ['Zoom', 'Google Meet', 'Microsoft Teams'],
        'recommendation': 'Consolidate to one service'
    },
]


def load_env():
    """Load environment variables"""
    env_file = Path(__file__).parent.parent.parent.parent / '.env'
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value


def get_transactions_from_xero(start_date: datetime, end_date: datetime):
    """Get transactions from xero-integrator"""
    logger.info(f"Fetching transactions from {start_date.date()} to {end_date.date()}")

    # TODO: Call xero-integrator skill
    # For now, return mock data
    return [
        {
            'id': 'TX001',
            'date': datetime(2026, 1, 5),
            'description': 'Netflix subscription',
            'vendor': 'netflix.com',
            'amount': -15.99,
            'category': 'Entertainment'
        },
        {
            'id': 'TX002',
            'date': datetime(2026, 1, 6),
            'description': 'Notion team plan',
            'vendor': 'notion.so',
            'amount': -15.00,
            'category': 'Software & Subscriptions'
        },
        {
            'id': 'TX003',
            'date': datetime(2026, 1, 7),
            'description': 'Adobe Creative Cloud',
            'vendor': 'adobe.com',
            'amount': -54.99,
            'category': 'Software & Subscriptions'
        },
        {
            'id': 'TX004',
            'date': datetime(2026, 1, 8),
            'description': 'Slack workspace',
            'vendor': 'slack.com',
            'amount': -40.00,
            'category': 'Software & Subscriptions'
        },
        {
            'id': 'TX005',
            'date': datetime(2026, 1, 9),
            'description': 'GitHub Team',
            'vendor': 'github.com',
            'amount': -21.00,
            'category': 'Software & Subscriptions'
        },
        {
            'id': 'TX006',
            'date': datetime(2026, 1, 10),
            'description': 'Xero accounting',
            'vendor': 'xero.com',
            'amount': -35.00,
            'category': 'Software & Subscriptions'
        },
    ]


def identify_subscriptions(transactions: List[Dict]) -> List[Dict]:
    """Identify subscription charges from transactions"""
    subscriptions = {}

    for transaction in transactions:
        description = transaction.get('description', '').lower()
        vendor = transaction.get('vendor', '').lower()

        # Check against patterns
        for pattern, name in SUBSCRIPTION_PATTERNS.items():
            if pattern in description or pattern in vendor:
                if name not in subscriptions:
                    subscriptions[name] = {
                        'name': name,
                        'pattern': pattern,
                        'charges': [],
                        'total_amount': 0,
                    }

                subscriptions[name]['charges'].append(transaction)
                subscriptions[name]['total_amount'] += abs(transaction['amount'])

    # Calculate frequency and monthly cost
    for sub in subscriptions.values():
        if len(sub['charges']) >= 2:
            # Calculate average interval
            dates = sorted([c['date'] for c in sub['charges']])
            intervals = [(dates[i+1] - dates[i]).days for i in range(len(dates)-1)]
            avg_interval = sum(intervals) / len(intervals)

            if 25 <= avg_interval <= 35:
                sub['frequency'] = 'monthly'
                sub['monthly_cost'] = sub['total_amount'] / len(sub['charges'])
            elif 85 <= avg_interval <= 95:
                sub['frequency'] = 'quarterly'
                sub['monthly_cost'] = (sub['total_amount'] / len(sub['charges'])) / 3
            elif 350 <= avg_interval <= 380:
                sub['frequency'] = 'annual'
                sub['monthly_cost'] = (sub['total_amount'] / len(sub['charges'])) / 12
            else:
                sub['frequency'] = 'irregular'
                sub['monthly_cost'] = sub['total_amount'] / len(sub['charges'])
        else:
            sub['frequency'] = 'monthly'  # assume monthly
            sub['monthly_cost'] = abs(sub['charges'][0]['amount'])

        sub['annual_cost'] = sub['monthly_cost'] * 12

    return list(subscriptions.values())


def check_usage(subscription: Dict) -> Dict:
    """Check subscription usage patterns"""
    # TODO: Check actual usage data (login logs, API calls, etc.)
    # For now, return mock usage data

    # Simulate usage check
    usage_data = {
        'Netflix': {'last_activity': datetime.now() - timedelta(days=60), 'usage_pct': 0},
        'Notion': {'last_activity': datetime.now() - timedelta(days=45), 'usage_pct': 0},
        'Adobe Creative Cloud': {'last_activity': datetime.now() - timedelta(days=15), 'usage_pct': 15},
        'Slack': {'last_activity': datetime.now() - timedelta(days=7), 'usage_pct': 30},
        'GitHub': {'last_activity': datetime.now() - timedelta(days=1), 'usage_pct': 90},
        'Xero': {'last_activity': datetime.now() - timedelta(days=1), 'usage_pct': 100},
    }

    sub_name = subscription['name']
    usage = usage_data.get(sub_name, {
        'last_activity': datetime.now() - timedelta(days=5),
        'usage_pct': 50
    })

    days_inactive = (datetime.now() - usage['last_activity']).days

    return {
        'last_activity': usage['last_activity'],
        'days_inactive': days_inactive,
        'usage_percentage': usage['usage_pct'],
        'status': 'active' if days_inactive < 30 else 'unused'
    }


def find_duplicates(subscriptions: List[Dict]) -> List[Dict]:
    """Find subscriptions with duplicate functionality"""
    duplicates = []

    for group in DUPLICATE_GROUPS:
        active_in_group = [
            sub for sub in subscriptions
            if sub['name'] in group['services']
        ]

        if len(active_in_group) > 1:
            total_cost = sum(sub['monthly_cost'] for sub in active_in_group)
            min_cost = min(sub['monthly_cost'] for sub in active_in_group)

            duplicates.append({
                'group': group['name'],
                'subscriptions': [s['name'] for s in active_in_group],
                'total_monthly_cost': total_cost,
                'recommendation': group['recommendation'],
                'potential_savings_monthly': total_cost - min_cost,
                'potential_savings_annual': (total_cost - min_cost) * 12
            })

    return duplicates


def generate_recommendations(subscriptions: List[Dict], usage_data: Dict, duplicates: List[Dict], unused_days: int = 30) -> List[Dict]:
    """Generate cost optimization recommendations"""
    recommendations = []

    # Check for unused subscriptions
    for sub in subscriptions:
        usage = usage_data.get(sub['name'], {})
        days_inactive = usage.get('days_inactive', 0)

        if days_inactive > unused_days:
            recommendations.append({
                'type': 'cancel_unused',
                'subscription': sub['name'],
                'reason': f"No activity in {days_inactive} days",
                'action': 'Cancel subscription',
                'monthly_cost': sub['monthly_cost'],
                'annual_savings': sub['annual_cost'],
                'priority': 'high'
            })

    # Check for low usage
    for sub in subscriptions:
        usage = usage_data.get(sub['name'], {})
        usage_pct = usage.get('usage_percentage', 50)

        if usage_pct < 30 and usage_pct > 0:
            recommendations.append({
                'type': 'downgrade_tier',
                'subscription': sub['name'],
                'reason': f"Low usage ({usage_pct}% of features)",
                'action': 'Consider downgrading to cheaper tier',
                'monthly_cost': sub['monthly_cost'],
                'annual_savings': sub['annual_cost'] * 0.30,  # Estimate 30% savings
                'priority': 'medium'
            })

    # Check for duplicates
    for dup in duplicates:
        recommendations.append({
            'type': 'consolidate_duplicates',
            'group': dup['group'],
            'subscriptions': dup['subscriptions'],
            'reason': f"Duplicate functionality: {', '.join(dup['subscriptions'])}",
            'action': f"{dup['recommendation']}. Keep one, cancel others.",
            'monthly_cost': dup['total_monthly_cost'],
            'annual_savings': dup['potential_savings_annual'],
            'priority': 'medium'
        })

    # Sort by annual savings
    recommendations.sort(key=lambda x: x.get('annual_savings', 0), reverse=True)

    return recommendations


def generate_audit_report(subscriptions: List[Dict], usage_data: Dict, duplicates: List[Dict], recommendations: List[Dict]) -> str:
    """Generate comprehensive audit report"""
    total_monthly = sum(sub['monthly_cost'] for sub in subscriptions)
    total_annual = total_monthly * 12
    total_savings = sum(rec['annual_savings'] for rec in recommendations)

    report = f"""# Subscription Audit Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Summary

- **Total Subscriptions:** {len(subscriptions)}
- **Total Monthly Cost:** ${total_monthly:.2f}
- **Total Annual Cost:** ${total_annual:.2f}
- **Optimization Potential:** ${total_savings:.2f}/year

---

## Active Subscriptions

| Subscription | Monthly Cost | Annual Cost | Status | Usage |
|--------------|--------------|-------------|--------|-------|
"""

    for sub in sorted(subscriptions, key=lambda x: x['monthly_cost'], reverse=True):
        usage = usage_data.get(sub['name'], {})
        status_emoji = "🟢" if usage.get('status') == 'active' else "🔴"
        usage_pct = usage.get('usage_percentage', 0)

        report += f"| {sub['name']} | ${sub['monthly_cost']:.2f} | ${sub['annual_cost']:.2f} | {status_emoji} {usage.get('status', 'unknown').capitalize()} | {usage_pct}% |\n"

    report += "\n---\n\n"

    if duplicates:
        report += "## Duplicate Functionality Detected\n\n"
        for dup in duplicates:
            report += f"### {dup['group']}\n"
            report += f"- **Active:** {', '.join(dup['subscriptions'])}\n"
            report += f"- **Total Cost:** ${dup['total_monthly_cost']:.2f}/month\n"
            report += f"- **Recommendation:** {dup['recommendation']}\n"
            report += f"- **Potential Savings:** ${dup['potential_savings_annual']:.2f}/year\n\n"

        report += "---\n\n"

    report += "## Cost Optimization Recommendations\n\n"

    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            priority_emoji = "🔴" if rec['priority'] == 'high' else "🟡" if rec['priority'] == 'medium' else "🟢"
            report += f"{i}. {priority_emoji} **{rec.get('subscription', rec.get('group'))}**\n"
            report += f"   - **Type:** {rec['type'].replace('_', ' ').title()}\n"
            report += f"   - **Reason:** {rec['reason']}\n"
            report += f"   - **Action:** {rec['action']}\n"
            report += f"   - **Annual Savings:** ${rec['annual_savings']:.2f}\n\n"
    else:
        report += "*No optimization opportunities identified at this time.*\n\n"

    report += "---\n\n"
    report += f"## Total Potential Savings: ${total_savings:.2f}/year\n\n"
    report += "---\n\n"
    report += "*Generated by ceo-briefing-generator skill (subscription audit)*\n"

    return report


def main():
    parser = argparse.ArgumentParser(description='Audit subscriptions for cost optimization')
    parser.add_argument('--unused-days', type=int, default=30,
                       help='Flag subscriptions unused for this many days')
    parser.add_argument('--recommend', action='store_true',
                       help='Generate recommendations')
    parser.add_argument('--export', choices=['json', 'md'],
                       help='Export format')
    parser.add_argument('--output', help='Output file path')
    parser.add_argument('--period', default='quarter',
                       choices=['month', 'quarter', 'year'],
                       help='Time period to analyze')

    args = parser.parse_args()

    load_env()

    # Get date range
    end_date = datetime.now()
    if args.period == 'month':
        start_date = end_date - timedelta(days=30)
    elif args.period == 'quarter':
        start_date = end_date - timedelta(days=90)
    else:  # year
        start_date = end_date - timedelta(days=365)

    # Get transactions
    transactions = get_transactions_from_xero(start_date, end_date)

    # Identify subscriptions
    logger.info("Identifying subscriptions...")
    subscriptions = identify_subscriptions(transactions)
    logger.info(f"Found {len(subscriptions)} subscriptions")

    # Check usage for each
    logger.info("Checking usage patterns...")
    usage_data = {}
    for sub in subscriptions:
        usage_data[sub['name']] = check_usage(sub)

    # Find duplicates
    logger.info("Checking for duplicate functionality...")
    duplicates = find_duplicates(subscriptions)

    # Generate recommendations
    recommendations = []
    if args.recommend:
        logger.info("Generating recommendations...")
        recommendations = generate_recommendations(subscriptions, usage_data, duplicates, args.unused_days)

    # Generate report
    report = generate_audit_report(subscriptions, usage_data, duplicates, recommendations)

    # Export or print
    if args.export == 'json':
        output = {
            'generated': datetime.now().isoformat(),
            'subscriptions': subscriptions,
            'usage_data': {k: {**v, 'last_activity': v['last_activity'].isoformat()} for k, v in usage_data.items()},
            'duplicates': duplicates,
            'recommendations': recommendations,
            'summary': {
                'total_subscriptions': len(subscriptions),
                'total_monthly_cost': sum(s['monthly_cost'] for s in subscriptions),
                'total_annual_cost': sum(s['annual_cost'] for s in subscriptions),
                'total_potential_savings': sum(r['annual_savings'] for r in recommendations)
            }
        }

        if args.output:
            with open(args.output, 'w') as f:
                json.dump(output, f, indent=2)
            logger.info(f"Exported to {args.output}")
        else:
            print(json.dumps(output, indent=2))

    elif args.export == 'md':
        if args.output:
            Path(args.output).write_text(report)
            logger.info(f"Report saved to {args.output}")
        else:
            print(report)

    else:
        # Print to stdout
        print(report)

        # Also save to vault
        vault_path = Path(os.getenv('VAULT_PATH', 'C:/Users/Najma-LP/Desktop/My Vault/AI_Employee_Vault'))
        logs_dir = vault_path / 'Logs'
        logs_dir.mkdir(parents=True, exist_ok=True)

        filename = f"Subscription_Audit_{datetime.now().strftime('%Y-%m-%d')}.md"
        filepath = logs_dir / filename
        filepath.write_text(report)
        logger.info(f"Audit saved to: {filepath}")


if __name__ == '__main__':
    main()
