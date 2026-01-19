#!/usr/bin/env python3
"""
Odoo Report Script for AI Employee

Generates financial reports from Odoo accounting data.
Uses the Odoo MCP server for all operations.

Usage:
    python odoo_report.py --type profit_loss
    python odoo_report.py --type balance_sheet --from 2026-01-01
    python odoo_report.py --all
"""

import os
import sys
import json
import logging
import argparse
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure logging
log_dir = Path(__file__).parent.parent.parent.parent / "Logs"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "odoo_integrator_2026-01-18.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("odoo_report")


class OdooReportGenerator:
    """Generate financial reports from Odoo data"""

    def __init__(self):
        self.mcp_url = os.getenv("ODOO_MCP_URL", "http://localhost:8000")
        self.vault_path = Path(os.getenv("VAULT_PATH", "."))
        self.accounting_path = self.vault_path / "Accounting"
        self.reports_path = self.accounting_path / "Reports"
        self.reports_path.mkdir(parents=True, exist_ok=True)

    def _call_mcp(self, tool_name: str, arguments: Dict) -> Any:
        """Call Odoo MCP server tool"""
        try:
            response = requests.post(
                f"{self.mcp_url}/",
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {
                        "name": tool_name,
                        "arguments": arguments
                    }
                },
                timeout=30
            )
            response.raise_for_status()
            data = response.json()

            if "error" in data:
                logger.error(f"MCP Error: {data['error']}")
                return None

            result = data.get("result", {})
            if "content" in result and len(result["content"]) > 0:
                text = result["content"][0].get("text", "")
                return json.loads(text) if text else None

            return result

        except Exception as e:
            logger.error(f"MCP call failed: {e}")
            return None

    def generate_profit_loss(self, from_date: Optional[str] = None, to_date: Optional[str] = None) -> str:
        """Generate Profit & Loss statement"""
        logger.info("Generating Profit & Loss statement...")

        # Get income (customer invoices)
        income_domain = [
            ["move_type", "=", "out_invoice"],
            ["state", "=", "posted"]
        ]

        if from_date:
            income_domain.append(["invoice_date", ">=", from_date])
        if to_date:
            income_domain.append(["invoice_date", "<=", to_date])

        income_result = self._call_mcp("search_records", {
            "model": "account.move",
            "domain": income_domain,
            "fields": ["name", "invoice_date", "amount_total", "partner_id"],
            "limit": 1000
        })

        # Get expenses (vendor bills)
        expense_domain = [
            ["move_type", "=", "in_invoice"],
            ["state", "=", "posted"]
        ]

        if from_date:
            expense_domain.append(["invoice_date", ">=", from_date])
        if to_date:
            expense_domain.append(["invoice_date", "<=", to_date])

        expense_result = self._call_mcp("search_records", {
            "model": "account.move",
            "domain": expense_domain,
            "fields": ["name", "invoice_date", "amount_total", "partner_id"],
            "limit": 1000
        })

        income_list = income_result.get("records", []) if income_result else []
        expense_list = expense_result.get("records", []) if expense_result else []

        total_income = sum(item.get("amount_total", 0) for item in income_list)
        total_expenses = sum(item.get("amount_total", 0) for item in expense_list)
        net_profit = total_income - total_expenses

        # Generate report
        report = f"""# Profit & Loss Statement

**Period:** {from_date or "All time"} to {to_date or "Present"}
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M")}

---

## Revenue

| Source | Amount |
|--------|--------|
"""

        # Group income by partner
        income_by_partner = {}
        for item in income_list:
            partner = item.get("partner_id", ["Unknown"])[1] if isinstance(item.get("partner_id"), list) else "Unknown"
            amount = item.get("amount_total", 0)
            income_by_partner[partner] = income_by_partner.get(partner, 0) + amount

        for partner, amount in sorted(income_by_partner.items(), key=lambda x: x[1], reverse=True):
            report += f"| {partner} | ${amount:,.2f} |\n"

        report += f"| **Total Revenue** | **${total_income:,.2f}** |\n"

        report += "\n## Expenses\n\n"
        report += "| Category | Amount |\n"
        report += "|----------|--------|\n"

        # Group expenses by partner (vendor)
        expense_by_partner = {}
        for item in expense_list:
            partner = item.get("partner_id", ["Unknown"])[1] if isinstance(item.get("partner_id"), list) else "Unknown"
            amount = item.get("amount_total", 0)
            expense_by_partner[partner] = expense_by_partner.get(partner, 0) + amount

        for partner, amount in sorted(expense_by_partner.items(), key=lambda x: x[1], reverse=True):
            report += f"| {partner} | ${amount:,.2f} |\n"

        report += f"| **Total Expenses** | **${total_expenses:,.2f}** |\n"

        report += "\n## Net Profit\n\n"
        report += f"| **Net Profit** | **${net_profit:,.2f}** |\n"
        report += f"| **Profit Margin** | **{net_profit/total_income*100 if total_income > 0 else 0:.1f}%** |\n"

        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_Profit_Loss.md"
        file_path = self.reports_path / filename

        with open(file_path, 'w') as f:
            f.write(report)

        logger.info(f"Profit & Loss saved to {filename}")
        return str(file_path)

    def generate_balance_sheet(self, as_of_date: Optional[str] = None) -> str:
        """Generate Balance Sheet"""
        logger.info("Generating Balance Sheet...")

        # Get all partners with balances
        result = self._call_mcp("search_records", {
            "model": "res.partner",
            "domain": [
                ["customer_rank", ">", 0],
                ["supplier_rank", ">", 0]
            ],
            "fields": ["name", "customer_rank", "supplier_rank"],
            "limit": 1000
        })

        partners = result.get("records", []) if result else []

        report = f"""# Balance Sheet

**As of:** {as_of_date or datetime.now().strftime("%Y-%m-%d")}
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M")}

---

## Assets

### Current Assets

| Asset | Value |
|-------|-------|
| Cash & Equivalents | TBD |
| Accounts Receivable | TBD |
| Inventory | TBD |
| **Total Current Assets** | **TBD** |

### Fixed Assets

| Asset | Value |
|-------|-------|
| Equipment | TBD |
| **Total Fixed Assets** | **TBD** |

---

## Liabilities

### Current Liabilities

| Liability | Value |
|-----------|-------|
| Accounts Payable | TBD |
| **Total Current Liabilities** | **TBD** |

---

## Equity

| Equity Item | Value |
|-------------|-------|
| Owner's Equity | TBD |
| **Total Equity** | **TBD** |

---

*Note: Full balance sheet requires additional Odoo modules and account configuration*
"""

        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_Balance_Sheet.md"
        file_path = self.reports_path / filename

        with open(file_path, 'w') as f:
            f.write(report)

        logger.info(f"Balance Sheet saved to {filename}")
        return str(file_path)

    def generate_aged_receivables(self) -> str:
        """Generate Aged Accounts Receivable report"""
        logger.info("Generating Aged Receivables...")

        # Get unpaid customer invoices
        result = self._call_mcp("search_records", {
            "model": "account.move",
            "domain": [
                ["move_type", "=", "out_invoice"],
                ["payment_state", "!=", "paid"],
                ["state", "=", "posted"]
            ],
            "fields": ["name", "invoice_date", "invoice_date_due", "amount_total", "amount_residual", "partner_id", "payment_state"],
            "order": "invoice_date_due asc",
            "limit": 1000
        })

        invoices = result.get("records", []) if result else []

        # Calculate aging
        today = datetime.now()
        aging_buckets = {
            "Current": [],
            "1-30 Days": [],
            "31-60 Days": [],
            "61-90 Days": [],
            "90+ Days": []
        }

        for invoice in invoices:
            due_date_str = invoice.get("invoice_date_due", "")
            if due_date_str:
                try:
                    due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
                    days_overdue = (today - due_date).days
                except ValueError:
                    days_overdue = 0
            else:
                days_overdue = 0

            amount = invoice.get("amount_residual", 0)

            if days_overdue <= 0:
                aging_buckets["Current"].append(amount)
            elif days_overdue <= 30:
                aging_buckets["1-30 Days"].append(amount)
            elif days_overdue <= 60:
                aging_buckets["31-60 Days"].append(amount)
            elif days_overdue <= 90:
                aging_buckets["61-90 Days"].append(amount)
            else:
                aging_buckets["90+ Days"].append(amount)

        # Generate report
        report = f"""# Aged Accounts Receivable

**As of:** {datetime.now().strftime("%Y-%m-%d")}
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M")}

---

## Summary

| Aging Bucket | Count | Amount |
|--------------|-------|--------|
| Current | {len(aging_buckets["Current"])} | ${sum(aging_buckets["Current"]):,.2f} |
| 1-30 Days | {len(aging_buckets["1-30 Days"])} | ${sum(aging_buckets["1-30 Days"]):,.2f} |
| 31-60 Days | {len(aging_buckets["31-60 Days"])} | ${sum(aging_buckets["31-60 Days"]):,.2f} |
| 61-90 Days | {len(aging_buckets["61-90 Days"])} | ${sum(aging_buckets["61-90 Days"]):,.2f} |
| 90+ Days | {len(aging_buckets["90+ Days"])} | ${sum(aging_buckets["90+ Days"]):,.2f} |
| **Total** | **{len(invoices)}** | **${sum(aging_buckets["Current"] + aging_buckets["1-30 Days"] + aging_buckets["31-60 Days"] + aging_buckets["61-90 Days"] + aging_buckets["90+ Days"]):,.2f}** |

---

## Detailed Invoices

"""

        for invoice in invoices[:20]:  # Show first 20
            partner = invoice.get("partner_id", ["Unknown"])[1] if isinstance(invoice.get("partner_id"), list) else "Unknown"
            report += f"\n### {invoice.get('name', 'N/A')}\n"
            report += f"- **Customer:** {partner}\n"
            report += f"- **Invoice Date:** {invoice.get('invoice_date', 'N/A')}\n"
            report += f"- **Due Date:** {invoice.get('invoice_date_due', 'N/A')}\n"
            report += f"- **Total:** ${invoice.get('amount_total', 0):,.2f}\n"
            report += f"- **Outstanding:** ${invoice.get('amount_residual', 0):,.2f}\n"
            report += f"- **Status:** {invoice.get('payment_state', 'unknown').title()}\n"

        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_Aged_Receivables.md"
        file_path = self.reports_path / filename

        with open(file_path, 'w') as f:
            f.write(report)

        logger.info(f"Aged Receivables saved to {filename}")
        return str(file_path)

    def generate_cash_flow(self, from_date: Optional[str] = None, to_date: Optional[str] = None) -> str:
        """Generate Cash Flow statement"""
        logger.info("Generating Cash Flow statement...")

        # Get payments received
        payments_domain = [
            ["payment_type", "=", "inbound"],
            ["state", "=", "posted"]
        ]

        if from_date:
            payments_domain.append(["payment_date", ">=", from_date])
        if to_date:
            payments_domain.append(["payment_date", "<=", to_date])

        payments_result = self._call_mcp("search_records", {
            "model": "account.payment",
            "domain": payments_domain,
            "fields": ["name", "payment_date", "amount", "partner_id"],
            "limit": 1000
        })

        payments = payments_result.get("records", []) if payments_result else []
        total_received = sum(p.get("amount", 0) for p in payments)

        # Get payments made
        payments_out_domain = [
            ["payment_type", "=", "outbound"],
            ["state", "=", "posted"]
        ]

        if from_date:
            payments_out_domain.append(["payment_date", ">=", from_date])
        if to_date:
            payments_out_domain.append(["payment_date", "<=", to_date])

        payments_out_result = self._call_mcp("search_records", {
            "model": "account.payment",
            "domain": payments_out_domain,
            "fields": ["name", "payment_date", "amount", "partner_id"],
            "limit": 1000
        })

        payments_out = payments_out_result.get("records", []) if payments_out_result else []
        total_paid = sum(p.get("amount", 0) for p in payments_out)

        net_cash_flow = total_received - total_paid

        report = f"""# Cash Flow Statement

**Period:** {from_date or "All time"} to {to_date or "Present"}
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M")}

---

## Cash Inflows

| Source | Amount |
|--------|--------|
"""

        # Group by partner
        inflow_by_partner = {}
        for payment in payments:
            partner = payment.get("partner_id", ["Unknown"])[1] if isinstance(payment.get("partner_id"), list) else "Unknown"
            amount = payment.get("amount", 0)
            inflow_by_partner[partner] = inflow_by_partner.get(partner, 0) + amount

        for partner, amount in sorted(inflow_by_partner.items(), key=lambda x: x[1], reverse=True):
            report += f"| {partner} | ${amount:,.2f} |\n"

        report += f"| **Total Cash In** | **${total_received:,.2f}** |\n"

        report += "\n## Cash Outflows\n\n"
        report += "| Source | Amount |\n"
        report += "|--------|--------|\n"

        # Group by partner
        outflow_by_partner = {}
        for payment in payments_out:
            partner = payment.get("partner_id", ["Unknown"])[1] if isinstance(payment.get("partner_id"), list) else "Unknown"
            amount = payment.get("amount", 0)
            outflow_by_partner[partner] = outflow_by_partner.get(partner, 0) + amount

        for partner, amount in sorted(outflow_by_partner.items(), key=lambda x: x[1], reverse=True):
            report += f"| {partner} | ${amount:,.2f} |\n"

        report += f"| **Total Cash Out** | **${total_paid:,.2f}** |\n"

        report += "\n## Net Cash Flow\n\n"
        report += f"| **Net Cash Flow** | **${net_cash_flow:,.2f}** |\n"

        if net_cash_flow > 0:
            report += f"\n✅ **Positive cash flow** - Good financial health\n"
        else:
            report += f"\n⚠️  **Negative cash flow** - Monitor cash position\n"

        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_Cash_Flow.md"
        file_path = self.reports_path / filename

        with open(file_path, 'w') as f:
            f.write(report)

        logger.info(f"Cash Flow saved to {filename}")
        return str(file_path)

    def generate_expense_breakdown(self, from_date: Optional[str] = None) -> str:
        """Generate expense breakdown by category"""
        logger.info("Generating Expense Breakdown...")

        # Get all expenses
        expense_domain = [
            ["move_type", "=", "in_invoice"],
            ["state", "=", "posted"]
        ]

        if from_date:
            expense_domain.append(["invoice_date", ">=", from_date])

        result = self._call_mcp("search_records", {
            "model": "account.move",
            "domain": expense_domain,
            "fields": ["name", "invoice_date", "amount_total", "partner_id"],
            "limit": 1000
        })

        expenses = result.get("records", []) if result else []

        # Load categorization
        cat_dir = self.accounting_path / "Categorization"
        categorized = {}

        if cat_dir.exists():
            cat_files = sorted(cat_dir.glob("*.json"), reverse=True)[:5]
            for cat_file in cat_files:
                with open(cat_file, 'r') as f:
                    data = json.load(f)
                    for item in data.get("items", []):
                        categorized[item["id"]] = item

        # Categorize expenses
        expenses_by_category = {}
        uncategorized_total = 0

        for expense in expenses:
            exp_id = expense["id"]
            if exp_id in categorized:
                category = categorized[exp_id]["category"]
                amount = expense.get("amount_total", 0)
                expenses_by_category[category] = expenses_by_category.get(category, 0) + amount
            else:
                uncategorized_total += expense.get("amount_total", 0)

        report = f"""# Expense Breakdown by Category

**Period:** {from_date or "All time"}
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M")}

---

## Categorized Expenses

| Category | Amount |
|----------|--------|
"""

        total_expenses = 0
        for category, amount in sorted(expenses_by_category.items(), key=lambda x: x[1], reverse=True):
            report += f"| {category} | ${amount:,.2f} |\n"
            total_expenses += amount

        report += f"| **Total Categorized** | **${total_expenses:,.2f}** |\n"

        if uncategorized_total > 0:
            report += f"\n## Uncategorized\n\n"
            report += f"| Uncategorized | ${uncategorized_total:,.2f} |\n"
            total_expenses += uncategorized_total

        report += f"\n### Summary\n\n"
        report += f"- **Total Expenses:** ${total_expenses:,.2f}\n"
        report += f"- **Categorization Rate:** {len([e for e in expenses if e['id'] in categorized]) / len(expenses) * 100:.1f}%\n"

        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_Expense_Breakdown.md"
        file_path = self.reports_path / filename

        with open(file_path, 'w') as f:
            f.write(report)

        logger.info(f"Expense Breakdown saved to {filename}")
        return str(file_path)


