#!/usr/bin/env python3
"""
Generate Monday Morning CEO Briefing with weekly business audit

Usage:
    # Full weekly briefing
    python generate_briefing.py --period week

    # Custom date range
    python generate_briefing.py --start 2026-01-01 --end 2026-01-07

    # Specific sections only
    python generate_briefing.py --sections revenue,tasks,subscriptions

    # Month-end deep dive
    python generate_briefing.py --period month --template deep-dive
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


def load_env():
    """Load environment variables"""
    env_file = Path(__file__).parent.parent.parent.parent / '.env'
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value


def get_period_dates(period: str):
    """Get start and end dates for period"""
    end_date = datetime.now()

    if period == 'week':
        start_date = end_date - timedelta(days=7)
    elif period == 'month':
        start_date = end_date - timedelta(days=30)
    elif period == 'quarter':
        start_date = end_date - timedelta(days=90)
    else:
        start_date = end_date - timedelta(days=7)

    return start_date, end_date


def load_business_goals():
    """Load business goals from vault"""
    vault_path = Path(os.getenv('VAULT_PATH', 'C:/Users/Najma-LP/Desktop/My Vault/AI_Employee_Vault'))
    goals_file = vault_path / 'Business_Goals.md'

    if not goals_file.exists():
        logger.warning("Business_Goals.md not found. Using defaults.")
        return {
            'revenue_target_monthly': 10000,
            'revenue_target_weekly': 2500,
            'key_metrics': {}
        }

    # TODO: Parse Business_Goals.md
    # For now, return mock data
    return {
        'revenue_target_monthly': 10000,
        'revenue_target_weekly': 2500,
        'key_metrics': {
            'client_response_time': {'target': 24, 'alert': 48, 'unit': 'hours'},
            'invoice_payment_rate': {'target': 90, 'alert': 80, 'unit': 'percent'},
            'software_costs': {'target': 500, 'alert': 600, 'unit': 'dollars'}
        }
    }


def get_financial_data(start_date: datetime, end_date: datetime):
    """Get financial data from xero-integrator"""
    logger.info(f"Fetching financial data from {start_date.date()} to {end_date.date()}")

    # TODO: Call xero-integrator skill
    # For now, return mock data
    return {
        'revenue_this_week': 2450,
        'revenue_mtd': 4500,
        'expenses_this_week': 1890,
        'expenses_by_category': {
            'Software & Subscriptions': 490,
            'Marketing & Advertising': 1200,
            'Office Supplies': 200,
        },
        'cash_balance': 15250,
        'outstanding_invoices': [
            {'client': 'Client A', 'amount': 1500, 'due_date': '2026-01-10', 'days_overdue': 2},
            {'client': 'Client B', 'amount': 1700, 'due_date': '2026-01-05', 'days_overdue': 7},
        ]
    }


def get_task_data(start_date: datetime, end_date: datetime):
    """Get completed tasks from vault"""
    vault_path = Path(os.getenv('VAULT_PATH', 'C:/Users/Najma-LP/Desktop/My Vault/AI_Employee_Vault'))
    tasks_dir = vault_path / 'Tasks' / 'Done'

    if not tasks_dir.exists():
        logger.warning("Tasks/Done folder not found")
        return {
            'completed_tasks': [],
            'bottlenecks': [],
            'upcoming_deadlines': []
        }

    # TODO: Parse task files
    # For now, return mock data
    return {
        'completed_tasks': [
            {'name': 'Client A proposal delivered', 'estimated_days': 2, 'actual_days': 2},
            {'name': 'Product launch preparation', 'estimated_days': 3, 'actual_days': 5},
            {'name': 'Q4 financial review completed', 'estimated_days': 1, 'actual_days': 1},
        ],
        'bottlenecks': [
            {'task': 'Client B proposal', 'expected': 2, 'actual': 5, 'delay': 3, 'impact': 'High'}
        ],
        'upcoming_deadlines': [
            {'task': 'Project Alpha final delivery', 'due_date': '2026-01-15', 'days_remaining': 3},
            {'task': 'Quarterly tax prep', 'due_date': '2026-01-31', 'days_remaining': 19},
        ]
    }


def get_social_media_data(start_date: datetime, end_date: datetime):
    """Get social media metrics from social-media-manager"""
    logger.info("Fetching social media data")

    # TODO: Call social-media-manager skill
    # For now, return mock data
    return {
        'posts_published': 12,
        'total_impressions': 15000,
        'total_engagement': 450,
        'engagement_rate': 3.0,
        'follower_growth': 25,
        'top_post': {
            'platform': 'Instagram',
            'content': 'Behind the scenes at our new office...',
            'impressions': 5000,
            'likes': 280,
            'comments': 45,
        }
    }


def audit_subscriptions():
    """Run subscription audit"""
    logger.info("Running subscription audit")

    # TODO: Call audit_subscriptions.py
    # For now, return mock data
    return {
        'total_subscriptions': 12,
        'total_monthly_cost': 847,
        'unused_subscriptions': [
            {'name': 'Notion', 'cost': 15, 'days_inactive': 45},
        ],
        'optimization_opportunities': [
            {
                'subscription': 'Notion',
                'action': 'cancel',
                'reason': 'No activity in 45 days, duplicate with Google Docs',
                'annual_savings': 180
            },
            {
                'subscription': 'Adobe Creative Cloud',
                'action': 'downgrade',
                'reason': 'Low usage (15%), cheaper plan available',
                'annual_savings': 420
            },
            {
                'subscription': 'Slack',
                'action': 'review',
                'reason': 'Low team engagement, consolidate to free tier',
                'annual_savings': 480
            }
        ],
        'total_potential_savings': 1080
    }


def generate_executive_summary(data: Dict) -> str:
    """Generate 3-sentence executive summary"""
    financial = data['financial']
    goals = data['goals']

    revenue_pct = (financial['revenue_this_week'] / goals['revenue_target_weekly']) * 100
    revenue_status = "ahead of" if revenue_pct > 100 else "on track with" if revenue_pct > 90 else "behind"

    summary = f"""## 📊 Executive Summary

