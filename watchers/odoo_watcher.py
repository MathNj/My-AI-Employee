#!/usr/bin/env python3
"""
Odoo Watcher - Monitors Odoo ERP for accounting events
Monitors: Invoices, Payments, Bills, Partners

Author: AI Employee System
Created: 2026-01-18
"""

import os
import sys
import json
import time
import logging
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import requests

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure logging
LOG_DIR = Path(__file__).parent.parent / 'Logs'
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / 'odoo_watcher.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Odoo MCP Server configuration
ODOO_MCP_URL = os.getenv('ODOO_MCP_URL', 'http://localhost:8000')
ODOO_URL = os.getenv('ODOO_URL', 'http://localhost:8069')
ODOO_DB = os.getenv('ODOO_DB', 'odoo')
ODOO_USERNAME = os.getenv('ODOO_USERNAME', 'admin')
ODOO_API_KEY = os.getenv('ODOO_API_KEY', '')

# Vault paths
VAULT_PATH = Path(__file__).parent.parent
NEEDS_ACTION_PATH = VAULT_PATH / 'Needs_Action'
ACCOUNTING_PATH = VAULT_PATH / 'Accounting'
ACCOUNTING_PATH.mkdir(exist_ok=True)

# Create subdirectories
(ACCOUNTING_PATH / 'Invoices').mkdir(exist_ok=True)
(ACCOUNTING_PATH / 'Payments').mkdir(exist_ok=True)
(ACCOUNTING_PATH / 'Bills').mkdir(exist_ok=True)
(ACCOUNTING_PATH / 'Partners').mkdir(exist_ok=True)

# State tracking
STATE_FILE = LOG_DIR / 'odoo_watcher_state.json'
CHECK_INTERVAL = 300  # 5 minutes

# Email notification settings
NOTIFICATION_ENABLED = os.getenv('NOTIFICATION_ENABLED', 'true').lower() == 'true'
NOTIFICATION_EMAIL = os.getenv('NOTIFICATION_EMAIL', '')
NOTIFICATION_THRESHOLD = float(os.getenv('NOTIFICATION_THRESHOLD', '0'))  # Notify for invoices >= this amount

class OdooWatcherState:
    """Manages watcher state for detecting new/changed items"""

    def __init__(self):
        self.state = self.load_state()
        self.last_check = self.state.get('last_check', None)

    def load_state(self) -> Dict:
        """Load state from file"""
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load state: {e}")
        return {
            'processed_invoices': [],
            'processed_payments': [],
            'processed_bills': [],
            'last_check': None
        }

    def save_state(self):
        """Save state to file"""
        try:
            with open(STATE_FILE, 'w') as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save state: {e}")

    def is_processed(self, item_type: str, item_id: int) -> bool:
        """Check if item has been processed"""
        key = f'processed_{item_type}'
        return item_id in self.state.get(key, [])

    def mark_processed(self, item_type: str, item_id: int):
        """Mark item as processed"""
        key = f'processed_{item_type}'
        if key not in self.state:
            self.state[key] = []
        self.state[key].append(item_id)
        self.save_state()

    def update_last_check(self, timestamp: str):
        """Update last check timestamp"""
        self.state['last_check'] = timestamp
        self.save_state()


