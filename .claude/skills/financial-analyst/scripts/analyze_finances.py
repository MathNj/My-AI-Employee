#!/usr/bin/env python3
"""
Financial Analyst - Financial Data Analysis Tool

Analyzes financial data to generate insights, summaries, trends, and risk signals.

CRITICAL: This script performs ANALYSIS ONLY.
- Never moves money
- Never executes payments
- Never edits bank records
- Never takes irreversible actions

Usage:
    python analyze_finances.py                      # Analyze current month
    python analyze_finances.py --period month       # Current month
    python analyze_finances.py --period year        # Current year
    python analyze_finances.py --period custom --start 2026-01-01 --end 2026-01-31
    python analyze_finances.py --output reports/custom.md
"""

import os
import sys
import json
import csv
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Tuple, Optional
import argparse

# Vault paths
VAULT_PATH = Path(__file__).parent.parent.parent.parent.absolute()
ACCOUNTING = VAULT_PATH / "Accounting"
BANK_TRANSACTIONS = VAULT_PATH / "Bank_Transactions"
SUBSCRIPTIONS = VAULT_PATH / "Subscriptions"
REPORTS = VAULT_PATH / "Reports"
BUSINESS_GOALS = VAULT_PATH / "Business_Goals.md"
LOGS = VAULT_PATH / "Logs"

# Ensure directories exist
for folder in [ACCOUNTING, BANK_TRANSACTIONS, SUBSCRIPTIONS, REPORTS, LOGS]:
    folder.mkdir(exist_ok=True)

# Expense categories
EXPENSE_CATEGORIES = {
    'software': ['software', 'saas', 'subscription', 'license', 'cloud', 'hosting'],
    'marketing': ['ads', 'advertising', 'marketing', 'seo', 'social media'],
    'infrastructure': ['server', 'hosting', 'aws', 'azure', 'gcp', 'domain'],
    'tools': ['tool', 'service', 'api', 'integration'],
    'professional_services': ['consultant', 'contractor', 'freelancer', 'legal', 'accounting'],
    'travel': ['travel', 'flight', 'hotel', 'uber', 'taxi'],
    'office': ['office', 'supplies', 'equipment', 'furniture'],
    'utilities': ['utility', 'internet', 'phone', 'electricity'],
    'other': []
}

# Anomaly thresholds
ANOMALY_THRESHOLDS = {
    'spike_multiplier': 2.5,  # Flag if expense is 2.5x average
    'new_vendor_flag': True,  # Flag new vendors
    'duplicate_threshold_hours': 24,  # Flag duplicates within 24 hours
    'large_transaction_amount': 1000  # Flag transactions > $1000
}


def log_activity(action: str, details: Dict):
    """Log financial analysis activity."""
    log_file = LOGS / f"financial_analysis_{datetime.now().strftime('%Y-%m-%d')}.json"

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "details": details,
        "skill": "financial-analyst"
    }

    try:
        logs = []
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)

        logs.append(log_entry)

        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Warning: Failed to log activity: {e}", file=sys.stderr)