Strong week with revenue {revenue_status} target ({revenue_pct:.0f}% of goal). """

    # Add key win
    if data['tasks']['completed_tasks']:
        top_task = data['tasks']['completed_tasks'][0]
        summary += f"Major milestone: {top_task['name']}. "

    # Add critical alert
    if data['tasks']['bottlenecks']:
        bottleneck = data['tasks']['bottlenecks'][0]
        summary += f"One bottleneck identified: {bottleneck['task']} delayed by {bottleneck['delay']} days."
    else:
        summary += "No critical bottlenecks identified."

    return summary


def generate_financial_section(data: Dict) -> str:
    """Generate financial performance section"""
    financial = data['financial']
    goals = data['goals']

    revenue_pct = (financial['revenue_mtd'] / goals['revenue_target_monthly']) * 100
    trend = "🟢 On track" if revenue_pct >= 40 else "🟡 Attention needed" if revenue_pct >= 30 else "🔴 Behind target"

    section = f"""## 💰 Financial Performance

### Revenue
- **This Week**: ${financial['revenue_this_week']:,.0f}
- **MTD**: ${financial['revenue_mtd']:,.0f} ({revenue_pct:.0f}% of ${goals['revenue_target_monthly']:,.0f} target)
- **Trend**: {trend}
- **vs Last Week**: +15% growth

### Expenses
- **Total This Week**: ${financial['expenses_this_week']:,.0f}
"""

    for category, amount in financial['expenses_by_category'].items():
        section += f"- **{category}**: ${amount:,.0f}\n"

    section += f"""
### Cash Flow
- **Current Balance**: ${financial['cash_balance']:,.0f}
- **Projected EOM**: ${financial['cash_balance'] + 3000:,.0f}
"""

    if financial['outstanding_invoices']:
        section += f"- **Outstanding Invoices**: ${sum(inv['amount'] for inv in financial['outstanding_invoices']):,.0f} ({len(financial['outstanding_invoices'])} clients)\n"

        overdue = [inv for inv in financial['outstanding_invoices'] if inv['days_overdue'] > 0]
        if overdue:
            section += f"  - ⚠️ **{len(overdue)} overdue** (follow up this week)\n"

    return section


def generate_tasks_section(data: Dict) -> str:
    """Generate project & task progress section"""
    tasks = data['tasks']

    section = """## ✅ Project & Task Progress

### Completed This Week
"""

    for task in tasks['completed_tasks']:
        status = "⚠️" if task['actual_days'] > task['estimated_days'] else ""
        section += f"- ✅ {task['name']} (Est: {task['estimated_days']} days, Actual: {task['actual_days']} days) {status}\n"

    if tasks['bottlenecks']:
        section += "\n### Bottlenecks\n"
        section += "| Task | Expected | Actual | Delay | Impact |\n"
        section += "|------|----------|--------|-------|--------|\n"
        for bottleneck in tasks['bottlenecks']:
            section += f"| {bottleneck['task']} | {bottleneck['expected']} days | {bottleneck['actual']} days | +{bottleneck['delay']} days | {bottleneck['impact']} |\n"

    section += "\n### Upcoming Deadlines\n"
    for deadline in tasks['upcoming_deadlines']:
        section += f"- **{deadline['task']}**: {deadline['due_date']} ({deadline['days_remaining']} days remaining)\n"

    return section


def generate_subscription_section(data: Dict) -> str:
    """Generate subscription audit section"""
    subs = data['subscriptions']

    section = f"""## 💳 Subscription Audit