class OdooMCPClient:
    """Client for Odoo MCP Server"""

    def __init__(self, base_url: str = ODOO_MCP_URL):
        self.base_url = base_url
        self.request_id = 0

    def _call_mcp(self, tool_name: str, arguments: Dict) -> Any:
        """Call MCP tool via HTTP"""
        self.request_id += 1

        try:
            response = requests.post(
                f"{self.base_url}/",
                json={
                    "jsonrpc": "2.0",
                    "id": self.request_id,
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

            if 'error' in data:
                logger.error(f"MCP Error: {data['error']}")
                return None

            return data.get('result')
        except Exception as e:
            logger.error(f"Failed to call MCP tool {tool_name}: {e}")
            return None

    def search_records(self, model: str, domain: Optional[List] = None,
                     fields: Optional[List[str]] = None, limit: int = 100) -> List[Dict]:
        """Search records in Odoo"""
        args = {
            'model': model,
            'domain': domain or [],
            'fields': fields or [],
            'limit': limit
        }

        result = self._call_mcp('search_records', args)
        if result and 'records' in result:
            return result['records']
        return []

    def get_record(self, model: str, res_id: int) -> Optional[Dict]:
        """Get a specific record"""
        result = self._call_mcp('get_record', {
            'model': model,
            'res_id': res_id
        })
        if result and 'record' in result:
            return result['record']
        return None

    def execute_method(self, model: str, method: str, args: List = None) -> Any:
        """Execute a method on a model"""
        call_args = {
            'model': model,
            'method': method
        }
        if args:
            call_args['args'] = args

        return self._call_mcp('execute_method', call_args)


class OdooWatcher:
    """Main Odoo Watcher class"""

    def __init__(self):
        self.client = OdooMCPClient()
        self.state = OdooWatcherState()
        self.running = False

    def test_connection(self) -> bool:
        """Test connection to Odoo MCP server"""
        try:
            result = self.client.search_records('res.users', [], [['id', '=', 1]], limit=1)
            return result is not None
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

    def monitor_invoices(self) -> int:
        """Monitor for new customer invoices"""
        logger.info("Checking for new invoices...")

        # Search for invoices created in last hour
        one_hour_ago = (datetime.now() - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')

        invoices = self.client.search_records(
            'account.move',
            [
                ['move_type', '=', 'out_invoice'],
                ['state', '!=', 'cancel'],
                ['create_date', '>=', one_hour_ago]
            ],
            ['id', 'name', 'partner_id', 'invoice_date', 'invoice_payment_term_id',
             'amount_total', 'state', 'create_date', 'invoice_origin'],
            limit=50
        )

        new_count = 0
        for invoice in invoices:
            invoice_id = invoice.get('id')
            if not self.state.is_processed('invoices', invoice_id):
                logger.info(f"New invoice detected: {invoice.get('name')}")

                # Fetch full invoice details
                full_invoice = self.client.get_record('account.move', invoice_id)
                if full_invoice and full_invoice.get('record'):
                    self._process_invoice(full_invoice['record'])
                    self.state.mark_processed('invoices', invoice_id)
                    new_count += 1

        return new_count

    def monitor_payments(self) -> int:
        """Monitor for new payments"""
        logger.info("Checking for new payments...")

        one_hour_ago = (datetime.now() - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')

        payments = self.client.search_records(
            'account.payment',
            [
                ['payment_type', '=', 'inbound'],
                ['create_date', '>=', one_hour_ago]
            ],
            ['id', 'name', 'partner_id', 'amount', 'payment_date', 'create_date',
             'state', 'payment_type', 'journal_id'],
            limit=50
        )

        new_count = 0
        for payment in payments:
            payment_id = payment.get('id')
            if not self.state.is_processed('payments', payment_id):
                logger.info(f"New payment detected: {payment.get('name')}")

                full_payment = self.client.get_record('account.payment', payment_id)
                if full_payment and full_payment.get('record'):
                    self._process_payment(full_payment['record'])
                    self.state.mark_processed('payments', payment_id)
                    new_count += 1

        return new_count

    def monitor_bills(self) -> int:
        """Monitor for new vendor bills"""
        logger.info("Checking for new vendor bills...")

        one_hour_ago = (datetime.now() - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')

        bills = self.client.search_records(
            'account.move',
            [
                ['move_type', '=', 'in_invoice'],
                ['state', '!=', 'cancel'],
                ['create_date', '>=', one_hour_ago]
            ],
            ['id', 'name', 'partner_id', 'invoice_date', 'amount_total',
             'state', 'create_date', 'invoice_date_due'],
            limit=50
        )

        new_count = 0
        for bill in bills:
            bill_id = bill.get('id')
            if not self.state.is_processed('bills', bill_id):
                logger.info(f"New vendor bill detected: {bill.get('name')}")

                full_bill = self.client.get_record('account.move', bill_id)
                if full_bill and full_bill.get('record'):
                    self._process_bill(full_bill['record'])
                    self.state.mark_processed('bills', bill_id)
                    new_count += 1

        return new_count

    def _process_invoice(self, invoice: Dict):
        """Process customer invoice and create task"""
        try:
            invoice_name = invoice.get('name', f'INV-{invoice.get("id")}')
            partner = invoice.get('partner_id', [{}])[0]
            partner_name = partner.get('name', 'Unknown') if isinstance(partner, dict) else 'Unknown'

            amount = invoice.get('amount_total', 0)
            invoice_date = invoice.get('invoice_date') or invoice.get('create_date', '')
            state = invoice.get('state', 'draft')

            # Create task file
            task_filename = f"ODOO_INVOICE_{invoice_name.replace(' ', '_').replace('/', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            task_path = NEEDS_ACTION_PATH / task_filename

            task_content = f"""# Odoo Invoice Received

**Source:** Odoo Accounting
**Priority:** High
**Type:** Invoice Review

## Invoice Details

- **Invoice Number:** {invoice_name}
- **Customer:** {partner_name}
- **Amount:** ${amount:,.2f}
- **Invoice Date:** {invoice_date}
- **Status:** {state}
- **Odoo ID:** {invoice.get('id')}

## Actions Required

1. **Review Invoice Details**
   - Verify line items and quantities
   - Check pricing and terms
   - Confirm customer information

2. **Send Invoice to Customer**
   - Use email-sender skill to send invoice
   - Attach PDF invoice from Odoo

3. **Track Payment**
   - Monitor for incoming payment
   - Record payment in accounting system

## Additional Information

- **Created:** {invoice.get('create_date')}
- **Payment Terms:** {invoice.get('invoice_payment_term_id', 'N/A')}
- **Origin:** {invoice.get('invoice_origin', 'N/A')}

---
*Generated by Odoo Watcher on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

            task_path.write_text(task_content)
            logger.info(f"Created task: {task_filename}")

            # Send email notification if enabled and above threshold
            if amount >= NOTIFICATION_THRESHOLD:
                self._send_email_notification('invoice', invoice)

            # Save to Accounting/Invoices
            self._save_to_accounting('invoice', invoice)

        except Exception as e:
            logger.error(f"Error processing invoice: {e}")

    def _process_payment(self, payment: Dict):
        """Process payment received"""
        try:
            payment_name = payment.get('name', f'PAY-{payment.get("id")}')
            partner = payment.get('partner_id', [{}])[0]
            partner_name = partner.get('name', 'Unknown') if isinstance(partner, dict) else 'Unknown'

            amount = payment.get('amount', 0)
            payment_date = payment.get('payment_date', '')
            state = payment.get('state', 'draft')

            # Create task file
            task_filename = f"ODOO_PAYMENT_{payment_name.replace(' ', '_').replace('/', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            task_path = NEEDS_ACTION_PATH / task_filename

            task_content = f"""# Odoo Payment Received

**Source:** Odoo Accounting
**Priority:** Medium
**Type:** Payment Recording

## Payment Details

- **Payment Reference:** {payment_name}
- **Customer:** {partner_name}
- **Amount:** ${amount:,.2f}
- **Payment Date:** {payment_date}
- **Status:** {state}
- **Odoo ID:** {payment.get('id')}

## Actions Required

1. **Verify Payment**
   - Match payment to open invoice
   - Confirm amount matches invoice
   - Update invoice status

2. **Record in Accounting**
   - Reconcile payment in accounting system
   - Update customer balance

3. **Send Confirmation**
   - Send payment receipt to customer
   - Update accounts receivable

---
*Generated by Odoo Watcher on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

            task_path.write_text(task_content)
            logger.info(f"Created task: {task_filename}")

            # Send email notification if enabled and above threshold
            if amount >= NOTIFICATION_THRESHOLD:
                self._send_email_notification('payment', payment)

            # Save to Accounting/Payments
            self._save_to_accounting('payment', payment)

        except Exception as e:
            logger.error(f"Error processing payment: {e}")

    def _process_bill(self, bill: Dict):
        """Process vendor bill"""
        try:
            bill_name = bill.get('name', f'BILL-{bill.get("id")}')
            partner = bill.get('partner_id', [{}])[0]
            vendor_name = partner.get('name', 'Unknown') if isinstance(partner, dict) else 'Unknown'

            amount = bill.get('amount_total', 0)
            bill_date = bill.get('invoice_date', '')
            due_date = bill.get('invoice_date_due', '')
            state = bill.get('state', 'draft')

            # Create task file
            task_filename = f"ODOO_BILL_{bill_name.replace(' ', '_').replace('/', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            task_path = NEEDS_ACTION_PATH / task_filename

            task_content = f"""# Odoo Vendor Bill Received

**Source:** Odoo Accounting
**Priority:** Medium
**Type:** Bill Approval

## Bill Details

- **Bill Number:** {bill_name}
- **Vendor:** {vendor_name}
- **Amount:** ${amount:,.2f}
- **Bill Date:** {bill_date}
- **Due Date:** {due_date}
- **Status:** {state}
- **Odoo ID:** {bill.get('id')}

## Actions Required

1. **Review Bill**
   - Verify line items and quantities
   - Check pricing and terms
   - Confirm vendor information

2. **Approval**
   - Approve for payment
   - Schedule payment per terms

3. **Record Payment**
   - Process payment when due
   - Update accounts payable

---
*Generated by Odoo Watcher on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

            task_path.write_text(task_content)
            logger.info(f"Created task: {task_filename}")

            # Send email notification if enabled and above threshold
            if amount >= NOTIFICATION_THRESHOLD:
                self._send_email_notification('bill', bill)

            # Save to Accounting/Bills
            self._save_to_accounting('bill', bill)

        except Exception as e:
            logger.error(f"Error processing bill: {e}")

    def _save_to_accounting(self, item_type: str, item: Dict):
        """Save item to Accounting directory"""
        try:
            today = datetime.now().strftime('%Y-%m')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

            if item_type == 'invoice':
                filename = f'invoice_{item.get("id")}_{timestamp}.json'
                filepath = ACCOUNTING_PATH / 'Invoices' / filename
            elif item_type == 'payment':
                filename = f'payment_{item.get("id")}_{timestamp}.json'
                filepath = ACCOUNTING_PATH / 'Payments' / filename
            elif item_type == 'bill':
                filename = f'bill_{item.get("id")}_{timestamp}.json'
                filepath = ACCOUNTING_PATH / 'Bills' / filename
            else:
                logger.warning(f"Unknown item type: {item_type}")
                return

            # Save JSON with metadata
            data = {
                'odoo_type': item_type,
                'odoo_id': item.get('id'),
                'data': item,
                'watcher_timestamp': datetime.now().isoformat(),
                'synced_from': 'Odoo Watcher'
            }

            filepath.write_text(json.dumps(data, indent=2, default=str))
            logger.info(f"Saved to accounting: {filename}")

        except Exception as e:
            logger.error(f"Error saving to accounting: {e}")

    def _send_email_notification(self, notification_type: str, item_data: Dict) -> bool:
        """Send email notification via Gmail MCP server

        Args:
            notification_type: Type of notification (invoice, payment, bill)
            item_data: Dictionary with item details

        Returns:
            True if successful, False otherwise
        """
        if not NOTIFICATION_ENABLED:
            logger.debug("Email notifications disabled")
            return False

        if not NOTIFICATION_EMAIL:
            logger.warning("NOTIFICATION_EMAIL not set, skipping email notification")
            return False

        try:
            # Build email based on type
            if notification_type == 'invoice':
                subject = f"📄 New Invoice Created: {item_data.get('name', 'Unknown')}"
                body = self._format_invoice_email(item_data)
            elif notification_type == 'payment':
                subject = f"💰 Payment Received: {item_data.get('name', 'Unknown')}"
                body = self._format_payment_email(item_data)
            elif notification_type == 'bill':
                subject = f"📋 New Vendor Bill: {item_data.get('name', 'Unknown')}"
                body = self._format_bill_email(item_data)
            else:
                logger.warning(f"Unknown notification type: {notification_type}")
                return False

            # Create email task file for approval workflow
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            email_filename = f"EMAIL_ODOO_{notification_type.upper()}_{timestamp}.md"
            email_path = NEEDS_ACTION_PATH / email_filename

            email_content = f"""---
type: email_notification
source: odoo_watcher
notification_type: {notification_type}
priority: medium
to: {NOTIFICATION_EMAIL}
subject: {subject}
format: text
auto_approve: true
---

{body}
"""

            email_path.write_text(email_content, encoding='utf-8')
            logger.info(f"Email notification queued: {email_filename}")

            # Try to send immediately via Gmail MCP if available
            self._send_via_gmail_mcp(NOTIFICATION_EMAIL, subject, body)

            return True

        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
            return False

    def _format_invoice_email(self, invoice: Dict) -> str:
        """Format invoice notification email body"""
        invoice_name = invoice.get('name', 'Unknown')
        partner = invoice.get('partner_id', [{}])[0]
        partner_name = partner.get('name', 'Unknown') if isinstance(partner, dict) else 'Unknown'
        amount = invoice.get('amount_total', 0)
        invoice_date = invoice.get('invoice_date') or invoice.get('create_date', '')
        state = invoice.get('state', 'draft')

        return f"""A new invoice has been created in Odoo.

Invoice Details:
  Invoice Number: {invoice_name}
  Customer: {partner_name}
  Amount: ${amount:,.2f}
  Invoice Date: {invoice_date}
  Status: {state}
  Odoo ID: {invoice.get('id')}

Next Steps:
  - Review invoice in Odoo: http://localhost:8069/web#id={invoice.get('id')}&model=account.move
  - Check task file in Needs_Action/ for details
  - Invoice will be sent to customer after approval

---
Generated by Odoo Watcher
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

    def _format_payment_email(self, payment: Dict) -> str:
        """Format payment notification email body"""
        payment_name = payment.get('name', 'Unknown')
        partner = payment.get('partner_id', [{}])[0]
        partner_name = partner.get('name', 'Unknown') if isinstance(partner, dict) else 'Unknown'
        amount = payment.get('amount', 0)
        payment_date = payment.get('payment_date', '')
        state = payment.get('state', 'draft')

        return f"""A payment has been received in Odoo.

Payment Details:
  Payment Reference: {payment_name}
  Customer: {partner_name}
  Amount: ${amount:,.2f}
  Payment Date: {payment_date}
  Status: {state}
  Odoo ID: {payment.get('id')}

Next Steps:
  - Review payment in Odoo: http://localhost:8069/web#id={payment.get('id')}&model=account.payment
  - Reconcile with outstanding invoice if needed
  - Check task file in Needs_Action/ for details

---
Generated by Odoo Watcher
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

    def _format_bill_email(self, bill: Dict) -> str:
        """Format vendor bill notification email body"""
        bill_name = bill.get('name', 'Unknown')
        partner = bill.get('partner_id', [{}])[0]
        vendor_name = partner.get('name', 'Unknown') if isinstance(partner, dict) else 'Unknown'
        amount = bill.get('amount_total', 0)
        bill_date = bill.get('invoice_date', '')
        due_date = bill.get('invoice_date_due', '')
        state = bill.get('state', 'draft')

        return f"""A new vendor bill has been received in Odoo.

Bill Details:
  Bill Number: {bill_name}
  Vendor: {vendor_name}
  Amount: ${amount:,.2f}
  Bill Date: {bill_date}
  Due Date: {due_date}
  Status: {state}
  Odoo ID: {bill.get('id')}

Next Steps:
  - Review bill in Odoo: http://localhost:8069/web#id={bill.get('id')}&model=account.move
  - Approve for payment
  - Check task file in Needs_Action/ for details

---
Generated by Odoo Watcher
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

    def _send_via_gmail_mcp(self, to: str, subject: str, body: str) -> bool:
        """Send email directly via Gmail MCP server

        Args:
            to: Recipient email
            subject: Email subject
            body: Email body

        Returns:
            True if successful, False otherwise
        """
        try:
            mcp_server_path = VAULT_PATH / 'mcp-servers' / 'gmail-mcp' / 'dist' / 'index.js'

            if not mcp_server_path.exists():
                logger.debug(f"Gmail MCP server not found at: {mcp_server_path}")
                return False

            # Build MCP request
            request_data = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "send_email",
                    "arguments": {
                        "to": [to],
                        "subject": subject,
                        "body": body,
                        "isHtml": False
                    }
                }
            }

            # Call MCP server
            result = subprocess.run(
                ["node", str(mcp_server_path)],
                input=json.dumps(request_data) + "\n",
                capture_output=True,
                text=True,
                cwd=str(mcp_server_path.parent),
                timeout=30
            )

            if result.returncode == 0:
                try:
                    response = json.loads(result.stdout)
                    if "result" in response:
                        logger.info(f"✅ Email notification sent via Gmail MCP to {to}")
                        return True
                    else:
                        logger.warning(f"Gmail MCP returned error: {response.get('error')}")
                        return False
                except json.JSONDecodeError:
                    logger.warning("Could not parse Gmail MCP response")
                    return False
            else:
                logger.debug(f"Gmail MCP error: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.debug("Gmail MCP timeout")
            return False
        except Exception as e:
            logger.debug(f"Failed to send via Gmail MCP: {e}")
            return False

    def get_status(self) -> Dict:
        """Get watcher status"""
        return {
            'name': 'Odoo Watcher',
            'status': 'running' if self.running else 'stopped',
            'last_check': self.state.last_check,
            'check_interval': CHECK_INTERVAL,
            'state_file': str(STATE_FILE),
            'odoo_url': ODOO_URL,
            'odoo_db': ODOO_DB,
            'notifications_enabled': NOTIFICATION_ENABLED,
            'notification_email': NOTIFICATION_EMAIL if NOTIFICATION_EMAIL else 'Not configured',
            'notification_threshold': NOTIFICATION_THRESHOLD
        }

    def run_once(self) -> Dict[str, int]:
        """Run one monitoring cycle"""
        logger.info("=" * 60)
        logger.info("Starting Odoo monitoring cycle")

        results = {
            'invoices': 0,
            'payments': 0,
            'bills': 0
        }

        # Test connection
        if not self.test_connection():
            logger.error("Cannot connect to Odoo MCP server")
            return results

        # Monitor different document types
        results['invoices'] = self.monitor_invoices()
        results['payments'] = self.monitor_payments()
        results['bills'] = self.monitor_bills()

        # Update last check time
        self.state.update_last_check(datetime.now().isoformat())

        total_new = sum(results.values())
        logger.info(f"Monitoring cycle complete: {total_new} new items detected")
        logger.info(f"  - Invoices: {results['invoices']}")
        logger.info(f"  - Payments: {results['payments']}")
        logger.info(f"  - Bills: {results['bills']}")

        return results

    def start(self):
        """Start continuous monitoring"""
        self.running = True
        logger.info("Odoo Watcher started")
        logger.info(f"Check interval: {CHECK_INTERVAL} seconds")
        logger.info(f"Monitoring Odoo at: {ODOO_URL}")

        try:
            while self.running:
                self.run_once()
                logger.info(f"Next check in {CHECK_INTERVAL} seconds...")
                time.sleep(CHECK_INTERVAL)
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
            self.stop()

    def stop(self):
        """Stop monitoring"""
        self.running = False
        logger.info("Odoo Watcher stopped")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Odoo Watcher - Monitor Odoo ERP for accounting events')
    parser.add_argument('--once', action='store_true', help='Run once and exit')
    parser.add_argument('--test', action='store_true', help='Test connection to Odoo')

    args = parser.parse_args()

    watcher = OdooWatcher()

    if args.test:
        logger.info("Testing Odoo connection...")
        if watcher.test_connection():
            logger.info("[OK] Connection successful!")
            return 0
        else:
            logger.error("[ERROR] Connection failed!")
            return 1

    if args.once:
        results = watcher.run_once()
        logger.info(f"New items: {sum(results.values())}")
        return 0
    else:
        watcher.start()
        return 0


if __name__ == '__main__':
    sys.exit(main())
