#!/usr/bin/env python3
"""
Odoo Webhook Server - Real-time event processing from Odoo

Receives webhook notifications from Odoo when:
- New invoices are created/posted
- Payments are received
- Vendor bills are created
- Partners are added/modified

This eliminates the need for polling and provides instant notifications.

Usage:
    python odoo_webhook_server.py --port 5000
    python odoo_webhook_server.py --start
    python odoo_webhook_server.py --test

Odoo Webhook Setup:
    1. In Odoo, go to Settings > Technical > Automation > Webhooks
    2. Create new webhook pointing to: http://your-server:5000/webhook/odoo
    3. Select events: invoice.create, payment.create, etc.
    4. Set secret key for authentication
"""

from __future__ import annotations

import os
import sys
import json
import hmac
import hashlib
import logging
import threading
import queue
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from concurrent.futures import ThreadPoolExecutor

try:
    from flask import Flask, request, jsonify
except ImportError:
    print("Installing required package: flask")
    os.system("pip install flask")
    from flask import Flask, request, jsonify

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure logging
LOG_DIR = Path(__file__).parent.parent / 'Logs'
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / f'odoo_webhook_{datetime.now().strftime("%Y-%m-%d")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("odoo_webhook")


# =============================================================================
# Configuration
# =============================================================================

@dataclass
class WebhookConfig:
    """Configuration for webhook server"""
    host: str = os.getenv('ODOO_WEBHOOK_HOST', '0.0.0.0')
    port: int = int(os.getenv('ODOO_WEBHOOK_PORT', '5000'))
    secret: str = os.getenv('ODOO_WEBHOOK_SECRET', 'change-me-in-production')
    debug: bool = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'

    vault_path: Path = field(default_factory=lambda: Path(__file__).parent.parent)
    needs_action_path: Path = field(default_factory=lambda: lambda: Path(__file__).parent.parent / 'Needs_Action')
    accounting_path: Path = field(default_factory=lambda: Path(__file__).parent.parent / 'Accounting')

    # Processing settings
    enable_async: bool = os.getenv('ODOO_WEBHOOK_ASYNC', 'true').lower() == 'true'
    max_workers: int = int(os.getenv('ODOO_WEBHOOK_WORKERS', '4'))
    event_queue_size: int = int(os.getenv('ODOO_WEBHOOK_QUEUE_SIZE', '1000'))

    # Deduplication
    dedup_window: int = int(os.getenv('ODOO_WEBHOOK_DEDUP_WINDOW', '3600'))  # 1 hour


# =============================================================================
# Event Types
# =============================================================================

class OdooEventType(Enum):
    """Odoo event types"""
    INVOICE_CREATED = "invoice.created"
    INVOICE_POSTED = "invoice.posted"
    INVOICE_PAID = "invoice.paid"
    PAYMENT_RECEIVED = "payment.received"
    BILL_CREATED = "bill.created"
    BILL_POSTED = "bill.posted"
    PARTNER_CREATED = "partner.created"
    PARTNER_UPDATED = "partner.updated"


@dataclass
class OdooEvent:
    """Represents an Odoo webhook event"""
    event_type: str
    model: str
    record_id: int
    data: Dict
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    processed: bool = False
    retry_count: int = 0

    def to_dict(self) -> Dict:
        return asdict(self)


# =============================================================================
# Event Processor
# =============================================================================

