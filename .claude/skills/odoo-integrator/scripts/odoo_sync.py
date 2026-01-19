#!/usr/bin/env python3
"""
Odoo Sync Script for AI Employee

Syncs accounting data from local Odoo Community instance to the vault.
Uses the Odoo MCP server for all operations.

Usage:
    python odoo_sync.py --sync all
    python odoo_sync.py --sync invoices --from-date 2026-01-01
    python odoo_sync.py --sync payments --dry-run
"""

import os
import sys
import json
import logging
import requests
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure logging
log_dir = Path(__file__).parent.parent.parent.parent / "Logs"
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "odoo_integrator_2026-01-18.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("odoo_sync")


class OdooSyncClient:
    """Client for syncing data from Odoo via MCP server"""

    def __init__(self):
        self.mcp_url = os.getenv("ODOO_MCP_URL", "http://localhost:8000")
        self.vault_path = Path(os.getenv("VAULT_PATH", "."))
        self.accounting_path = self.vault_path / "Accounting"
        self.timeout = int(os.getenv("ODOO_MCP_TIMEOUT", "30"))

        # Create accounting directories
        (self.accounting_path / "Invoices").mkdir(parents=True, exist_ok=True)
        (self.accounting_path / "Payments").mkdir(parents=True, exist_ok=True)
        (self.accounting_path / "Vendors").mkdir(parents=True, exist_ok=True)
        (self.accounting_path / "Customers").mkdir(parents=True, exist_ok=True)
        (self.accounting_path / "Reports").mkdir(parents=True, exist_ok=True)

        # Sync state file
        self.state_file = self.accounting_path / ".sync_state.json"
        self.state = self._load_state()

    def _load_state(self) -> Dict:
        """Load sync state from file"""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                return json.load(f)
        return {
            "last_sync": None,
            "invoices": {},
            "payments": {},
            "partners": {}
        }

    def _save_state(self):
        """Save sync state to file"""
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)

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
                timeout=self.timeout
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

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return None

    def sync_invoices(self, from_date: Optional[str] = None, dry_run: bool = False) -> int:
        """Sync invoices from Odoo"""
        logger.info("Syncing invoices...")

        # Build domain filter
        domain = [
            ["move_type", "in", ["out_invoice", "in_invoice"]],
            ["state", "=", "posted"]
        ]

        if from_date:
            domain.append(["invoice_date", ">=", from_date])

        # Search for invoices
        result = self._call_mcp("search_records", {
            "model": "account.move",
            "domain": domain,
            "fields": [
                "id", "name", "move_type", "state", "payment_state",
                "invoice_date", "partner_id", "amount_total", "amount_residual",
                "create_date", "write_date"
            ],
            "order": "invoice_date desc",
            "limit": 1000
        })

        if not result or "records" not in result:
            logger.warning("No invoices found or error occurred")
            return 0

        invoices = result["records"]
        count = len(invoices)

        logger.info(f"Found {count} invoices")

        if dry_run:
            logger.info("[DRY RUN] Would sync invoices:")
            for inv in invoices[:5]:
                logger.info(f"  - {inv['name']}: {inv['amount_total']}")
            return count

        # Group by month
        by_month = {}
        for inv in invoices:
            month = inv.get("invoice_date", inv.get("create_date", ""))[:7]
            if month not in by_month:
                by_month[month] = []
            by_month[month].append(inv)

        # Save to files
        for month, month_invoices in by_month.items():
            file_path = self.accounting_path / "Invoices" / f"{month}.json"

            # Load existing data
            existing = {}
            if file_path.exists():
                with open(file_path, 'r') as f:
                    existing = json.load(f)

            # Merge/update
            existing_invoices = existing.get("invoices", [])
            existing_ids = {inv["id"] for inv in existing_invoices}

            for inv in month_invoices:
                if inv["id"] not in existing_ids:
                    existing_invoices.append(inv)

            # Save
            with open(file_path, 'w') as f:
                json.dump({
                    "month": month,
                    "synced_at": datetime.now().isoformat(),
                    "count": len(existing_invoices),
                    "invoices": existing_invoices
                }, f, indent=2)

            logger.info(f"Saved {len(month_invoices)} invoices to {file_path.name}")

        # Update state
        self.state["invoices"]["last_sync"] = datetime.now().isoformat()
        self.state["invoices"]["count"] = count
        self._save_state()

        return count

    def sync_payments(self, from_date: Optional[str] = None, dry_run: bool = False) -> int:
        """Sync payments from Odoo"""
        logger.info("Syncing payments...")

        # Build domain filter
        domain = [["state", "=", "posted"]]

        if from_date:
            domain.append(["payment_date", ">=", from_date])

        # Search for payments
        result = self._call_mcp("search_records", {
            "model": "account.payment",
            "domain": domain,
            "fields": [
                "id", "name", "payment_type", "partner_type",
                "amount", "payment_date", "partner_id", "state",
                "journal_id", "create_date"
            ],
            "order": "payment_date desc",
            "limit": 1000
        })

        if not result or "records" not in result:
            logger.warning("No payments found or error occurred")
            return 0

        payments = result["records"]
        count = len(payments)

        logger.info(f"Found {count} payments")

        if dry_run:
            logger.info("[DRY RUN] Would sync payments:")
            for pay in payments[:5]:
                logger.info(f"  - {pay['name']}: {pay['amount']}")
            return count

        # Group by month
        by_month = {}
        for pay in payments:
            month = pay.get("payment_date", pay.get("create_date", ""))[:7]
            if month not in by_month:
                by_month[month] = []
            by_month[month].append(pay)

        # Save to files
        for month, month_payments in by_month.items():
            file_path = self.accounting_path / "Payments" / f"{month}.json"

            # Load existing data
            existing = {}
            if file_path.exists():
                with open(file_path, 'r') as f:
                    existing = json.load(f)

            # Merge/update
            existing_payments = existing.get("payments", [])
            existing_ids = {pay["id"] for pay in existing_payments}

            for pay in month_payments:
                if pay["id"] not in existing_ids:
                    existing_payments.append(pay)

            # Save
            with open(file_path, 'w') as f:
                json.dump({
                    "month": month,
                    "synced_at": datetime.now().isoformat(),
                    "count": len(existing_payments),
                    "payments": existing_payments
                }, f, indent=2)

            logger.info(f"Saved {len(month_payments)} payments to {file_path.name}")

        # Update state
        self.state["payments"]["last_sync"] = datetime.now().isoformat()
        self.state["payments"]["count"] = count
        self._save_state()

        return count

    def sync_partners(self, dry_run: bool = False) -> Dict[str, int]:
        """Sync customers and vendors from Odoo"""
        logger.info("Syncing partners...")

        # Search for customers
        customers = self._call_mcp("search_records", {
            "model": "res.partner",
            "domain": [["customer_rank", ">", 0]],
            "fields": ["id", "name", "email", "phone", "customer_rank", "supplier_rank"],
            "limit": 1000
        })

        # Search for vendors
        vendors = self._call_mcp("search_records", {
            "model": "res.partner",
            "domain": [["supplier_rank", ">", 0]],
            "fields": ["id", "name", "email", "phone", "customer_rank", "supplier_rank"],
            "limit": 1000
        })

        customer_count = 0
        vendor_count = 0

        if customers and "records" in customers:
            customer_list = customers["records"]
            customer_count = len(customer_list)

            if not dry_run:
                with open(self.accounting_path / "Customers.json", 'w') as f:
                    json.dump({
                        "synced_at": datetime.now().isoformat(),
                        "count": customer_count,
                        "customers": customer_list
                    }, f, indent=2)
                logger.info(f"Saved {customer_count} customers")

        if vendors and "records" in vendors:
            vendor_list = vendors["records"]
            vendor_count = len(vendor_list)

            if not dry_run:
                with open(self.accounting_path / "Vendors.json", 'w') as f:
                    json.dump({
                        "synced_at": datetime.now().isoformat(),
                        "count": vendor_count,
                        "vendors": vendor_list
                    }, f, indent=2)
                logger.info(f"Saved {vendor_count} vendors")

        # Update state
        self.state["partners"]["last_sync"] = datetime.now().isoformat()
        self.state["partners"]["customers"] = customer_count
        self.state["partners"]["vendors"] = vendor_count
        self._save_state()

        return {"customers": customer_count, "vendors": vendor_count}

    def sync_all(self, from_date: Optional[str] = None, dry_run: bool = False):
        """Sync all accounting data from Odoo"""
        logger.info("=" * 60)
        logger.info("Odoo Sync - Starting")
        logger.info("=" * 60)

        if dry_run:
            logger.info("DRY RUN MODE - No files will be modified")
            print()

        start_time = datetime.now()

        try:
            # Sync partners first (they're referenced by invoices/payments)
            partners = self.sync_partners(dry_run=dry_run)
            logger.info(f"[OK] Partners: {partners['customers']} customers, {partners['vendors']} vendors")
            print()

            # Sync invoices
            invoices = self.sync_invoices(from_date=from_date, dry_run=dry_run)
            logger.info(f"[OK] Invoices: {invoices} synced")
            print()

            # Sync payments
            payments = self.sync_payments(from_date=from_date, dry_run=dry_run)
            logger.info(f"[OK] Payments: {payments} synced")
            print()

            # Update overall state
            self.state["last_sync"] = datetime.now().isoformat()
            self._save_state()

            elapsed = (datetime.now() - start_time).total_seconds()

            logger.info("=" * 60)
            logger.info(f"Sync completed in {elapsed:.1f} seconds")
            logger.info("=" * 60)

            # Print summary
            print("\nSync Summary:")
            print(f"  Customers: {partners['customers']}")
            print(f"  Vendors: {partners['vendors']}")
            print(f"  Invoices: {invoices}")
            print(f"  Payments: {payments}")

        except Exception as e:
            logger.error(f"Sync failed: {e}")
            raise


def main():
    parser = argparse.ArgumentParser(
        description="Sync accounting data from Odoo to vault",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --sync all                    Sync everything
  %(prog)s --sync invoices                Sync only invoices
  %(prog)s --sync all --from-date 2026-01-01  Sync since Jan 1
  %(prog)s --sync all --dry-run            Show what would be synced
        """
    )

    parser.add_argument(
        "--sync",
        choices=["all", "invoices", "payments", "partners"],
        default="all",
        help="What to sync from Odoo"
    )

    parser.add_argument(
        "--from-date",
        help="Only sync records from this date (YYYY-MM-DD)"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be synced without making changes"
    )

    args = parser.parse_args()

    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()

    # Create sync client
    client = OdooSyncClient()

    # Execute sync
    if args.sync == "all":
        client.sync_all(from_date=args.from_date, dry_run=args.dry_run)
    elif args.sync == "invoices":
        client.sync_invoices(from_date=args.from_date, dry_run=args.dry_run)
    elif args.sync == "payments":
        client.sync_payments(from_date=args.from_date, dry_run=args.dry_run)
    elif args.sync == "partners":
        client.sync_partners(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