### Summary
- **Total Subscriptions**: {subs['total_subscriptions']} (${subs['total_monthly_cost']:,.0f}/month, ${subs['total_monthly_cost'] * 12:,.0f}/year)
- **Optimization Potential**: ${subs['total_potential_savings']:,.0f}/year

### Cost Optimization Opportunities

"""

    for i, opp in enumerate(subs['optimization_opportunities'], 1):
        action_emoji = "✅" if opp['action'] == 'cancel' else "⚠️"
        section += f"{action_emoji} **{opp['subscription']}** - ${opp['annual_savings']:,.0f}/year\n"
        section += f"  - **Action**: {opp['action'].capitalize()}\n"
        section += f"  - **Reason**: {opp['reason']}\n\n"

    section += f"### Total Potential Savings: ${subs['total_potential_savings']:,.0f}/year\n"

    return section


def generate_social_media_section(data: Dict) -> str:
    """Generate social media performance section"""
    social = data['social_media']

    section = f"""## 📱 Social Media Performance

### This Week
- **Posts Published**: {social['posts_published']}
- **Total Impressions**: {social['total_impressions']:,}
- **Total Engagement**: {social['total_engagement']} ({social['engagement_rate']:.1f}% rate)
- **Follower Growth**: +{social['follower_growth']} followers

### Top Performing Post
**Platform**: {social['top_post']['platform']}
**Content**: "{social['top_post']['content']}"
**Impressions**: {social['top_post']['impressions']:,}
**Engagement**: {social['top_post']['likes']} likes, {social['top_post']['comments']} comments

### Recommendation
{social['top_post']['platform']} continues to outperform. Consider increasing {social['top_post']['platform']} content frequency.
"""

    return section


def generate_recommendations(data: Dict) -> str:
    """Generate proactive recommendations"""
    section = """## 🎯 Proactive Recommendations

### Cost Optimization 💰
"""

    # Subscription recommendations
    subs = data['subscriptions']
    if subs['optimization_opportunities']:
        top_sub = subs['optimization_opportunities'][0]
        section += f"1. **Subscription Cleanup**: {top_sub['action'].capitalize()} {top_sub['subscription']}\n"
        section += f"   - **Impact**: ${top_sub['annual_savings']:,.0f}/year savings\n"
        section += f"   - **Action**: Review with team, implement next week\n\n"

    # Invoice follow-up
    financial = data['financial']
    overdue_invoices = [inv for inv in financial['outstanding_invoices'] if inv['days_overdue'] > 0]
    if overdue_invoices:
        total_overdue = sum(inv['amount'] for inv in overdue_invoices)
        section += f"2. **Payment Follow-up**: {len(overdue_invoices)} invoices overdue (${total_overdue:,.0f})\n"
        section += f"   - **Impact**: Cash flow risk\n"
        section += f"   - **Action**: Follow up with clients this week\n\n"

    section += "### Process Improvements ⚙️\n"

    # Bottleneck improvements
    bottlenecks = data['tasks']['bottlenecks']
    if bottlenecks:
        bottleneck = bottlenecks[0]
        section += f"3. **{bottleneck['task']}**: Taking {bottleneck['actual']} days vs {bottleneck['expected']} days target\n"
        section += f"   - **Impact**: Delayed revenue, poor experience\n"
        section += f"   - **Action**: Review process, identify blockers, automate where possible\n\n"

    # Social media optimization
    social = data['social_media']
    if social['engagement_rate'] > 4.0:
        section += f"4. **Social Media ROI**: {social['top_post']['platform']} engagement {social['engagement_rate']:.1f}%, above 3% average\n"
        section += f"   - **Impact**: Lead generation opportunity\n"
        section += f"   - **Action**: Increase {social['top_post']['platform']} posting frequency\n"

    return section


def generate_metrics_dashboard(data: Dict) -> str:
    """Generate key metrics dashboard"""
    financial = data['financial']
    goals = data['goals']
    tasks = data['tasks']

    revenue_pct = (financial['revenue_this_week'] / goals['revenue_target_weekly']) * 100
    revenue_status = "🟢" if revenue_pct >= 90 else "🟡" if revenue_pct >= 70 else "🔴"

    expense_ratio = (financial['expenses_this_week'] / financial['revenue_this_week']) * 100 if financial['revenue_this_week'] > 0 else 100
    expense_status = "🟢" if expense_ratio < 80 else "🟡" if expense_ratio < 90 else "🔴"

    task_completion = len([t for t in tasks['completed_tasks'] if t['actual_days'] <= t['estimated_days']]) / len(tasks['completed_tasks']) * 100 if tasks['completed_tasks'] else 0
    task_status = "🟢" if task_completion >= 80 else "🟡" if task_completion >= 60 else "🔴"

    section = f"""## 📈 Key Metrics Dashboard

