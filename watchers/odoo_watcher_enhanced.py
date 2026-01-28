#!/usr/bin/env python3
"""
Odoo Watcher Enhanced - Monitors Odoo ERP for accounting events

Improvements:
- Circuit breaker pattern for API failures
- Redis caching for deduplication
- Configurable polling intervals with exponential backoff
- Better error handling and recovery
- Performance metrics and logging

Author: AI Employee System
Created: 2026-01-18
Enhanced: 2026-01-26
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
from dataclasses import dataclass, field
from enum import Enum
from collections import deque

try:
    import requests
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "requests"], check=True)
    import requests

try:
    import redis
except ImportError:
    redis = None

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure logging
LOG_DIR = Path(__file__).parent.parent / 'Logs'
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / f'odoo_watcher_enhanced_{datetime.now().strftime("%Y-%m-%d")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("odoo_watcher_enhanced")


# =============================================================================
# Configuration
# =============================================================================

@dataclass
class WatcherConfig:
    """Configuration for Odoo Watcher"""
    odoo_mcp_url: str = os.getenv('ODOO_MCP_URL', 'http://localhost:8000')
    odoo_url: str = os.getenv('ODOO_URL', 'http://localhost:8069')
    odoo_db: str = os.getenv('ODOO_DB', 'odoo')
    odoo_username: str = os.getenv('ODOO_USERNAME', 'admin')
    odoo_api_key: str = os.getenv('ODOO_API_KEY', '')

    check_interval: int = int(os.getenv('ODOO_CHECK_INTERVAL', '300'))  # 5 minutes
    timeout: int = int(os.getenv('ODOO_MCP_TIMEOUT', '30'))

    # Circuit breaker settings
    cb_failure_threshold: int = int(os.getenv('ODOO_CB_THRESHOLD', '5'))
    cb_timeout: int = int(os.getenv('ODOO_CB_TIMEOUT', '120'))

    # Retry settings
    max_retries: int = int(os.getenv('ODOO_MAX_RETRIES', '3'))
    retry_delay: float = float(os.getenv('ODOO_RETRY_DELAY', '2.0'))

    # Cache settings
    enable_cache: bool = os.getenv('ODOO_ENABLE_CACHE', 'true').lower() == 'true'
    redis_host: str = os.getenv('REDIS_HOST', 'localhost')
    redis_port: int = int(os.getenv('REDIS_PORT', '6379'))
    cache_ttl: int = int(os.getenv('ODOO_CACHE_TTL', '600'))  # 10 minutes

    # Notification settings
    notification_enabled: bool = os.getenv('NOTIFICATION_ENABLED', 'true').lower() == 'true'
    notification_email: str = os.getenv('NOTIFICATION_EMAIL', '')
    notification_threshold: float = float(os.getenv('NOTIFICATION_THRESHOLD', '0'))

    # Paths
    vault_path: Path = field(default_factory=lambda: Path(__file__).parent.parent)
    needs_action_path: Path = field(default_factory=lambda: Path(__file__).parent.parent / 'Needs_Action')
    accounting_path: Path = field(default_factory=lambda: Path(__file__).parent.parent / 'Accounting')
    state_file: Path = field(default_factory=lambda: lambda: LOG_DIR / 'odoo_watcher_enhanced_state.json')


# =============================================================================
# Circuit Breaker
# =============================================================================

class CircuitBreakerState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """Circuit breaker for Odoo API calls"""

    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.success_count = 0
        self.logger = logging.getLogger("circuit_breaker")

    def record_success(self):
        self.failure_count = 0
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= 2:
                self.state = CircuitBreakerState.CLOSED
                self.success_count = 0
                self.logger.info("Circuit breaker: CLOSED (recovery confirmed)")

    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.failure_count >= self.failure_threshold:
            if self.state != CircuitBreakerState.OPEN:
                self.state = CircuitBreakerState.OPEN
                self.logger.warning(f"Circuit breaker: OPEN ({self.failure_count} failures)")

    def can_execute(self) -> bool:
        if self.state == CircuitBreakerState.CLOSED:
            return True

        if self.state == CircuitBreakerState.OPEN:
            if self.last_failure_time and \
               (datetime.now() - self.last_failure_time).total_seconds() >= self.timeout:
                self.state = CircuitBreakerState.HALF_OPEN
                self.logger.info("Circuit breaker: HALF_OPEN (testing recovery)")
                return True
            return False

        return True  # HALF_OPEN

    def reset(self):
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.success_count = 0


# =============================================================================
# Cache Manager
# =============================================================================

class CacheManager:
    """Redis cache for deduplication"""

    def __init__(self, config: WatcherConfig):
        self.config = config
        self.enabled = config.enable_cache and redis is not None
        self.client = None

        if self.enabled:
            try:
                self.client = redis.Redis(
                    host=config.redis_host,
                    port=config.redis_port,
                    db=0,
                    decode_responses=True,
                    socket_connect_timeout=2,
                    socket_timeout=2
                )
                self.client.ping()
                logger.info(f"Cache enabled: Redis at {config.redis_host}:{config.redis_port}")
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}. Caching disabled.")
                self.enabled = False

    def is_processed(self, item_type: str, item_id: int) -> bool:
        """Check if item was already processed"""
        if not self.enabled:
            return False

        try:
            key = f"odoo_watcher:processed:{item_type}:{item_id}"
            return self.client.exists(key) > 0
        except Exception as e:
            logger.debug(f"Cache check error: {e}")
            return False

    def mark_processed(self, item_type: str, item_id: int, ttl: Optional[int] = None):
        """Mark item as processed"""
        if not self.enabled:
            return

        try:
            key = f"odoo_watcher:processed:{item_type}:{item_id}"
            ttl = ttl or self.config.cache_ttl
            self.client.setex(key, ttl, str(datetime.now().isoformat()))
        except Exception as e:
            logger.debug(f"Cache set error: {e}")

    def get_stats(self) -> Dict:
        """Get cache statistics"""
        if not self.enabled:
            return {"enabled": False}

        try:
            info = self.client.info("stats")
            return {
                "enabled": True,
                "total_keys": self.client.dbsize(),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0)
            }
        except Exception as e:
            return {"enabled": True, "error": str(e)}


# =============================================================================
# State Management
# =============================================================================

class OdooWatcherState:
    """Manages watcher state for detecting new/changed items"""

    def __init__(self, state_file: Path):
        self.state_file = state_file
        self.state = self.load_state()
        self.last_check = self.state.get('last_check', None)

        # Track processed items in memory for fast lookup
        self.processed_invoices = set(self.state.get('processed_invoices', []))
        self.processed_payments = set(self.state.get('processed_payments', []))
        self.processed_bills = set(self.state.get('processed_bills', []))

        # Metrics
        self.total_processed = self.state.get('total_processed', 0)
        self.total_errors = self.state.get('total_errors', 0)

    def load_state(self) -> Dict:
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load state: {e}")
        return {
            'processed_invoices': [],
            'processed_payments': [],
            'processed_bills': [],
            'last_check': None,
            'total_processed': 0,
            'total_errors': 0
        }

    def save_state(self):
        try:
            # Only persist IDs (not full sets) to keep file small
            self.state['processed_invoices'] = list(self.processed_invoices)[-1000:]  # Keep last 1000
            self.state['processed_payments'] = list(self.processed_payments)[-1000:]
            self.state['processed_bills'] = list(self.processed_bills)[-1000:]
            self.state['total_processed'] = self.total_processed
            self.state['total_errors'] = self.total_errors

            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save state: {e}")

    def is_processed(self, item_type: str, item_id: int, cache: Optional[CacheManager] = None) -> bool:
        # Check cache first
        if cache and cache.is_processed(item_type, item_id):
            return True

        # Check memory
        if item_type == 'invoices':
            return item_id in self.processed_invoices
        elif item_type == 'payments':
            return item_id in self.processed_payments
        elif item_type == 'bills':
            return item_id in self.processed_bills
        return False

    def mark_processed(self, item_type: str, item_id: int, cache: Optional[CacheManager] = None):
        if item_type == 'invoices':
            self.processed_invoices.add(item_id)
        elif item_type == 'payments':
            self.processed_payments.add(item_id)
        elif item_type == 'bills':
            self.processed_bills.add(item_id)

        self.total_processed += 1
        self.save_state()

        # Also mark in cache
        if cache:
            cache.mark_processed(item_type, item_id)

    def update_last_check(self, timestamp: str):
        self.state['last_check'] = timestamp
        self.save_state()

    def get_metrics(self) -> Dict:
        return {
            "last_check": self.last_check,
            "total_processed": self.total_processed,
            "total_errors": self.total_errors,
            "processed_invoices_count": len(self.processed_invoices),
            "processed_payments_count": len(self.processed_payments),
            "processed_bills_count": len(self.processed_bills)
        }


# =============================================================================
# Odoo MCP Client with Retry
# =============================================================================

class OdooMCPClientEnhanced:
    """Enhanced client for Odoo MCP Server with retry logic"""

    def __init__(self, base_url: str, config: WatcherConfig):
        self.base_url = base_url
        self.config = config
        self.request_id = 0
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=config.cb_failure_threshold,
            timeout=config.cb_timeout
        )

    def _call_mcp(self, tool_name: str, arguments: Dict,
                 use_cache: bool = False) -> Optional[Any]:
        """Call MCP tool via HTTP with retry logic"""
        self.request_id += 1

        # Check circuit breaker
        if not self.circuit_breaker.can_execute():
            logger.warning("Circuit breaker OPEN - skipping Odoo API call")
            return None

        delay = self.config.retry_delay

        for attempt in range(self.config.max_retries):
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
                    timeout=self.config.timeout
                )
                response.raise_for_status()
                data = response.json()

                if 'error' in data:
                    raise Exception(f"MCP Error: {data['error']}")

                result = data.get('result')
                self.circuit_breaker.record_success()
                return result

            except requests.exceptions.Timeout:
                logger.warning(f"Timeout on attempt {attempt + 1}")
            except requests.exceptions.ConnectionError:
                logger.warning(f"Connection error on attempt {attempt + 1}")
            except Exception as e:
                logger.error(f"Error on attempt {attempt + 1}: {e}")
                if attempt == 0:
                    self.circuit_breaker.record_failure()

            # Retry with backoff
            if attempt < self.config.max_retries - 1:
                time.sleep(delay * (2 ** attempt))

        # All retries failed
        self.circuit_breaker.record_failure()
        return None

    def search_records(self, model: str, domain: Optional[List] = None,
                      fields: Optional[List[str]] = None, limit: int = 100,
                      offset: int = 0) -> List[Dict]:
        args = {
            'model': model,
            'domain': domain or [],
            'fields': fields or [],
            'limit': limit,
            'offset': offset
        }

        result = self._call_mcp('search_records', args)
        if result and isinstance(result, dict) and 'records' in result:
            return result['records']
        elif result and isinstance(result, list):
            return result
        return []

    def get_record(self, model: str, res_id: int) -> Optional[Dict]:
        result = self._call_mcp('get_record', {
            'model': model,
            'res_id': res_id
        })
        if result and isinstance(result, dict) and 'record' in result:
            return result['record']
        return result

    def execute_method(self, model: str, method: str, args: List = None) -> Any:
        call_args = {
            'model': model,
            'method': method
        }
        if args:
            call_args['args'] = args

        return self._call_mcp('execute_method', call_args)

    def reset_circuit_breaker(self):
        """Reset circuit breaker (for testing/recovery)"""
        self.circuit_breaker.reset()
        logger.info("Circuit breaker reset")


# =============================================================================
# Enhanced Odoo Watcher
# =============================================================================

class OdooWatcherEnhanced:
    """Enhanced Odoo Watcher with caching and circuit breaker"""

    def __init__(self, config: Optional[WatcherConfig] = None):
        self.config = config or WatcherConfig()
        self.client = OdooMCPClientEnhanced(self.config.odoo_mcp_url, self.config)
        self.state = OdooWatcherState(self.config.state_file)
        self.cache = CacheManager(self.config)
        self.running = False

        # Create directories
        self.config.accounting_path.mkdir(exist_ok=True)
        (self.config.accounting_path / 'Invoices').mkdir(exist_ok=True)
        (self.config.accounting_path / 'Payments').mkdir(exist_ok=True)
        (self.config.accounting_path / 'Bills').mkdir(exist_ok=True)
        (self.config.accounting_path / 'Partners').mkdir(exist_ok=True)

    def test_connection(self) -> bool:
        """Test connection to Odoo MCP server"""
        try:
            result = self.client.search_records('res.users', [], [['id', '=', 1]], limit=1)
            return result is not None and len(result) > 0
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

    def monitor_invoices(self) -> int:
        """Monitor for new customer invoices"""
        logger.info("Checking for new invoices...")

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
            if not self.state.is_processed('invoices', invoice_id, self.cache):
                logger.info(f"New invoice detected: {invoice.get('name')}")

                self._process_invoice(invoice)
                self.state.mark_processed('invoices', invoice_id, self.cache)
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
            if not self.state.is_processed('payments', payment_id, self.cache):
                logger.info(f"New payment detected: {payment.get('name')}")

                self._process_payment(payment)
                self.state.mark_processed('payments', payment_id, self.cache)
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
            if not self.state.is_processed('bills', bill_id, self.cache):
                logger.info(f"New vendor bill detected: {bill.get('name')}")

                self._process_bill(bill)
                self.state.mark_processed('bills', bill_id, self.cache)
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

            task_filename = f"ODOO_INVOICE_{invoice_name.replace(' ', '_').replace('/', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            task_path = self.config.needs_action_path / task_filename

            task_content = f"""---
