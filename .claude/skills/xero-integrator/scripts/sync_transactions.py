#!/usr/bin/env python3
"""
Sync transactions from Xero to Obsidian vault

Usage:
    python sync_transactions.py
    python sync_transactions.py --start 2026-01-01 --end 2026-01-31
    python sync_transactions.py --auto-categorize
"""

import argparse
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
import os
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_env():
    """Load environment variables from .env file"""
    env_file = Path(__file__).parent.parent.parent.parent / '.env'
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value


def get_xero_transactions(start_date, end_date):
    """
    Fetch transactions from Xero via MCP server

    In production, this would call the Xero MCP server.
    For now, returns mock data for demonstration.
    """
    logger.info(f"Fetching transactions from {start_date} to {end_date}")

    # TODO: Replace with actual Xero MCP call
    # transactions = xero_mcp.get_transactions(start_date, end_date)

    # Mock data for demonstration
    mock_transactions = [
        {
            "id": "TX001",
            "date": "2026-01-12",
            "vendor": "Staples Inc.",
            "description": "Office supplies - paper and pens",
            "amount": -45.00,
            "category": None,
            "account": "Business Checking"
        },
        {
            "id": "TX002",
            "date": "2026-01-12",
            "vendor": "Adobe Inc.",
            "description": "Creative Cloud subscription",
            "amount": -29.99,
            "category": None,
            "account": "Business Credit Card"
        },
        {
            "id": "TX003",
            "date": "2026-01-12",
            "vendor": "Client A LLC",
            "description": "Invoice #2026-001 payment",
            "amount": 1500.00,
            "category": None,
            "account": "Business Checking"
        }
    ]

    logger.info(f"Retrieved {len(mock_transactions)} transactions")
    return mock_transactions


def categorize_transaction(transaction):
    """
    Auto-categorize transaction using AI rules

    Returns: (category, confidence)
    """
    vendor = transaction['vendor'].lower()
    description = transaction['description'].lower()
    amount = transaction['amount']

    # Simple rule-based categorization
    # TODO: Implement AI-powered categorization

    if amount > 0:
        return "Client Payment", 95

    if 'staples' in vendor or 'office depot' in vendor:
        return "Office Supplies", 95

    if 'adobe' in vendor or 'microsoft' in vendor or 'software' in description:
        return "Software & Subscriptions", 90

    if 'google' in vendor and 'ads' in description:
        return "Marketing & Advertising", 98

    if 'uber' in vendor or 'lyft' in vendor or 'airline' in vendor:
        return "Travel & Entertainment", 85

    return "Uncategorized", 0


def create_transaction_file(transactions, month, vault_path, auto_categorize=False):
    """Create or update monthly transaction markdown file"""
    accounting_dir = vault_path / 'Accounting'
    accounting_dir.mkdir(exist_ok=True)

    filename = f"Transactions_{month}.md"
    filepath = accounting_dir / filename

    # Read existing transactions if file exists
    existing_transactions = {}
    if filepath.exists():
        content = filepath.read_text()
        # Parse existing to avoid duplicates
        # Simple implementation - in production, parse markdown properly
        for line in content.split('\n'):
            if line.startswith('- **'):
                # Extract transaction ID if present
                pass

    # Build markdown content
    content = f"# Transactions - {month}\n\n"
    content += f"**Last Synced:** {datetime.now().isoformat()}\n\n"

    # Group by date
    by_date = {}
    for tx in transactions:
        date = tx['date']
        if date not in by_date:
            by_date[date] = []
        by_date[date].append(tx)

    needs_review = []

    for date in sorted(by_date.keys()):
        content += f"## {date}\n\n"

        for tx in by_date[date]:
            category = tx.get('category')
            confidence = None

            if not category and auto_categorize:
                category, confidence = categorize_transaction(tx)

            amount_str = f"${abs(tx['amount']):.2f}"
            if tx['amount'] > 0:
                amount_str = f"+{amount_str}"
            else:
                amount_str = f"-{amount_str}"

            if category:
                if confidence and confidence >= 90:
                    status = "(Auto-categorized)"
                elif confidence and confidence >= 70:
                    status = "(Suggested - Needs Review)"
                    needs_review.append(tx)
                else:
                    status = "(Needs Review)"
                    needs_review.append(tx)

                content += f"- **{category}** - {amount_str} - {tx['vendor']} - {tx['description']} {status}\n"
            else:
                content += f"- **Uncategorized** - {amount_str} - {tx['vendor']} - {tx['description']} (Needs Categorization)\n"
                needs_review.append(tx)

    # Summary section
    content += f"\n## Summary\n\n"
    content += f"- **Total Transactions:** {len(transactions)}\n"

    if auto_categorize:
        auto_cat = sum(1 for tx in transactions if tx.get('category'))
        content += f"- **Auto-Categorized:** {auto_cat}\n"
        content += f"- **Needs Review:** {len(needs_review)}\n"

    # Write file
    filepath.write_text(content)
    logger.info(f"Created/updated {filepath}")

    return filepath, needs_review