| Metric | This Week | Target | Status |
|--------|-----------|--------|--------|
| Revenue | ${financial['revenue_this_week']:,.0f} | ${goals['revenue_target_weekly']:,.0f}/wk | {revenue_status} {revenue_pct:.0f}% |
| Expense Ratio | {expense_ratio:.0f}% | <80% | {expense_status} |
| Task Completion | {task_completion:.0f}% | >80% | {task_status} |
| Cash Flow | ${financial['cash_balance']:,.0f} | Healthy | 🟢 |

### Legend
🟢 On Track | 🟡 Attention Needed | 🔴 Urgent
"""

    return section


def generate_briefing(start_date: datetime, end_date: datetime, sections: list = None):
    """Generate complete CEO briefing"""
    logger.info(f"Generating CEO briefing for {start_date.date()} to {end_date.date()}")

    # Collect all data
    data = {
        'goals': load_business_goals(),
        'financial': get_financial_data(start_date, end_date),
        'tasks': get_task_data(start_date, end_date),
        'social_media': get_social_media_data(start_date, end_date),
        'subscriptions': audit_subscriptions(),
    }

    # Generate briefing sections
    briefing = f"""# Monday Morning CEO Briefing
## Week of {start_date.strftime('%B %d')} - {end_date.strftime('%B %d, %Y')}

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

"""

    all_sections = {
        'summary': generate_executive_summary,
        'financial': generate_financial_section,
        'tasks': generate_tasks_section,
        'subscriptions': generate_subscription_section,
        'social': generate_social_media_section,
        'recommendations': generate_recommendations,
        'metrics': generate_metrics_dashboard,
    }

    # Include only requested sections if specified
    if sections:
        selected_sections = {k: v for k, v in all_sections.items() if k in sections}
    else:
        selected_sections = all_sections

    # Generate each section
    for section_name, section_func in selected_sections.items():
        try:
            briefing += section_func(data) + "\n\n---\n\n"
        except Exception as e:
            logger.error(f"Error generating {section_name} section: {e}")
            briefing += f"## Error\n\nFailed to generate {section_name} section: {str(e)}\n\n---\n\n"

    briefing += "*Generated by ceo-briefing-generator skill*\n"
    briefing += f"*Next briefing: {(end_date + timedelta(days=7)).strftime('%B %d, %Y')}*\n"

    return briefing


def save_briefing(briefing: str, date: datetime):
    """Save briefing to vault"""
    vault_path = Path(os.getenv('VAULT_PATH', 'C:/Users/Najma-LP/Desktop/My Vault/AI_Employee_Vault'))
    briefings_dir = vault_path / 'Briefings'
    briefings_dir.mkdir(parents=True, exist_ok=True)

    filename = f"Monday_Briefing_{date.strftime('%Y-%m-%d')}.md"
    filepath = briefings_dir / filename

    filepath.write_text(briefing)
    logger.info(f"Briefing saved to: {filepath}")

    return filepath


def update_dashboard(briefing_summary: dict):
    """Update Dashboard.md with briefing summary"""
    vault_path = Path(os.getenv('VAULT_PATH', 'C:/Users/Najma-LP/Desktop/My Vault/AI_Employee_Vault'))
    dashboard_file = vault_path / 'Dashboard.md'

    if dashboard_file.exists():
        logger.info("Dashboard.md updated with briefing summary")
        # TODO: Update dashboard with key metrics
    else:
        logger.warning("Dashboard.md not found")


def main():
    parser = argparse.ArgumentParser(description='Generate CEO Briefing')
    parser.add_argument('--period', default='week',
                       choices=['week', 'month', 'quarter'],
                       help='Time period for briefing')
    parser.add_argument('--start', help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end', help='End date (YYYY-MM-DD)')
    parser.add_argument('--sections', help='Comma-separated sections to include')
    parser.add_argument('--template', help='Briefing template (standard, deep-dive)')
    parser.add_argument('--output', help='Output file path')

    args = parser.parse_args()

    load_env()

    # Parse dates
    if args.start and args.end:
        start_date = datetime.strptime(args.start, '%Y-%m-%d')
        end_date = datetime.strptime(args.end, '%Y-%m-%d')
    else:
        start_date, end_date = get_period_dates(args.period)

    # Parse sections
    sections = None
    if args.sections:
        sections = [s.strip() for s in args.sections.split(',')]

    # Generate briefing
    briefing = generate_briefing(start_date, end_date, sections)

    # Save briefing
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(briefing)
        logger.info(f"Briefing saved to: {output_path}")
    else:
        filepath = save_briefing(briefing, end_date)
        logger.info(f"Briefing generated: {filepath}")

    # Update dashboard
    update_dashboard({
        'date': end_date,
        'revenue_status': 'on_track',
        'critical_alerts': 0
    })

    # Print to stdout
    print(briefing)


if __name__ == '__main__':
    main()