type: invoice_review
source: odoo_watcher
priority: high
---

# Odoo Invoice Received

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

---
*Generated by Odoo Watcher Enhanced on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

            task_path.write_text(task_content)
            logger.info(f"Created task: {task_filename}")

            if amount >= self.config.notification_threshold:
                self._send_email_notification('invoice', invoice)

            self._save_to_accounting('invoice', invoice)

        except Exception as e:
            logger.error(f"Error processing invoice: {e}")
            self.state.total_errors += 1

    def _process_payment(self, payment: Dict):
        """Process payment received"""
        try:
            payment_name = payment.get('name', f'PAY-{payment.get("id")}')
            partner = payment.get('partner_id', [{}])[0]
            partner_name = partner.get('name', 'Unknown') if isinstance(partner, dict) else 'Unknown'

            amount = payment.get('amount', 0)
            payment_date = payment.get('payment_date', '')
            state = payment.get('state', 'draft')

            task_filename = f"ODOO_PAYMENT_{payment_name.replace(' ', '_').replace('/', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            task_path = self.config.needs_action_path / task_filename

            task_content = f"""---
type: payment_recording
source: odoo_watcher
priority: medium
---

# Odoo Payment Received

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
*Generated by Odoo Watcher Enhanced on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

            task_path.write_text(task_content)
            logger.info(f"Created task: {task_filename}")

            if amount >= self.config.notification_threshold:
                self._send_email_notification('payment', payment)

            self._save_to_accounting('payment', payment)

        except Exception as e:
            logger.error(f"Error processing payment: {e}")
            self.state.total_errors += 1

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

            task_filename = f"ODOO_BILL_{bill_name.replace(' ', '_').replace('/', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            task_path = self.config.needs_action_path / task_filename

            task_content = f"""---