def parse_date(date_str: str) -> Optional[datetime]:
    """Parse date from various formats."""
    formats = [
        '%Y-%m-%d',
        '%m/%d/%Y',
        '%d/%m/%Y',
        '%Y/%m/%d',
        '%B %d, %Y',
        '%b %d, %Y'
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue

    return None


def categorize_expense(description: str, vendor: str = '') -> str:
    """Categorize expense based on description and vendor."""
    text = f"{description} {vendor}".lower()

    for category, keywords in EXPENSE_CATEGORIES.items():
        if any(keyword in text for keyword in keywords):
            return category

    return 'other'


def parse_transaction_file(file_path: Path) -> List[Dict]:
    """
    Parse transaction file (MD or CSV).

    Returns list of transaction dicts with:
    - date: datetime
    - amount: float
    - type: 'income' or 'expense'
    - category: str
    - description: str
    - vendor: str
    """
    transactions = []

    try:
        if file_path.suffix == '.csv':
            # Parse CSV
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    date = parse_date(row.get('date', row.get('Date', '')))
                    if not date:
                        continue

                    amount_str = row.get('amount', row.get('Amount', '0'))
                    amount = float(amount_str.replace('$', '').replace(',', ''))

                    trans_type = row.get('type', row.get('Type', 'expense')).lower()
                    if amount < 0:
                        trans_type = 'expense'
                        amount = abs(amount)
                    elif 'income' in trans_type or 'revenue' in trans_type:
                        trans_type = 'income'
                    else:
                        trans_type = 'expense'

                    description = row.get('description', row.get('Description', ''))
                    vendor = row.get('vendor', row.get('Vendor', ''))

                    transactions.append({
                        'date': date,
                        'amount': amount,
                        'type': trans_type,
                        'category': categorize_expense(description, vendor),
                        'description': description,
                        'vendor': vendor,
                        'source_file': file_path.name
                    })

        elif file_path.suffix == '.md':
            # Parse markdown (simple format)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Look for transaction lines (various formats)
            for line in content.split('\n'):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                # Try to extract date, amount, description
                # Format: YYYY-MM-DD | $XXX.XX | Description
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 3:
                    date = parse_date(parts[0])
                    if not date:
                        continue

                    amount_str = parts[1].replace('$', '').replace(',', '')
                    try:
                        amount = abs(float(amount_str))
                    except ValueError:
                        continue

                    description = parts[2] if len(parts) > 2 else ''
                    vendor = parts[3] if len(parts) > 3 else ''

                    # Determine type
                    trans_type = 'expense'
                    if len(parts) > 4 and 'income' in parts[4].lower():
                        trans_type = 'income'

                    transactions.append({
                        'date': date,
                        'amount': amount,
                        'type': trans_type,
                        'category': categorize_expense(description, vendor),
                        'description': description,
                        'vendor': vendor,
                        'source_file': file_path.name
                    })

    except Exception as e:
        print(f"Error parsing {file_path}: {e}", file=sys.stderr)

    return transactions


def load_transactions(start_date: datetime, end_date: datetime) -> List[Dict]:
    """Load all transactions within date range."""
    all_transactions = []

    # Load from Accounting
    for file_path in ACCOUNTING.glob('*.csv'):
        transactions = parse_transaction_file(file_path)
        all_transactions.extend(transactions)

    for file_path in ACCOUNTING.glob('*.md'):
        transactions = parse_transaction_file(file_path)
        all_transactions.extend(transactions)

    # Load from Bank_Transactions
    for file_path in BANK_TRANSACTIONS.glob('*.csv'):
        transactions = parse_transaction_file(file_path)
        all_transactions.extend(transactions)

    for file_path in BANK_TRANSACTIONS.glob('*.md'):
        transactions = parse_transaction_file(file_path)
        all_transactions.extend(transactions)

    # Filter by date range
    filtered = [t for t in all_transactions
                if start_date <= t['date'] <= end_date]

    return filtered


def analyze_revenue(transactions: List[Dict]) -> Dict:
    """Analyze revenue from transactions."""
    revenue_transactions = [t for t in transactions if t['type'] == 'income']

    if not revenue_transactions:
        return {
            'total': 0,
            'count': 0,
            'average': 0,
            'trend': 'no_data',
            'by_source': {}
        }

    total = sum(t['amount'] for t in revenue_transactions)
    count = len(revenue_transactions)
    average = total / count if count > 0 else 0

    # Group by vendor/source
    by_source = defaultdict(float)
    for t in revenue_transactions:
        source = t['vendor'] or t['description'][:30]
        by_source[source] += t['amount']

    # Calculate trend (compare first half vs second half)
    mid_point = len(revenue_transactions) // 2
    if mid_point > 0:
        first_half = sum(t['amount'] for t in revenue_transactions[:mid_point])
        second_half = sum(t['amount'] for t in revenue_transactions[mid_point:])

        if second_half > first_half * 1.1:
            trend = 'increasing'
        elif second_half < first_half * 0.9:
            trend = 'decreasing'
        else:
            trend = 'stable'
    else:
        trend = 'insufficient_data'

    return {
        'total': total,
        'count': count,
        'average': average,
        'trend': trend,
        'by_source': dict(by_source)
    }


def analyze_expenses(transactions: List[Dict]) -> Dict:
    """Analyze expenses by category."""
    expense_transactions = [t for t in transactions if t['type'] == 'expense']

    if not expense_transactions:
        return {
            'total': 0,
            'count': 0,
            'by_category': {},
            'top_vendors': {}
        }

    total = sum(t['amount'] for t in expense_transactions)
    count = len(expense_transactions)

    # Group by category
    by_category = defaultdict(float)
    for t in expense_transactions:
        by_category[t['category']] += t['amount']

    # Group by vendor
    by_vendor = defaultdict(float)
    for t in expense_transactions:
        vendor = t['vendor'] or 'Unknown'
        by_vendor[vendor] += t['amount']

    # Top vendors
    top_vendors = dict(sorted(by_vendor.items(),
                             key=lambda x: x[1],
                             reverse=True)[:10])

    return {
        'total': total,
        'count': count,
        'by_category': dict(by_category),
        'top_vendors': top_vendors
    }


def calculate_cash_flow(revenue_analysis: Dict, expense_analysis: Dict,
                       opening_balance: float = 0) -> Dict:
    """Calculate cash flow."""
    revenue = revenue_analysis['total']
    expenses = expense_analysis['total']
    net_flow = revenue - expenses
    closing_balance = opening_balance + net_flow

    return {
        'opening_balance': opening_balance,
        'revenue': revenue,
        'expenses': expenses,
        'net_flow': net_flow,
        'closing_balance': closing_balance
    }


def detect_anomalies(transactions: List[Dict]) -> List[Dict]:
    """Detect financial anomalies."""
    anomalies = []

    # Calculate average transaction amounts by category
    category_amounts = defaultdict(list)
    for t in transactions:
        if t['type'] == 'expense':
            category_amounts[t['category']].append(t['amount'])

    category_averages = {
        cat: sum(amounts) / len(amounts)
        for cat, amounts in category_amounts.items()
        if amounts
    }

    # Track vendors seen
    known_vendors = set()

    # Analyze transactions
    for i, transaction in enumerate(transactions):
        if transaction['type'] != 'expense':
            continue

        amount = transaction['amount']
        category = transaction['category']
        vendor = transaction['vendor'] or 'Unknown'

        # Check for spikes
        if category in category_averages:
            avg = category_averages[category]
            if amount > avg * ANOMALY_THRESHOLDS['spike_multiplier']:
                anomalies.append({
                    'type': 'unusual_spike',
                    'severity': 'medium',
                    'transaction': transaction,
                    'message': f"Expense {amount:.2f} is {amount/avg:.1f}x average for {category}"
                })

        # Check for new vendors
        if ANOMALY_THRESHOLDS['new_vendor_flag'] and vendor not in known_vendors:
            known_vendors.add(vendor)
            anomalies.append({
                'type': 'new_vendor',
                'severity': 'low',
                'transaction': transaction,
                'message': f"First transaction with vendor: {vendor}"
            })

        # Check for large transactions
        if amount > ANOMALY_THRESHOLDS['large_transaction_amount']:
            anomalies.append({
                'type': 'large_transaction',
                'severity': 'medium',
                'transaction': transaction,
                'message': f"Large transaction: ${amount:.2f}"
            })

        # Check for duplicates
        for j in range(max(0, i-10), i):
            other = transactions[j]
            if other['type'] != 'expense':
                continue

            time_diff = abs((transaction['date'] - other['date']).total_seconds() / 3600)
            if (time_diff < ANOMALY_THRESHOLDS['duplicate_threshold_hours'] and
                abs(transaction['amount'] - other['amount']) < 0.01 and
                transaction['vendor'] == other['vendor']):

                anomalies.append({
                    'type': 'possible_duplicate',
                    'severity': 'high',
                    'transaction': transaction,
                    'message': f"Possible duplicate charge: ${transaction['amount']:.2f} from {transaction['vendor']}"
                })
                break

    return anomalies


def load_subscriptions() -> List[Dict]:
    """Load subscription data."""
    subscriptions = []

    for file_path in SUBSCRIPTIONS.glob('*.md'):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Simple parsing - look for subscription info
            # Format: Service | $XX/month | Status
            for line in content.split('\n'):
                if '|' in line and '$' in line:
                    parts = [p.strip() for p in line.split('|')]
                    if len(parts) >= 3:
                        service = parts[0]
                        cost_str = parts[1].replace('$', '').replace('/month', '').replace(',', '')
                        try:
                            cost = float(cost_str)
                            status = parts[2] if len(parts) > 2 else 'active'

                            subscriptions.append({
                                'service': service,
                                'monthly_cost': cost,
                                'annual_cost': cost * 12,
                                'status': status.lower(),
                                'source_file': file_path.name
                            })
                        except ValueError:
                            continue

        except Exception as e:
            print(f"Error loading subscriptions from {file_path}: {e}", file=sys.stderr)

    return subscriptions


def analyze_subscriptions(subscriptions: List[Dict]) -> Dict:
    """Analyze subscription data."""
    active_subs = [s for s in subscriptions if 'active' in s['status']]

    if not active_subs:
        return {
            'count': 0,
            'monthly_total': 0,
            'annual_total': 0,
            'by_service': {}
        }

    monthly_total = sum(s['monthly_cost'] for s in active_subs)
    annual_total = sum(s['annual_cost'] for s in active_subs)

    by_service = {s['service']: s['monthly_cost'] for s in active_subs}

    return {
        'count': len(active_subs),
        'monthly_total': monthly_total,
        'annual_total': annual_total,
        'by_service': by_service
    }


def assess_risk_level(anomalies: List[Dict], cash_flow: Dict) -> str:
    """Assess overall financial risk level."""
    high_severity_count = sum(1 for a in anomalies if a['severity'] == 'high')
    medium_severity_count = sum(1 for a in anomalies if a['severity'] == 'medium')

    # Check cash flow
    negative_cash_flow = cash_flow['net_flow'] < 0

    if high_severity_count > 2 or (high_severity_count > 0 and negative_cash_flow):
        return 'high'
    elif medium_severity_count > 3 or high_severity_count > 0:
        return 'medium'
    else:
        return 'low'


def assess_data_completeness(transactions: List[Dict]) -> str:
    """Assess data completeness."""
    if not transactions:
        return 'low'

    # Check for missing fields
    missing_vendors = sum(1 for t in transactions if not t['vendor'])
    missing_descriptions = sum(1 for t in transactions if not t['description'])

    completeness_ratio = 1 - (missing_vendors + missing_descriptions) / (len(transactions) * 2)

    if completeness_ratio > 0.9:
        return 'high'
    elif completeness_ratio > 0.7:
        return 'medium'
    else:
        return 'low'


def generate_report(start_date: datetime, end_date: datetime,
                   revenue_analysis: Dict, expense_analysis: Dict,
                   cash_flow: Dict, anomalies: List[Dict],
                   subscription_analysis: Dict,
                   data_completeness: str, risk_level: str) -> str:
    """Generate formatted financial analysis report."""

    period_str = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"

    report = f"""---
report_id: FIN_{datetime.now().strftime('%Y%m%d%H%M%S')}
generated: {datetime.now().isoformat()}Z
period: {period_str}
data_completeness: {data_completeness}
risk_level: {risk_level}
---

# Financial Analysis Report

**Period:** {period_str}
**Generated:** {datetime.now().strftime('%B %d, %Y at %H:%M')}
**Data Completeness:** {data_completeness.upper()}
**Risk Level:** {risk_level.upper()}

---

## Executive Summary

"""

    # Executive summary
    if revenue_analysis['total'] > 0 and expense_analysis['total'] > 0:
        profit_margin = ((revenue_analysis['total'] - expense_analysis['total']) /
                        revenue_analysis['total'] * 100)
        report += f"**Revenue:** ${revenue_analysis['total']:,.2f}\n"
        report += f"**Expenses:** ${expense_analysis['total']:,.2f}\n"
        report += f"**Net:** ${cash_flow['net_flow']:,.2f}\n"
        report += f"**Profit Margin:** {profit_margin:.1f}%\n\n"

        if cash_flow['net_flow'] > 0:
            report += f"✅ Positive cash flow of ${cash_flow['net_flow']:,.2f}\n"
        else:
            report += f"⚠️  Negative cash flow of ${cash_flow['net_flow']:,.2f}\n"
    else:
        report += "Insufficient revenue or expense data for the period.\n"

    report += f"\n**Anomalies Detected:** {len(anomalies)}\n"

    # Revenue Analysis
    report += f"""
---

## Revenue Analysis

**Total Revenue:** ${revenue_analysis['total']:,.2f}
**Transaction Count:** {revenue_analysis['count']}
**Average per Transaction:** ${revenue_analysis['average']:,.2f}
**Trend:** {revenue_analysis['trend'].replace('_', ' ').title()}

"""

    if revenue_analysis['by_source']:
        report += "### Revenue by Source\n\n"
        for source, amount in sorted(revenue_analysis['by_source'].items(),
                                     key=lambda x: x[1],
                                     reverse=True)[:10]:
            report += f"- **{source}:** ${amount:,.2f}\n"

    # Expense Breakdown
    report += f"""
---

## Expense Breakdown

**Total Expenses:** ${expense_analysis['total']:,.2f}
**Transaction Count:** {expense_analysis['count']}

### By Category

| Category | Amount | % of Total | Trend |
|----------|--------|------------|-------|
"""

    total_expenses = expense_analysis['total']
    for category, amount in sorted(expense_analysis['by_category'].items(),
                                   key=lambda x: x[1],
                                   reverse=True):
        percentage = (amount / total_expenses * 100) if total_expenses > 0 else 0
        report += f"| {category.replace('_', ' ').title()} | ${amount:,.2f} | {percentage:.1f}% | - |\n"

    # Top Vendors
    if expense_analysis['top_vendors']:
        report += "\n### Top Vendors\n\n"
        for vendor, amount in list(expense_analysis['top_vendors'].items())[:10]:
            report += f"- **{vendor}:** ${amount:,.2f}\n"

    # Cash Flow
    report += f"""
---

## Cash Flow

**Opening Balance:** ${cash_flow['opening_balance']:,.2f}
**Revenue:** +${cash_flow['revenue']:,.2f}
**Expenses:** -${cash_flow['expenses']:,.2f}
**Net Flow:** ${cash_flow['net_flow']:,.2f}
**Closing Balance:** ${cash_flow['closing_balance']:,.2f}

"""

    if cash_flow['net_flow'] < 0:
        report += "⚠️  **Warning:** Negative cash flow for this period\n"

    # Anomalies & Flags
    report += """
---

## Anomalies & Flags

"""

    if anomalies:
        # Group by type
        by_type = defaultdict(list)
        for anomaly in anomalies:
            by_type[anomaly['type']].append(anomaly)

        for anomaly_type, items in by_type.items():
            severity_icon = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}
            report += f"### {anomaly_type.replace('_', ' ').title()} ({len(items)})\n\n"

            for item in items[:5]:  # Show top 5 per type
                icon = severity_icon.get(item['severity'], '⚪')
                report += f"{icon} **{item['severity'].upper()}:** {item['message']}\n"
                t = item['transaction']
                report += f"   - Date: {t['date'].strftime('%Y-%m-%d')}\n"
                report += f"   - Amount: ${t['amount']:,.2f}\n"
                report += f"   - Vendor: {t['vendor'] or 'Unknown'}\n\n"

    else:
        report += "✅ No anomalies detected\n"

    # Subscription Insights
    if subscription_analysis['count'] > 0:
        report += f"""
---

## Subscription Insights

**Active Subscriptions:** {subscription_analysis['count']}
**Monthly Cost:** ${subscription_analysis['monthly_total']:,.2f}
**Annual Cost:** ${subscription_analysis['annual_total']:,.2f}

### Top Subscriptions

"""
        for service, cost in sorted(subscription_analysis['by_service'].items(),
                                   key=lambda x: x[1],
                                   reverse=True)[:10]:
            annual = cost * 12
            report += f"- **{service}:** ${cost:,.2f}/month (${annual:,.2f}/year)\n"

    # Recommendations
    report += """
---

## Recommendations

"""

    if cash_flow['net_flow'] < 0:
        report += "- ⚠️  Address negative cash flow - review expense reduction opportunities\n"

    if len(anomalies) > 5:
        report += f"- ⚠️  {len(anomalies)} anomalies detected - review for errors or fraud\n"

    duplicate_anomalies = [a for a in anomalies if a['type'] == 'possible_duplicate']
    if duplicate_anomalies:
        report += f"- 🔴 {len(duplicate_anomalies)} possible duplicate charges - verify with vendors\n"

    if subscription_analysis['monthly_total'] > 0:
        if subscription_analysis['monthly_total'] > expense_analysis['total'] * 0.3:
            report += f"- ⚠️  Subscriptions are {subscription_analysis['monthly_total']/expense_analysis['total']*100:.0f}% of expenses - audit for unused services\n"

    report += """
---

## Data Quality Notes

"""

    if data_completeness == 'low':
        report += "⚠️  **Low data completeness** - some transactions missing vendor or description information\n"
    elif data_completeness == 'medium':
        report += "✅ **Medium data completeness** - most transactions have complete information\n"
    else:
        report += "✅ **High data completeness** - transactions well-documented\n"

    report += """
---

*This report provides descriptive analysis only, not prescriptive financial advice.*
*Final decisions belong to the business owner.*
*Generated by financial-analyst skill - analysis only, no actions taken.*
"""

    return report


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Analyze financial data and generate insights'
    )
    parser.add_argument(
        '--period',
        choices=['month', 'year', 'custom'],
        default='month',
        help='Analysis period'
    )
    parser.add_argument(
        '--start',
        type=str,
        help='Start date (YYYY-MM-DD) for custom period'
    )
    parser.add_argument(
        '--end',
        type=str,
        help='End date (YYYY-MM-DD) for custom period'
    )
    parser.add_argument(
        '--output',
        '-o',
        type=str,
        help='Output report file path'
    )
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Verbose output'
    )

    args = parser.parse_args()

    # Determine date range
    now = datetime.now()

    if args.period == 'month':
        start_date = datetime(now.year, now.month, 1)
        end_date = now
    elif args.period == 'year':
        start_date = datetime(now.year, 1, 1)
        end_date = now
    elif args.period == 'custom':
        if not args.start or not args.end:
            print("Error: --start and --end required for custom period")
            sys.exit(1)
        start_date = datetime.strptime(args.start, '%Y-%m-%d')
        end_date = datetime.strptime(args.end, '%Y-%m-%d')
    else:
        print(f"Error: Unknown period: {args.period}")
        sys.exit(1)

    print(f"Analyzing financial data from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")

    # Load data
    if args.verbose:
        print("Loading transactions...")
    transactions = load_transactions(start_date, end_date)
    print(f"  Loaded {len(transactions)} transactions")

    if args.verbose:
        print("Loading subscriptions...")
    subscriptions = load_subscriptions()
    print(f"  Loaded {len(subscriptions)} subscriptions")

    # Analyze
    if args.verbose:
        print("Analyzing revenue...")
    revenue_analysis = analyze_revenue(transactions)

    if args.verbose:
        print("Analyzing expenses...")
    expense_analysis = analyze_expenses(transactions)

    if args.verbose:
        print("Calculating cash flow...")
    cash_flow = calculate_cash_flow(revenue_analysis, expense_analysis)

    if args.verbose:
        print("Detecting anomalies...")
    anomalies = detect_anomalies(transactions)

    if args.verbose:
        print("Analyzing subscriptions...")
    subscription_analysis = analyze_subscriptions(subscriptions)

    # Assess
    data_completeness = assess_data_completeness(transactions)
    risk_level = assess_risk_level(anomalies, cash_flow)

    # Generate report
    if args.verbose:
        print("Generating report...")
    report = generate_report(
        start_date, end_date,
        revenue_analysis, expense_analysis,
        cash_flow, anomalies,
        subscription_analysis,
        data_completeness, risk_level
    )

    # Output
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = REPORTS / f"Financial_Analysis_{now.strftime('%Y-%m-%d')}.md"

    output_path.write_text(report, encoding='utf-8')
    print(f"\n✅ Report generated: {output_path}")

    # Log activity
    log_activity("financial_analysis_completed", {
        "period": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
        "transactions": len(transactions),
        "revenue": revenue_analysis['total'],
        "expenses": expense_analysis['total'],
        "net_flow": cash_flow['net_flow'],
        "anomalies": len(anomalies),
        "risk_level": risk_level
    })

    sys.exit(0)


if __name__ == '__main__':
    main()