class EventProcessor:
    """Processes Odoo webhook events and creates tasks"""

    def __init__(self, config: WebhookConfig):
        self.config = config
        self.processed_events = set()  # For deduplication
        self.lock = threading.Lock()

        # Create directories
        self.config.needs_action_path.mkdir(exist_ok=True)
        self.config.accounting_path.mkdir(exist_ok=True)
        (self.config.accounting_path / 'Invoices').mkdir(exist_ok=True)
        (self.config.accounting_path / 'Payments').mkdir(exist_ok=True)
        (self.config.accounting_path / 'Bills').mkdir(exist_ok=True)

    def _is_duplicate(self, event_id: str) -> bool:
        """Check if event was already processed"""
        with self.lock:
            if event_id in self.processed_events:
                return True
            # Add to processed set
            self.processed_events.add(event_id)

            # Cleanup old entries (keep set size manageable)
            if len(self.processed_events) > 10000:
                # Remove oldest 1000
                self.processed_events = set(list(self.processed_events)[1000:])

            return False

    def _generate_event_id(self, event: OdooEvent) -> str:
        """Generate unique event ID for deduplication"""
        return f"{event.model}:{event.record_id}:{event.event_type}:{event.timestamp[:19]}"

    def process_event(self, event: OdooEvent) -> bool:
        """Process a single Odoo event"""
        event_id = self._generate_event_id(event)

        if self._is_duplicate(event_id):
            logger.debug(f"Duplicate event skipped: {event_id}")
            return False

        logger.info(f"Processing event: {event.event_type} for {event.model}:{event.record_id}")

        try:
            if event.event_type == OdooEventType.INVOICE_CREATED.value:
                self._process_invoice_created(event)
            elif event.event_type == OdooEventType.INVOICE_POSTED.value:
                self._process_invoice_posted(event)
            elif event.event_type == OdooEventType.INVOICE_PAID.value:
                self._process_invoice_paid(event)
            elif event.event_type == OdooEventType.PAYMENT_RECEIVED.value:
                self._process_payment_received(event)
            elif event.event_type == OdooEventType.BILL_CREATED.value:
                self._process_bill_created(event)
            elif event.event_type == OdooEventType.BILL_POSTED.value:
                self._process_bill_posted(event)
            elif event.event_type == OdooEventType.PARTNER_CREATED.value:
                self._process_partner_created(event)
            else:
                logger.warning(f"Unknown event type: {event.event_type}")
                return False

            return True

        except Exception as e:
            logger.error(f"Error processing event: {e}")
            return False

    def _process_invoice_created(self, event: OdooEvent):
        """Process new invoice creation"""
        data = event.data
        invoice_name = data.get('name', f'INV-{event.record_id}')
        partner = data.get('partner_id', {})
        partner_name = partner.get('name', 'Unknown') if isinstance(partner, dict) else 'Unknown'
        amount = data.get('amount_total', 0)

        task_filename = f"WEBHOOK_INVOICE_{invoice_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        task_path = self.config.needs_action_path / task_filename

        task_content = f"""---
type: invoice_review
source: odoo_webhook
priority: high
realtime: true
event_type: {event.event_type}
odoo_id: {event.record_id}
---

# New Invoice Created (Real-time)

## Invoice Details

- **Invoice Number:** {invoice_name}
- **Customer:** {partner_name}
- **Amount:** ${amount:,.2f}
- **Status:** {data.get('state', 'draft')}
- **Created:** {event.timestamp}

## Actions Required

1. **Review Invoice**
   - Verify line items and quantities
   - Check pricing and terms
   - Confirm customer information

2. **Post Invoice**
   - Post to accounting when verified
   - Send to customer

---
*Received via Odoo Webhook at {event.timestamp}*
"""

        task_path.write_text(task_content)
        logger.info(f"Created webhook task: {task_filename}")

        # Save to accounting
        self._save_to_accounting('invoice', data, event)

    def _process_invoice_posted(self, event: OdooEvent):
        """Process invoice posting"""
        data = event.data
        invoice_name = data.get('name', f'INV-{event.record_id}')

        # Create a simpler task for posted invoices
        task_filename = f"WEBHOOK_INVOICE_POSTED_{invoice_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        task_path = self.config.needs_action_path / task_filename

        task_content = f"""---
type: invoice_posted
source: odoo_webhook
priority: medium
odoo_id: {event.record_id}
---

# Invoice Posted: {invoice_name}

Invoice has been posted and ready to send to customer.

- **Amount:** ${data.get('amount_total', 0):,.2f}
- **Posted:** {event.timestamp}

Action: Send invoice to customer using email-sender skill.
"""

        task_path.write_text(task_content)
        logger.info(f"Created posted invoice task: {task_filename}")

    def _process_invoice_paid(self, event: OdooEvent):
        """Process invoice payment"""
        data = event.data
        invoice_name = data.get('name', f'INV-{event.record_id}')

        task_filename = f"WEBHOOK_PAYMENT_RECEIVED_{invoice_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        task_path = self.config.needs_action_path / task_filename

        task_content = f"""---
type: payment_notification
source: odoo_webhook
priority: low
odoo_id: {event.record_id}
---

# Payment Received for: {invoice_name}

Invoice has been paid!

- **Amount:** ${data.get('amount_total', 0):,.2f}
- **Payment State:** Paid
- **Detected:** {event.timestamp}

Action: Send payment confirmation to customer.
"""

        task_path.write_text(task_content)

    def _process_payment_received(self, event: OdooEvent):
        """Process standalone payment"""
        data = event.data
        payment_name = data.get('name', f'PAY-{event.record_id}')

        task_filename = f"WEBHOOK_PAYMENT_{payment_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        task_path = self.config.needs_action_path / task_filename

        task_content = f"""---
type: payment_recording
source: odoo_webhook
priority: medium
odoo_id: {event.record_id}
---

# Payment Received (Real-time)

- **Payment Reference:** {payment_name}
- **Amount:** ${data.get('amount', 0):,.2f}
- **Payment Type:** {data.get('payment_type', 'unknown')}
- **Received:** {event.timestamp}

Action: Reconcile with open invoice.
"""

        task_path.write_text(task_content)

    def _process_bill_created(self, event: OdooEvent):
        """Process new vendor bill"""
        data = event.data
        bill_name = data.get('name', f'BILL-{event.record_id}')
        partner = data.get('partner_id', {})
        vendor_name = partner.get('name', 'Unknown') if isinstance(partner, dict) else 'Unknown'

        task_filename = f"WEBHOOK_BILL_{bill_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        task_path = self.config.needs_action_path / task_filename

        task_content = f"""---
type: bill_approval
source: odoo_webhook
priority: medium
odoo_id: {event.record_id}
---

# New Vendor Bill: {bill_name}

- **Vendor:** {vendor_name}
- **Amount:** ${data.get('amount_total', 0):,.2f}
- **Due Date:** {data.get('invoice_date_due', 'TBD')}
- **Received:** {event.timestamp}

Action: Review and approve for payment.
"""

        task_path.write_text(task_content)

        self._save_to_accounting('bill', data, event)

    def _process_bill_posted(self, event: OdooEvent):
        """Process posted bill"""
        # Bills when posted need payment scheduling
        pass

    def _process_partner_created(self, event: OdooEvent):
        """Process new partner (customer/vendor)"""
        data = event.data
        partner_name = data.get('name', 'Unknown')

        # Log the new partner - usually doesn't require immediate action
        logger.info(f"New partner created: {partner_name} (ID: {event.record_id})")

    def _save_to_accounting(self, item_type: str, item: Dict, event: OdooEvent):
        """Save item to accounting directory"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

            if item_type == 'invoice':
                filename = f'invoice_{event.record_id}_{timestamp}.json'
                filepath = self.config.accounting_path / 'Invoices' / filename
            elif item_type == 'bill':
                filename = f'bill_{event.record_id}_{timestamp}.json'
                filepath = self.config.accounting_path / 'Bills' / filename
            else:
                return

            data = {
                'odoo_type': item_type,
                'odoo_id': event.record_id,
                'data': item,
                'webhook_timestamp': event.timestamp,
                'synced_from': 'Odoo Webhook'
            }

            filepath.write_text(json.dumps(data, indent=2, default=str))
            logger.debug(f"Saved to accounting: {filename}")

        except Exception as e:
            logger.error(f"Error saving to accounting: {e}")


# =============================================================================
# Webhook Server
# =============================================================================

class OdooWebhookServer:
    """Flask server for receiving Odoo webhooks"""

    def __init__(self, config: WebhookConfig):
        self.config = config
        self.app = Flask(__name__)
        self.processor = EventProcessor(config)
        self.event_queue = queue.Queue(maxsize=config.event_queue_size)
        self.executor = ThreadPoolExecutor(max_workers=config.max_workers)

        # Statistics
        self.stats = {
            'events_received': 0,
            'events_processed': 0,
            'events_failed': 0,
            'events_duplicate': 0,
            'start_time': datetime.now().isoformat()
        }

        self._setup_routes()

    def _setup_routes(self):
        """Setup Flask routes"""

        @self.app.route('/')
        def index():
            return jsonify({
                'service': 'Odoo Webhook Server',
                'status': 'running',
                'stats': self.stats
            })

        @self.app.route('/health')
        def health():
            return jsonify({'status': 'healthy'})

        @self.app.route('/webhook/odoo', methods=['POST'])
        def webhook_odoo():
            """Main webhook endpoint for Odoo events"""

            # Verify signature if secret is set
            if self.config.secret != 'change-me-in-production':
                signature = request.headers.get('X-Odoo-Signature', '')
                expected = hmac.new(
                    self.config.secret.encode(),
                    request.data,
                    hashlib.sha256
                ).hexdigest()

                if not hmac.compare_digest(signature, f'sha256={expected}'):
                    logger.warning("Invalid webhook signature")
                    return jsonify({'error': 'Invalid signature'}), 403

            # Parse event data
            try:
                event_data = request.get_json()

                if not event_data:
                    return jsonify({'error': 'No data provided'}), 400

                # Extract event info
                event_type = event_data.get('event_type')
                model = event_data.get('model')
                record_id = event_data.get('record_id')
                record_data = event_data.get('data', {})

                if not all([event_type, model, record_id]):
                    return jsonify({'error': 'Missing required fields'}), 400

                # Create event
                event = OdooEvent(
                    event_type=event_type,
                    model=model,
                    record_id=record_id,
                    data=record_data,
                    timestamp=event_data.get('timestamp', datetime.now().isoformat())
                )

                self.stats['events_received'] += 1

                # Process event (async or sync)
                if self.config.enable_async:
                    self.event_queue.put(event)
                    return jsonify({'status': 'queued', 'event_id': self._generate_event_id(event)})
                else:
                    success = self.processor.process_event(event)
                    if success:
                        self.stats['events_processed'] += 1
                        return jsonify({'status': 'processed', 'event_id': self._generate_event_id(event)})
                    else:
                        self.stats['events_failed'] += 1
                        return jsonify({'status': 'failed'}), 500

            except Exception as e:
                logger.error(f"Error processing webhook: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/webhook/batch', methods=['POST'])
        def webhook_batch():
            """Batch webhook endpoint for multiple events"""

            try:
                events_data = request.get_json()
                events = events_data.get('events', [])

                results = []
                for event_data in events:
                    event = OdooEvent(
                        event_type=event_data.get('event_type'),
                        model=event_data.get('model'),
                        record_id=event_data.get('record_id'),
                        data=event_data.get('data', {}),
                        timestamp=event_data.get('timestamp', datetime.now().isoformat())
                    )

                    if self.config.enable_async:
                        self.event_queue.put(event)
                        results.append({'status': 'queued'})
                    else:
                        success = self.processor.process_event(event)
                        results.append({'status': 'processed' if success else 'failed'})
                        self.stats['events_processed'] += int(success)

                return jsonify({'results': results})

            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/stats')
        def stats():
            """Get server statistics"""
            return jsonify({
                **self.stats,
                'queue_size': self.event_queue.qsize(),
                'uptime_seconds': (datetime.now() - datetime.fromisoformat(self.stats['start_time'])).total_seconds()
            })

        @self.app.route('/test', methods=['POST'])
        def test_webhook():
            """Test endpoint - simulates an Odoo webhook"""

            test_event = {
                'event_type': OdooEventType.INVOICE_CREATED.value,
                'model': 'account.move',
                'record_id': 99999,
                'timestamp': datetime.now().isoformat(),
                'data': {
                    'id': 99999,
                    'name': 'TEST/2026/0001',
                    'move_type': 'out_invoice',
                    'state': 'draft',
                    'partner_id': {'id': 1, 'name': 'Test Customer'},
                    'amount_total': 1500.00,
                    'invoice_date': datetime.now().strftime('%Y-%m-%d')
                }
            }

            event = OdooEvent(**test_event)
            success = self.processor.process_event(event)

            if success:
                self.stats['events_processed'] += 1
                return jsonify({'status': 'test event processed', 'event': test_event})
            else:
                return jsonify({'status': 'test event failed'}), 500

    def _generate_event_id(self, event: OdooEvent) -> str:
        return f"{event.model}:{event.record_id}:{event.event_type}:{event.timestamp[:19]}"

    def _process_queue(self):
        """Background worker to process queued events"""
        while True:
            try:
                event = self.event_queue.get(timeout=1)
                success = self.processor.process_event(event)

                if success:
                    self.stats['events_processed'] += 1
                else:
                    self.stats['events_failed'] += 1

                self.event_queue.task_done()

            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing queued event: {e}")

    def run(self):
        """Start the webhook server"""
        logger.info("=" * 60)
        logger.info("Odoo Webhook Server Starting")
        logger.info(f"  Host: {self.config.host}")
        logger.info(f"  Port: {self.config.port}")
        logger.info(f"  Async: {self.config.enable_async}")
        logger.info(f"  Max Workers: {self.config.max_workers}")
        logger.info("=" * 60)

        # Start background worker if async
        if self.config.enable_async:
            import threading
            worker = threading.Thread(target=self._process_queue, daemon=True)
            worker.start()
            logger.info("Background event processor started")

        # Run Flask app
        self.app.run(
            host=self.config.host,
            port=self.config.port,
            debug=self.config.debug,
            use_reloader=False
        )


# =============================================================================
# CLI
# =============================================================================

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Odoo Webhook Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--secret', help='Webhook secret for signature verification')
    parser.add_argument('--no-async', action='store_true', help='Disable async processing')
    parser.add_argument('--workers', type=int, help='Number of worker threads')
    parser.add_argument('--test', action='store_true', help='Send test webhook event')
    parser.add_argument('--start', action='store_true', help='Start the server')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')

    args = parser.parse_args()

    config = WebhookConfig()

    if args.host:
        config.host = args.host
    if args.port:
        config.port = args.port
    if args.secret:
        config.secret = args.secret
    if args.no_async:
        config.enable_async = False
    if args.workers:
        config.max_workers = args.workers
    if args.debug:
        config.debug = True

    server = OdooWebhookServer(config)

    if args.test:
        # Send test event
        import requests
        test_url = f"http://{config.host}:{config.port}/test"
        try:
            response = requests.post(test_url, timeout=5)
            print(f"Test webhook result: {response.json()}")
        except Exception as e:
            print(f"Test failed: {e}")
            return 1
        return 0

    if args.start or len(sys.argv) == 1:
        server.run()
        return 0

    return 0


if __name__ == '__main__':
    sys.exit(main())