type: bill_approval
source: odoo_watcher
priority: medium
---

# Odoo Vendor Bill Received

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
*Generated by Odoo Watcher Enhanced on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

            task_path.write_text(task_content)
            logger.info(f"Created task: {task_filename}")

            if amount >= self.config.notification_threshold:
                self._send_email_notification('bill', bill)

            self._save_to_accounting('bill', bill)

        except Exception as e:
            logger.error(f"Error processing bill: {e}")
            self.state.total_errors += 1

    def _save_to_accounting(self, item_type: str, item: Dict):
        """Save item to Accounting directory"""
        try:
            today = datetime.now().strftime('%Y-%m')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

            if item_type == 'invoice':
                filename = f'invoice_{item.get("id")}_{timestamp}.json'
                filepath = self.config.accounting_path / 'Invoices' / filename
            elif item_type == 'payment':
                filename = f'payment_{item.get("id")}_{timestamp}.json'
                filepath = self.config.accounting_path / 'Payments' / filename
            elif item_type == 'bill':
                filename = f'bill_{item.get("id")}_{timestamp}.json'
                filepath = self.config.accounting_path / 'Bills' / filename
            else:
                logger.warning(f"Unknown item type: {item_type}")
                return

            data = {
                'odoo_type': item_type,
                'odoo_id': item.get('id'),
                'data': item,
                'watcher_timestamp': datetime.now().isoformat(),
                'synced_from': 'Odoo Watcher Enhanced'
            }

            filepath.write_text(json.dumps(data, indent=2, default=str))
            logger.info(f"Saved to accounting: {filename}")

        except Exception as e:
            logger.error(f"Error saving to accounting: {e}")

    def _send_email_notification(self, notification_type: str, item_data: Dict) -> bool:
        """Send email notification"""
        if not self.config.notification_enabled:
            return False

        if not self.config.notification_email:
            logger.warning("NOTIFICATION_EMAIL not set")
            return False

        try:
            if notification_type == 'invoice':
                subject = f"[Odoo] New Invoice: {item_data.get('name', 'Unknown')}"
                body = f"New invoice ${item_data.get('amount_total', 0):,.2f} from {item_data.get('partner_id', [{}])[0].get('name', 'Unknown')}"
            elif notification_type == 'payment':
                subject = f"[Odoo] Payment Received: {item_data.get('name', 'Unknown')}"
                body = f"Payment ${item_data.get('amount', 0):,.2f} received"
            else:
                subject = f"[Odoo] New {notification_type.title()}"
                body = f"New {notification_type} detected"

            # Create email task
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            email_filename = f"EMAIL_ODOO_{notification_type.upper()}_{timestamp}.md"
            email_path = self.config.needs_action_path / email_filename

            email_content = f"""---
type: email_notification
source: odoo_watcher_enhanced
priority: medium
to: {self.config.notification_email}
subject: {subject}
---

{body}

View in Odoo: {self.config.odoo_url}/web#id={item_data.get('id')}
"""

            email_path.write_text(email_content)
            logger.info(f"Email notification queued: {email_filename}")
            return True

        except Exception as e:
            logger.error(f"Failed to queue email notification: {e}")
            return False

    def get_status(self) -> Dict:
        """Get watcher status"""
        return {
            'name': 'Odoo Watcher Enhanced',
            'status': 'running' if self.running else 'stopped',
            'check_interval': self.config.check_interval,
            'odoo_url': self.config.odoo_url,
            'notifications_enabled': self.config.notification_enabled,
            'cache_enabled': self.cache.enabled,
            'circuit_breaker_state': self.client.circuit_breaker.state.value,
            **self.state.get_metrics()
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

        if not self.test_connection():
            logger.error("Cannot connect to Odoo MCP server")
            return results

        results['invoices'] = self.monitor_invoices()
        results['payments'] = self.monitor_payments()
        results['bills'] = self.monitor_bills()

        self.state.update_last_check(datetime.now().isoformat())

        total_new = sum(results.values())
        logger.info(f"Monitoring cycle complete: {total_new} new items detected")

        return results

    def start(self):
        """Start continuous monitoring"""
        self.running = True
        logger.info("Odoo Watcher Enhanced started")
        logger.info(f"Check interval: {self.config.check_interval} seconds")
        logger.info(f"Cache enabled: {self.cache.enabled}")
        logger.info(f"Circuit breaker threshold: {self.config.cb_failure_threshold}")

        try:
            while self.running:
                self.run_once()
                logger.info(f"Next check in {self.config.check_interval} seconds...")
                time.sleep(self.config.check_interval)
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
            self.stop()

    def stop(self):
        """Stop monitoring"""
        self.running = False
        logger.info("Odoo Watcher Enhanced stopped")


# =============================================================================
# CLI
# =============================================================================

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Odoo Watcher Enhanced - Monitor Odoo ERP')
    parser.add_argument('--once', action='store_true', help='Run once and exit')
    parser.add_argument('--test', action='store_true', help='Test connection')
    parser.add_argument('--interval', type=int, help='Override check interval (seconds)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose logging')

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    config = WatcherConfig()
    if args.interval:
        config.check_interval = args.interval

    watcher = OdooWatcherEnhanced(config)

    if args.test:
        logger.info("Testing Odoo connection...")
        if watcher.test_connection():
            logger.info("[OK] Connection successful!")
            logger.info(f"Status: {watcher.get_status()}")
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