def create_approval_requests(transactions, vault_path):
    """Create approval files for uncertain categorizations"""
    if not transactions:
        return

    approval_dir = vault_path / 'Pending_Approval'
    approval_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    filename = f"XERO_CATEGORIZATION_{timestamp}.md"
    filepath = approval_dir / filename

    content = f"---\n"
    content += f"type: xero_categorization\n"
    content += f"created: {datetime.now().isoformat()}\n"
    content += f"status: pending\n"
    content += f"---\n\n"
    content += f"# Xero Transaction Categorization Review\n\n"
    content += f"Please review and approve these transaction categorizations.\n\n"

    for tx in transactions:
        category, confidence = categorize_transaction(tx)

        content += f"## Transaction {tx['id']}\n\n"
        content += f"- **Date:** {tx['date']}\n"
        content += f"- **Vendor:** {tx['vendor']}\n"
        content += f"- **Description:** {tx['description']}\n"
        content += f"- **Amount:** ${abs(tx['amount']):.2f}\n"
        content += f"- **Suggested Category:** {category} ({confidence}% confidence)\n\n"
        content += f"**Actions:**\n"
        content += f"- [ ] Approve suggested category\n"
        content += f"- [ ] Change to: ____________\n\n"

    filepath.write_text(content)
    logger.info(f"Created approval request: {filepath}")


def log_activity(action, details):
    """Log activity to audit trail"""
    logs_dir = Path(__file__).parent.parent.parent.parent / 'Logs'
    logs_dir.mkdir(exist_ok=True)

    log_file = logs_dir / f"xero_activity_{datetime.now().strftime('%Y-%m-%d')}.json"

    entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "details": details,
        "skill": "xero-integrator"
    }

    # Append to log file
    logs = []
    if log_file.exists():
        logs = json.loads(log_file.read_text())

    logs.append(entry)
    log_file.write_text(json.dumps(logs, indent=2))


def main():
    parser = argparse.ArgumentParser(description='Sync transactions from Xero')
    parser.add_argument('--start', help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end', help='End date (YYYY-MM-DD)')
    parser.add_argument('--auto-categorize', action='store_true',
                        help='Automatically categorize transactions')
    parser.add_argument('--full', action='store_true',
                        help='Full sync (ignore last sync date)')

    args = parser.parse_args()

    # Load environment
    load_env()

    # Get vault path
    vault_path = Path(os.getenv('VAULT_PATH',
                                 'C:/Users/Najma-LP/Desktop/My Vault/AI_Employee_Vault'))

    # Determine date range
    if args.start and args.end:
        start_date = args.start
        end_date = args.end
    else:
        # Default: last 30 days
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

    logger.info(f"Starting Xero sync: {start_date} to {end_date}")

    try:
        # Fetch transactions
        transactions = get_xero_transactions(start_date, end_date)

        if not transactions:
            logger.info("No transactions found")
            return

        # Determine month for file
        month = datetime.strptime(end_date, '%Y-%m-%d').strftime('%Y-%m')

        # Create transaction file
        filepath, needs_review = create_transaction_file(
            transactions, month, vault_path, args.auto_categorize
        )

        # Create approval requests if needed
        if needs_review and args.auto_categorize:
            create_approval_requests(needs_review, vault_path)

        # Log activity
        log_activity('sync_transactions', {
            'start_date': start_date,
            'end_date': end_date,
            'transactions_count': len(transactions),
            'needs_review': len(needs_review),
            'auto_categorize': args.auto_categorize,
            'output_file': str(filepath)
        })

        logger.info(f"Sync complete: {len(transactions)} transactions")
        logger.info(f"Output: {filepath}")

        if needs_review:
            logger.info(f"{len(needs_review)} transactions need review")

    except Exception as e:
        logger.error(f"Sync failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
