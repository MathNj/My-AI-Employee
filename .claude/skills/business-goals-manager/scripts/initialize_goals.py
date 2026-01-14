#!/usr/bin/env python3
"""
Initialize Business_Goals.md with appropriate template

Usage:
    # Interactive prompt for business type
    python initialize_goals.py

    # Specify business type
    python initialize_goals.py --type startup

    # Custom output path
    python initialize_goals.py --type consulting --output /path/to/Business_Goals.md
"""

import argparse
import logging
from datetime import datetime
from pathlib import Path
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TEMPLATES = {
    'startup': {
        'revenue_monthly': 10000,
        'revenue_stretch': 12000,
        'revenue_minimum': 8000,
        'metrics': [
            {'name': 'Monthly Recurring Revenue (MRR)', 'target': '$10K', 'threshold': '< $8K', 'unit': 'dollars', 'priority': 'High'},
            {'name': 'Customer Acquisition Cost (CAC)', 'target': '< $500', 'threshold': '> $800', 'unit': 'dollars', 'priority': 'High'},
            {'name': 'Customer Lifetime Value (LTV)', 'target': '> $5,000', 'threshold': '< $3,000', 'unit': 'dollars', 'priority': 'High'},
            {'name': 'Churn Rate', 'target': '< 5%', 'threshold': '> 10%', 'unit': 'percent', 'priority': 'High'},
            {'name': 'New Customer Signups', 'target': '20+', 'threshold': '< 10', 'unit': 'count', 'priority': 'High'},
            {'name': 'Product Development Velocity', 'target': '10 features/month', 'threshold': '< 5 features', 'unit': 'count', 'priority': 'Medium'},
            {'name': 'Runway', 'target': '> 12 months', 'threshold': '< 6 months', 'unit': 'months', 'priority': 'Critical'},
        ],
        'projects': [
            'Product-Market Fit Validation',
            'MVP Feature Development',
            'Initial Customer Acquisition',
            'Fundraising Preparation',
        ],
        'initiatives': [
            'Build customer feedback loop',
            'Establish product roadmap',
            'Create repeatable sales process',
            'Secure seed funding',
        ],
    },
    'consulting': {
        'revenue_monthly': 15000,
        'revenue_stretch': 18000,
        'revenue_minimum': 12000,
        'metrics': [
            {'name': 'Client response time', 'target': '< 24 hours', 'threshold': '> 48 hours', 'unit': 'hours', 'priority': 'High'},
            {'name': 'Invoice payment rate', 'target': '> 90%', 'threshold': '< 80%', 'unit': 'percent', 'priority': 'High'},
            {'name': 'Active client count', 'target': '5-8 clients', 'threshold': '< 3 clients', 'unit': 'count', 'priority': 'High'},
            {'name': 'Project profit margin', 'target': '> 60%', 'threshold': '< 40%', 'unit': 'percent', 'priority': 'High'},
            {'name': 'Client retention rate', 'target': '> 80%', 'threshold': '< 60%', 'unit': 'percent', 'priority': 'Medium'},
            {'name': 'Average project value', 'target': '> $5,000', 'threshold': '< $2,000', 'unit': 'dollars', 'priority': 'Medium'},
            {'name': 'Utilization rate', 'target': '70-80%', 'threshold': '< 50%', 'unit': 'percent', 'priority': 'Medium'},
        ],
        'projects': [
            'Client Project A - Strategy Consulting',
            'Client Project B - Implementation',
            'Business Development - New Client Pipeline',
            'Service Offering Expansion',
        ],
        'initiatives': [
            'Standardize delivery methodology',
            'Build case study portfolio',
            'Develop productized service offerings',
            'Create referral partner network',
        ],
    },
    'ecommerce': {
        'revenue_monthly': 50000,
        'revenue_stretch': 60000,
        'revenue_minimum': 40000,
        'metrics': [
            {'name': 'Conversion Rate', 'target': '> 3%', 'threshold': '< 1.5%', 'unit': 'percent', 'priority': 'High'},
            {'name': 'Average Order Value (AOV)', 'target': '> $75', 'threshold': '< $50', 'unit': 'dollars', 'priority': 'High'},
            {'name': 'Customer Acquisition Cost (CAC)', 'target': '< $25', 'threshold': '> $40', 'unit': 'dollars', 'priority': 'High'},
            {'name': 'Return Rate', 'target': '< 5%', 'threshold': '> 10%', 'unit': 'percent', 'priority': 'High'},
            {'name': 'Cart Abandonment Rate', 'target': '< 60%', 'threshold': '> 75%', 'unit': 'percent', 'priority': 'Medium'},
            {'name': 'Repeat Customer Rate', 'target': '> 30%', 'threshold': '< 15%', 'unit': 'percent', 'priority': 'Medium'},
            {'name': 'Inventory Turnover', 'target': '> 6x/year', 'threshold': '< 3x/year', 'unit': 'ratio', 'priority': 'Medium'},
        ],
        'projects': [
            'Product Line Expansion - New Categories',
            'Website Optimization - Checkout Flow',
            'Marketing Campaign - Q1 Launch',
            'Inventory Management System Upgrade',
        ],
        'initiatives': [
            'Launch email marketing automation',
            'Implement customer loyalty program',
            'Optimize supply chain logistics',
            'Expand to new marketplace channels',
        ],
    },
    'saas': {
        'revenue_monthly': 25000,
        'revenue_stretch': 30000,
        'revenue_minimum': 20000,
        'metrics': [
            {'name': 'Monthly Recurring Revenue (MRR)', 'target': '$25K+', 'threshold': '< $20K', 'unit': 'dollars', 'priority': 'Critical'},
            {'name': 'Net Revenue Retention (NRR)', 'target': '> 100%', 'threshold': '< 90%', 'unit': 'percent', 'priority': 'High'},
            {'name': 'Churn Rate (Monthly)', 'target': '< 3%', 'threshold': '> 5%', 'unit': 'percent', 'priority': 'High'},
            {'name': 'Customer Acquisition Cost (CAC)', 'target': '< $600', 'threshold': '> $1000', 'unit': 'dollars', 'priority': 'High'},
            {'name': 'LTV:CAC Ratio', 'target': '> 3:1', 'threshold': '< 2:1', 'unit': 'ratio', 'priority': 'High'},
            {'name': 'Free-to-Paid Conversion', 'target': '> 15%', 'threshold': '< 8%', 'unit': 'percent', 'priority': 'Medium'},
            {'name': 'Average Revenue Per User (ARPU)', 'target': '> $50', 'threshold': '< $30', 'unit': 'dollars', 'priority': 'Medium'},
        ],
        'projects': [
            'Feature Development - Enterprise Dashboard',
            'Customer Success Program Launch',
            'API Integration Platform',
            'Mobile App Development',
        ],
        'initiatives': [
            'Build self-service onboarding',
            'Implement usage-based pricing tier',
            'Create customer health score system',
            'Launch partner integration marketplace',
        ],
    },
}