def main():
    parser = argparse.ArgumentParser(
        description="Generate financial reports from Odoo"
    )

    parser.add_argument(
        "--type",
        choices=["profit_loss", "balance_sheet", "aged_receivables", "cash_flow", "expense_breakdown"],
        help="Type of report to generate"
    )

    parser.add_argument(
        "--from",
        dest="from_date",
        help="Start date (YYYY-MM-DD)"
    )

    parser.add_argument(
        "--to",
        dest="to_date",
        help="End date (YYYY-MM-DD)"
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Generate all reports"
    )

    args = parser.parse_args()

    # Load environment
    from dotenv import load_dotenv
    load_dotenv()

    # Create generator
    generator = OdooReportGenerator()

    if args.all:
        logger.info("Generating all reports...")
        generator.generate_profit_loss(args.from_date, args.to_date)
        generator.generate_balance_sheet(args.to_date)
        generator.generate_aged_receivables()
        generator.generate_cash_flow(args.from_date, args.to_date)
        generator.generate_expense_breakdown(args.from_date)
        logger.info("All reports generated successfully")
    elif args.type:
        if args.type == "profit_loss":
            path = generator.generate_profit_loss(args.from_date, args.to_date)
        elif args.type == "balance_sheet":
            path = generator.generate_balance_sheet(args.to_date)
        elif args.type == "aged_receivables":
            path = generator.generate_aged_receivables()
        elif args.type == "cash_flow":
            path = generator.generate_cash_flow(args.from_date, args.to_date)
        elif args.type == "expense_breakdown":
            path = generator.generate_expense_breakdown(args.from_date)

        logger.info(f"Report saved to: {path}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
