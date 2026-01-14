#!/usr/bin/env python3
"""
Xero Watcher for Personal AI Employee

Monitors Xero accounting system for important financial events:
- New invoices created (awaiting payment)
- New bills received (money owed)
- Overdue invoices (collections needed)
- Large transactions requiring categorization
- Bank reconciliation items
- Payment received

Creates actionable files in Needs_Action folder for AI Employee to process.

Based on architecture from Requirements.md
Requires Xero OAuth 2.0 credentials.

Author: Personal AI Employee Project
Created: 2026-01-13
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from base_watcher import BaseWatcher

# Optional: Import xero library if available
try:
    from xero import Xero
    from xero.auth import OAuth2Credentials
    XERO_AVAILABLE = True
except ImportError:
    XERO_AVAILABLE = False
    print("Warning: xero library not installed. Install with: pip install pyxero")


class XeroWatcher(BaseWatcher):
    """
    Watcher for Xero accounting system.

    Monitors for:
    - New unpaid invoices
    - New bills to pay
    - Overdue invoices
    - Large uncategorized transactions
    - Payment receipts
    - Bank reconciliation items
    """

    def __init__(
        self,
        vault_path: str,
        check_interval: int = 300,  # 5 minutes default
        credentials_path: Optional[str] = None
    ):
        """
        Initialize Xero watcher.

        Args:
            vault_path: Path to Obsidian vault root
            check_interval: Seconds between checks (default: 300 = 5 min)
            credentials_path: Path to Xero OAuth credentials file
        """
        super().__init__(
            vault_path=vault_path,
            check_interval=check_interval,
            watcher_name="XeroWatcher"
        )

        # Xero-specific paths (credentials are at project root, not in vault)
        project_root = Path(self.vault_path).parent
        self.credentials_dir = project_root / 'watchers' / 'credentials'
        self.credentials_dir.mkdir(parents=True, exist_ok=True)

        self.credentials_path = credentials_path or (
            self.credentials_dir / 'xero_credentials.json'
        )
        self.token_path = self.credentials_dir / 'xero_token.json'

        # Configuration
        self.config = self._load_config()

        # Xero connection
        self.xero = None
        self._initialize_xero_connection()

        self.logger.info("Xero Watcher initialized")
        self.logger.info(f"  Monitoring: Invoices, Bills, Transactions")
        self.logger.info(f"  Alert threshold: ${self.config['large_transaction_threshold']}")

    def _load_config(self) -> Dict[str, Any]:
        """Load watcher configuration."""
        project_root = Path(self.vault_path).parent
        config_path = project_root / 'watchers' / 'xero_config.json'

        default_config = {
            'large_transaction_threshold': 500.00,  # Alert for transactions > $500
            'overdue_alert_days': 7,  # Alert for invoices overdue > 7 days
            'monitor_invoices': True,
            'monitor_bills': True,
            'monitor_payments': True,
            'monitor_bank_transactions': True,
            'monitor_overdue': True
        }

        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                self.logger.warning(f"Error loading config, using defaults: {e}")

        return default_config

    def _initialize_xero_connection(self):
        """Initialize connection to Xero API."""
        if not XERO_AVAILABLE:
            self.logger.warning("Xero library not available - using mock mode")
            self.xero = None
            return

        # Check for credentials
        if not self.credentials_path.exists():
            self.logger.warning(
                f"Xero credentials not found at {self.credentials_path}\n"
                "Please set up Xero OAuth credentials. See: xero_setup.md"
            )
            self.xero = None
            return

        try:
            # Load OAuth credentials
            with open(self.credentials_path, 'r') as f:
                creds_data = json.load(f)

            # Load or create token
            token_data = None
            if self.token_path.exists():
                with open(self.token_path, 'r') as f:
                    token_data = json.load(f)

            # Create OAuth2 credentials
            credentials = OAuth2Credentials(
                client_id=creds_data['client_id'],
                client_secret=creds_data['client_secret'],
                callback_uri=creds_data.get('redirect_uri', 'http://localhost:8080'),
                token=token_data
            )

            # Set tenant ID if available
            tenant_id = creds_data.get('tenant_id')
            if tenant_id:
                credentials.tenant_id = tenant_id
                self.logger.info(f"Using tenant: {creds_data.get('tenant_name', tenant_id)}")

            # Initialize Xero connection
            self.xero = Xero(credentials)

            # Save updated token
            self._save_token(credentials.token)

            self.logger.info("✓ Connected to Xero API")

        except Exception as e:
            self.logger.error(f"Failed to connect to Xero: {e}")
            self.logger.warning("Running in mock mode")
            self.xero = None

    def _save_token(self, token: Dict):
        """Save OAuth token for reuse."""
        try:
            with open(self.token_path, 'w') as f:
                json.dump(token, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving token: {e}")

    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check Xero for new financial events.

        Returns:
            List of financial events requiring action
        """
        events = []

        try:
            # Check different categories
            if self.config['monitor_invoices']:
                events.extend(self._check_new_invoices())

            if self.config['monitor_bills']:
                events.extend(self._check_new_bills())

            if self.config['monitor_payments']:
                events.extend(self._check_payments_received())

            if self.config['monitor_overdue']:
                events.extend(self._check_overdue_invoices())

            if self.config['monitor_bank_transactions']:
                events.extend(self._check_uncategorized_transactions())

            # Filter out already processed events
            new_events = [
                event for event in events
                if not self.is_processed(event['id'])
            ]

            if new_events:
                self.logger.info(f"Found {len(new_events)} new financial event(s)")

            return new_events

        except Exception as e:
            self.logger.error(f"Error checking Xero: {e}", exc_info=True)
            return []

    def _check_new_invoices(self) -> List[Dict]:
        """Check for new unpaid invoices."""
        events = []

        try:
            if self.xero:
                # Real Xero API call
                invoices = self.xero.invoices.filter(
                    Status='AUTHORISED',
                    Type='ACCREC'  # Accounts Receivable (customer invoices)
                )
            else:
                # Mock data for testing
                invoices = self._get_mock_invoices()

            for invoice in invoices:
                invoice_id = invoice.get('InvoiceID') or invoice.get('id')

                # Check if this is new (within last check_interval)
                invoice_date = self._parse_date(invoice.get('Date') or invoice.get('date'))
                if self._is_recent(invoice_date):
                    events.append({
                        'id': f"invoice_{invoice_id}",
                        'type': 'new_invoice',
                        'event_type': 'new_invoice',
                        'invoice_id': invoice_id,
                        'invoice_number': invoice.get('InvoiceNumber') or invoice.get('number'),
                        'customer': invoice.get('Contact', {}).get('Name') or invoice.get('customer'),
                        'amount': invoice.get('Total') or invoice.get('amount'),
                        'due_date': invoice.get('DueDate') or invoice.get('due_date'),
                        'date': invoice_date,
                        'status': invoice.get('Status') or invoice.get('status')
                    })

        except Exception as e:
            self.logger.error(f"Error checking invoices: {e}")

        return events

    def _check_new_bills(self) -> List[Dict]:
        """Check for new bills to pay."""
        events = []

        try:
            if self.xero:
                # Real Xero API call
                bills = self.xero.invoices.filter(
                    Status='AUTHORISED',
                    Type='ACCPAY'  # Accounts Payable (bills)
                )
            else:
                # Mock data
                bills = self._get_mock_bills()

            for bill in bills:
                bill_id = bill.get('InvoiceID') or bill.get('id')
                bill_date = self._parse_date(bill.get('Date') or bill.get('date'))

                if self._is_recent(bill_date):
                    events.append({
                        'id': f"bill_{bill_id}",
                        'type': 'new_bill',
                        'event_type': 'new_bill',
                        'bill_id': bill_id,
                        'bill_number': bill.get('InvoiceNumber') or bill.get('number'),
                        'vendor': bill.get('Contact', {}).get('Name') or bill.get('vendor'),
                        'amount': bill.get('Total') or bill.get('amount'),
                        'due_date': bill.get('DueDate') or bill.get('due_date'),
                        'date': bill_date
                    })

        except Exception as e:
            self.logger.error(f"Error checking bills: {e}")

        return events

    def _check_payments_received(self) -> List[Dict]:
        """Check for payments received."""
        events = []

        try:
            if self.xero:
                # Real API: Check bank transactions for deposits
                transactions = self.xero.banktransactions.filter(
                    Type='RECEIVE',
                    Status='AUTHORISED'
                )
            else:
                # Mock data
                transactions = self._get_mock_payments()

            for tx in transactions:
                tx_id = tx.get('BankTransactionID') or tx.get('id')
                tx_date = self._parse_date(tx.get('Date') or tx.get('date'))
                amount = tx.get('Total') or tx.get('amount')

                # Only alert for significant payments
                if self._is_recent(tx_date) and amount >= self.config['large_transaction_threshold']:
                    events.append({
                        'id': f"payment_{tx_id}",
                        'type': 'payment_received',
                        'event_type': 'payment_received',
                        'transaction_id': tx_id,
                        'customer': tx.get('Contact', {}).get('Name') or tx.get('from'),
                        'amount': amount,
                        'date': tx_date,
                        'reference': tx.get('Reference') or tx.get('reference')
                    })

        except Exception as e:
            self.logger.error(f"Error checking payments: {e}")

        return events

    def _check_overdue_invoices(self) -> List[Dict]:
        """Check for overdue invoices."""
        events = []

        try:
            if self.xero:
                # Real API call
                invoices = self.xero.invoices.filter(
                    Status='AUTHORISED',
                    Type='ACCREC'
                )
            else:
                invoices = self._get_mock_invoices()

            today = datetime.now().date()

            for invoice in invoices:
                due_date_str = invoice.get('DueDate') or invoice.get('due_date')
                if not due_date_str:
                    continue

                due_date = self._parse_date(due_date_str)
                days_overdue = (today - due_date).days

                # Alert if overdue beyond threshold
                if days_overdue >= self.config['overdue_alert_days']:
                    invoice_id = invoice.get('InvoiceID') or invoice.get('id')

                    events.append({
                        'id': f"overdue_{invoice_id}",
                        'type': 'overdue_invoice',
                        'event_type': 'overdue_invoice',
                        'invoice_id': invoice_id,
                        'invoice_number': invoice.get('InvoiceNumber') or invoice.get('number'),
                        'customer': invoice.get('Contact', {}).get('Name') or invoice.get('customer'),
                        'amount': invoice.get('AmountDue') or invoice.get('amount'),
                        'due_date': due_date_str,
                        'days_overdue': days_overdue
                    })

        except Exception as e:
            self.logger.error(f"Error checking overdue invoices: {e}")

        return events

    def _check_uncategorized_transactions(self) -> List[Dict]:
        """Check for large uncategorized bank transactions."""
        events = []

        try:
            if self.xero:
                # Get recent bank transactions
                transactions = self.xero.banktransactions.filter(
                    Status='AUTHORISED'
                )
            else:
                transactions = self._get_mock_transactions()

            for tx in transactions:
                tx_id = tx.get('BankTransactionID') or tx.get('id')
                amount = abs(tx.get('Total') or tx.get('amount', 0))

                # Check if large and possibly uncategorized
                if amount >= self.config['large_transaction_threshold']:
                    tx_date = self._parse_date(tx.get('Date') or tx.get('date'))

                    if self._is_recent(tx_date):
                        events.append({
                            'id': f"transaction_{tx_id}",
                            'type': 'large_transaction',
                            'event_type': 'large_transaction',
                            'transaction_id': tx_id,
                            'amount': tx.get('Total') or tx.get('amount'),
                            'contact': tx.get('Contact', {}).get('Name') or tx.get('contact'),
                            'date': tx_date,
                            'reference': tx.get('Reference') or tx.get('reference'),
                            'description': tx.get('LineItems', [{}])[0].get('Description') if tx.get('LineItems') else tx.get('description')
                        })

        except Exception as e:
            self.logger.error(f"Error checking transactions: {e}")

        return events

    def create_action_file(self, event: Dict[str, Any]) -> Optional[Path]:
        """
        Create actionable file for financial event.

        Args:
            event: Financial event dictionary

        Returns:
            Path to created file
        """
        try:
            # Create filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            event_type = event['event_type']
            filename = f"xero_{event_type}_{timestamp}.md"
            filepath = self.needs_action / filename

            # Create markdown content based on event type
            content = self._create_event_content(event)

            # Write file
            filepath.write_text(content, encoding='utf-8')

            # Mark as processed
            self.mark_as_processed(event['id'])

            # Log action
            self.log_action(
                action_type=f"xero_{event_type}",
                details={
                    'event_id': event['id'],
                    'type': event_type,
                    'amount': event.get('amount'),
                    'description': self._get_event_description(event)
                },
                task_filename=filename
            )

            return filepath

        except Exception as e:
            self.logger.error(f"Error creating action file: {e}", exc_info=True)
            return None

    def _create_event_content(self, event: Dict) -> str:
        """Create markdown content for event."""
        event_type = event['event_type']
        timestamp = datetime.now().isoformat()

        # Common frontmatter
        content = f"""---
type: xero_event
event_type: {event_type}
source: xero_watcher
created: {timestamp}
status: pending
priority: high
"""

        # Add event-specific fields
        if 'invoice_id' in event:
            content += f"invoice_id: {event['invoice_id']}\n"
        if 'bill_id' in event:
            content += f"bill_id: {event['bill_id']}\n"
        if 'transaction_id' in event:
            content += f"transaction_id: {event['transaction_id']}\n"

        content += "---\n\n"

        # Event-specific content
        if event_type == 'new_invoice':
            content += f"""# New Invoice Created - {event.get('invoice_number')}

## Invoice Details
- **Customer:** {event.get('customer')}
- **Amount:** ${event.get('amount', 0):,.2f}
- **Due Date:** {event.get('due_date')}
- **Status:** {event.get('status')}
- **Date:** {event.get('date')}

## Action Required
A new invoice has been created and awaiting payment.

**Suggested Actions:**
1. Verify invoice details are correct
2. Send invoice to customer if not already sent
3. Add to accounts receivable tracking
4. Set up payment reminder for due date
5. Update cash flow projections

**Next Steps:**
- [ ] Verify invoice accuracy
- [ ] Confirm customer contact information
- [ ] Schedule payment follow-up
- [ ] Update financial dashboard
"""

        elif event_type == 'new_bill':
            content += f"""# New Bill Received - {event.get('bill_number')}

## Bill Details
- **Vendor:** {event.get('vendor')}
- **Amount:** ${event.get('amount', 0):,.2f}
- **Due Date:** {event.get('due_date')}
- **Date:** {event.get('date')}

## Action Required
A new bill has been received and needs to be paid.

**Suggested Actions:**
1. Review and approve bill
2. Schedule payment before due date
3. Categorize expense properly
4. Check budget impact
5. Ensure sufficient cash flow

**Next Steps:**
- [ ] Review bill details and receipts
- [ ] Approve or reject bill
- [ ] Schedule payment
- [ ] Update expense tracking
- [ ] Check cash flow impact
"""

        elif event_type == 'payment_received':
            content += f"""# Payment Received - ${event.get('amount', 0):,.2f}

## Payment Details
- **From:** {event.get('customer')}
- **Amount:** ${event.get('amount', 0):,.2f}
- **Date:** {event.get('date')}
- **Reference:** {event.get('reference')}

## Action Required
A significant payment has been received.

**Suggested Actions:**
1. Match payment to invoice(s)
2. Update customer account
3. Send payment confirmation
4. Update cash flow projections
5. Record in financial reports

**Next Steps:**
- [ ] Match to outstanding invoices
- [ ] Send thank you / receipt
- [ ] Update accounts receivable
- [ ] Update cash flow forecast
- [ ] Record in monthly reports
"""

        elif event_type == 'overdue_invoice':
            content += f"""# Overdue Invoice Alert - {event.get('invoice_number')}

## Invoice Details
- **Customer:** {event.get('customer')}
- **Amount Due:** ${event.get('amount', 0):,.2f}
- **Due Date:** {event.get('due_date')}
- **Days Overdue:** {event.get('days_overdue')}

## Action Required
This invoice is overdue and requires collection action.

**Suggested Actions:**
1. Send payment reminder to customer
2. Call customer to follow up
3. Offer payment plan if needed
4. Apply late fees if applicable
5. Consider collections if severely overdue

**Next Steps:**
- [ ] Send payment reminder email
- [ ] Follow up with phone call
- [ ] Check customer payment history
- [ ] Offer payment options
- [ ] Escalate if no response
"""

        elif event_type == 'large_transaction':
            content += f"""# Large Transaction Detected - ${abs(event.get('amount', 0)):,.2f}

## Transaction Details
- **Amount:** ${event.get('amount', 0):,.2f}
- **Contact:** {event.get('contact')}
- **Date:** {event.get('date')}
- **Reference:** {event.get('reference')}
- **Description:** {event.get('description')}

## Action Required
A large transaction requires review and categorization.

**Suggested Actions:**
1. Verify transaction is legitimate
2. Categorize expense/income properly
3. Attach receipt or documentation
4. Update budget tracking
5. Flag for accountant review if needed

**Next Steps:**
- [ ] Verify transaction legitimacy
- [ ] Assign proper category
- [ ] Attach supporting documents
- [ ] Update budget impact
- [ ] Add notes for tax purposes
"""

        content += f"\n---\n\n**Xero Event ID:** {event['id']}\n"
        content += f"**Detected:** {timestamp}\n"

        return content

    def _get_event_description(self, event: Dict) -> str:
        """Get short description of event."""
        event_type = event['event_type']

        if event_type == 'new_invoice':
            return f"Invoice {event.get('invoice_number')} - {event.get('customer')} - ${event.get('amount', 0):,.2f}"
        elif event_type == 'new_bill':
            return f"Bill {event.get('bill_number')} - {event.get('vendor')} - ${event.get('amount', 0):,.2f}"
        elif event_type == 'payment_received':
            return f"Payment from {event.get('customer')} - ${event.get('amount', 0):,.2f}"
        elif event_type == 'overdue_invoice':
            return f"Overdue: {event.get('invoice_number')} - {event.get('days_overdue')} days"
        elif event_type == 'large_transaction':
            return f"Transaction: {event.get('contact')} - ${abs(event.get('amount', 0)):,.2f}"

        return "Financial event"

    def _parse_date(self, date_str: Any) -> datetime.date:
        """Parse date from various formats."""
        if isinstance(date_str, datetime):
            return date_str.date()

        if isinstance(date_str, str):
            try:
                # Try ISO format
                return datetime.fromisoformat(date_str.split('T')[0]).date()
            except:
                try:
                    # Try common formats
                    for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y']:
                        try:
                            return datetime.strptime(date_str, fmt).date()
                        except:
                            continue
                except:
                    pass

        # Default to today if can't parse
        return datetime.now().date()

    def _is_recent(self, date: datetime.date) -> bool:
        """Check if date is within the check interval."""
        now = datetime.now().date()
        days_ago = (now - date).days

        # Consider events from last check interval + 1 day buffer
        interval_days = (self.check_interval / 86400) + 1

        return days_ago <= interval_days

    # Mock data methods for testing

    def _get_mock_invoices(self) -> List[Dict]:
        """Get mock invoice data for testing."""
        return [
            {
                'id': 'INV-2026-001',
                'number': 'INV-2026-001',
                'customer': 'Acme Corp',
                'amount': 2500.00,
                'date': datetime.now().isoformat(),
                'due_date': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
                'status': 'AUTHORISED'
            }
        ]

    def _get_mock_bills(self) -> List[Dict]:
        """Get mock bill data for testing."""
        return [
            {
                'id': 'BILL-2026-001',
                'number': 'BILL-2026-001',
                'vendor': 'Office Supplies Co',
                'amount': 350.00,
                'date': datetime.now().isoformat(),
                'due_date': (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')
            }
        ]

    def _get_mock_payments(self) -> List[Dict]:
        """Get mock payment data for testing."""
        return [
            {
                'id': 'PAY-2026-001',
                'from': 'Client XYZ',
                'amount': 1500.00,
                'date': datetime.now().isoformat(),
                'reference': 'Invoice payment'
            }
        ]

    def _get_mock_transactions(self) -> List[Dict]:
        """Get mock transaction data for testing."""
        return [
            {
                'id': 'TX-2026-001',
                'amount': -750.00,
                'contact': 'Software Vendor',
                'date': datetime.now().isoformat(),
                'reference': 'Annual license',
                'description': 'Software licensing fee'
            }
        ]


def main():
    """Main entry point for Xero watcher."""
    # Determine vault path
    vault_path = Path(__file__).parent.parent / "AI_Employee_Vault"

    print("=" * 70)
    print("Personal AI Employee - Xero Watcher")
    print("=" * 70)
    print(f"Vault: {vault_path}")
    print(f"Monitoring: Invoices, Bills, Payments, Transactions")
    print(f"Press Ctrl+C to stop")
    print("=" * 70)
    print()

    # Create and run watcher
    try:
        watcher = XeroWatcher(
            vault_path=str(vault_path),
            check_interval=300  # Check every 5 minutes
        )
        watcher.run()

    except KeyboardInterrupt:
        print("\n\nXero watcher stopped by user")
        sys.exit(0)

    except Exception as e:
        print(f"\n\nFatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