def get_vault_path():
    """Get vault path from environment or use default"""
    return Path(os.getenv('VAULT_PATH', 'C:/Users/Najma-LP/Desktop/My Vault/AI_Employee_Vault'))


def generate_goals_file(business_type: str) -> str:
    """Generate Business_Goals.md content from template"""
    template = TEMPLATES.get(business_type)
    if not template:
        raise ValueError(f"Unknown business type: {business_type}. Choose from: {', '.join(TEMPLATES.keys())}")

    today = datetime.now().strftime('%Y-%m-%d')

    content = f"""---
last_updated: {today}
review_frequency: weekly
created: {today}
version: 1.0
business_type: {business_type}
---

# Business Goals & Targets

## Revenue Targets

### Monthly
- **Target**: ${template['revenue_monthly']:,}
- **Stretch Goal**: ${template['revenue_stretch']:,}
- **Minimum Acceptable**: ${template['revenue_minimum']:,}

### Quarterly
- **Target**: ${template['revenue_monthly'] * 3:,}
- **Stretch Goal**: ${template['revenue_stretch'] * 3:,}
- **Minimum Acceptable**: ${template['revenue_minimum'] * 3:,}

### Annual
- **Target**: ${template['revenue_monthly'] * 12:,}
- **Stretch Goal**: ${template['revenue_stretch'] * 12:,}
- **Minimum Acceptable**: ${template['revenue_minimum'] * 12:,}

---

## Key Metrics to Track

| Metric | Target | Alert Threshold | Unit | Priority |
|--------|--------|-----------------|------|----------|
"""

    for metric in template['metrics']:
        content += f"| {metric['name']} | {metric['target']} | {metric['threshold']} | {metric['unit']} | {metric['priority']} |\n"

    content += """
---

## Active Projects

"""
    for i, project in enumerate(template['projects'], 1):
        content += f"{i}. **{project}**\n   - Status: Planning\n   - Progress: 0%\n   - Next Milestone: TBD\n\n"

    content += """---

## Strategic Initiatives

"""
    for i, initiative in enumerate(template['initiatives'], 1):
        content += f"{i}. {initiative}\n"

    content += f"""
---

## Alert Thresholds

These metrics trigger proactive notifications in the CEO Briefing:

### Critical Alerts (Immediate Action Required)
- Revenue < ${template['revenue_minimum']:,}/month
- Any metric reaches Critical priority threshold

### High Priority Alerts
- Revenue < {int(template['revenue_monthly'] * 0.9):,}/month (90% of target)
- Any High priority metric reaches alert threshold

### Medium Priority Alerts
- Revenue < ${template['revenue_monthly']:,}/month (below target)
- Any Medium priority metric reaches alert threshold

---

## Progress Tracking

### This Week
- Revenue: $0
- Key Wins: None yet
- Challenges: None yet

### This Month
- Revenue: $0
- Target Progress: 0%
- Active Clients: 0

### This Quarter
- Revenue: $0
- Target Progress: 0%
- Major Milestones: None yet

---

## Notes

*Update this file weekly during CEO Briefing review. The ceo-briefing-generator skill reads this file to track progress and generate proactive alerts.*

---

**Last Updated**: {today}
**Next Review**: {datetime.now().strftime('%Y-%m-%d')} (weekly)
"""

    return content


def main():
    parser = argparse.ArgumentParser(description='Initialize Business_Goals.md')
    parser.add_argument('--type', choices=list(TEMPLATES.keys()),
                       help='Business type (startup, consulting, ecommerce, saas)')
    parser.add_argument('--output', help='Output file path (default: AI_Employee_Vault/Business_Goals.md)')

    args = parser.parse_args()

    # Interactive prompt if type not specified
    if not args.type:
        print("\nSelect business type:")
        for i, btype in enumerate(TEMPLATES.keys(), 1):
            print(f"{i}. {btype.capitalize()}")

        choice = input("\nEnter number (1-4): ").strip()
        types_list = list(TEMPLATES.keys())
        try:
            args.type = types_list[int(choice) - 1]
        except (ValueError, IndexError):
            logger.error("Invalid choice")
            return 1

    # Generate content
    logger.info(f"Generating Business_Goals.md for {args.type} business...")
    content = generate_goals_file(args.type)

    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        vault_path = get_vault_path()
        output_path = vault_path / 'Business_Goals.md'

    # Create parent directory if needed
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write file
    output_path.write_text(content, encoding='utf-8')
    logger.info(f"✅ Business_Goals.md created at: {output_path}")

    # Print summary
    template = TEMPLATES[args.type]
    print(f"\n{'='*60}")
    print(f"Business Goals Initialized - {args.type.capitalize()}")
    print(f"{'='*60}")
    print(f"Monthly Revenue Target: ${template['revenue_monthly']:,}")
    print(f"Key Metrics Tracked: {len(template['metrics'])}")
    print(f"Active Projects: {len(template['projects'])}")
    print(f"Strategic Initiatives: {len(template['initiatives'])}")
    print(f"\nFile Location: {output_path}")
    print(f"{'='*60}\n")

    return 0


if __name__ == '__main__':
    exit(main())
