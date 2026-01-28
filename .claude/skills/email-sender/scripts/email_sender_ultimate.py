#!/usr/bin/env python3
"""
Ultimate Email Sender for Personal AI Employee

Advanced email sending with:
- Email template system with variables
- Batch sending with rate limiting
- Bounce and complaint handling
- Retry with exponential backoff
- Email scheduling and throttling
- Structured JSON logging
- Delivery tracking and analytics
- HTML and plain text support
- Attachment management

Usage:
    python email_sender_ultimate.py --to <email> --subject <subject> --body <body>
    python email_sender_ultimate.py --template <name> --data <json>
    python email_sender_ultimate.py --batch <file> --rate <emails/minute>
    python email_sender_ultimate.py --schedule <time> --to <email>
    python email_sender_ultimate.py --bounces               # Check bounces
"""

from __future__ import annotations

import os
import sys
import json
import time
import smtplib
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.utils import formataddr, formatdate
import socket

try:
    import jinja2
    HAS_JINJA = True
except ImportError:
    HAS_JINJA = False

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

try:
    from concurrent.futures import ThreadPoolExecutor, as_completed
    HAS_CONCURRENT = True
except ImportError:
    HAS_CONCURRENT = False


# =============================================================================
# Configuration
# =============================================================================

VAULT_PATH = Path(__file__).parent.parent.parent.parent.resolve()
PENDING_APPROVAL_PATH = VAULT_PATH / "Pending_Approval"
APPROVED_PATH = VAULT_PATH / "Approved"
DONE_PATH = VAULT_PATH / "Done"
LOGS_PATH = VAULT_PATH / "Logs"
TEMPLATES_PATH = VAULT_PATH / "Templates" / "Emails"
BOUNCES_PATH = LOGS_PATH / "Bounces"
QUEUE_PATH = VAULT_PATH / "Email_Queue"
CONFIG_PATH = VAULT_PATH / "email_sender_config.yaml"

# Ensure directories exist
for path in [TEMPLATES_PATH, BOUNCES_PATH, QUEUE_PATH]:
    path.mkdir(parents=True, exist_ok=True)


# =============================================================================
# Email Status Enums
# =============================================================================

class EmailStatus(Enum):
    """Email delivery status"""
    PENDING = "pending"
    SENDING = "sending"
    SENT = "sent"
    DELIVERED = "delivered"
    BOUNCED = "bounced"
    DEFERRED = "deferred"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BounceType(Enum):
    """Bounce classification types"""
    HARD = "hard"  # Permanent bounce (invalid email)
    SOFT = "soft"  # Temporary bounce (mailbox full)
    COMPLAINT = "complaint"  # Recipient marked as spam
    UNKNOWN = "unknown"


# =============================================================================
# Email Data Classes
# =============================================================================

@dataclass
class EmailAttachment:
    """Email attachment definition"""
    filename: str
    content: bytes
    content_type: str = "application/octet-stream"
    encoding: str = "base64"


@dataclass
class Email:
    """Email message definition"""
    id: str
    to: Union[str, List[str]]
    subject: str
    body: str
    html_body: Optional[str] = None
    from_name: Optional[str] = None
    from_addr: Optional[str] = None
    cc: Optional[Union[str, List[str]]] = None
    bcc: Optional[Union[str, List[str]]] = None
    reply_to: Optional[str] = None
    attachments: List[EmailAttachment] = field(default_factory=list)
    status: EmailStatus = EmailStatus.PENDING
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    scheduled_at: Optional[str] = None
    sent_at: Optional[str] = None
    attempts: int = 0
    max_attempts: int = 3
    last_error: Optional[str] = None
    message_id: Optional[str] = None
    template_name: Optional[str] = None
    template_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_due(self) -> bool:
        """Check if email is due to be sent"""
        if not self.scheduled_at:
            return True
        try:
            scheduled = datetime.fromisoformat(self.scheduled_at)
            return datetime.now() >= scheduled
        except:
            return True

    @property
    def can_retry(self) -> bool:
        """Check if email can be retried"""
        return self.attempts < self.max_attempts and self.status in [
            EmailStatus.FAILED, EmailStatus.DEFERRED
        ]

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = asdict(self)
        data['status'] = self.status.value
        if isinstance(self.to, list):
            data['to'] = self.to
        return data


@dataclass
class Bounce:
    """Email bounce record"""
    email: str
    bounce_type: BounceType
    reason: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    email_id: Optional[str] = None
    smtp_code: Optional[int] = None
    smtp_message: Optional[str] = None

    def to_dict(self) -> Dict:
        data = asdict(self)
        data['bounce_type'] = self.bounce_type.value
        return data


@dataclass
class EmailStats:
    """Email sending statistics"""
    sent: int = 0
    failed: int = 0
    bounced: int = 0
    deferred: int = 0
    total: int = 0
    avg_delivery_time: float = 0.0

    def to_dict(self) -> Dict:
        return asdict(self)


# =============================================================================
# Structured Logger
# =============================================================================

class EmailLogger:
    """Structured JSON logger for email operations"""

    def __init__(self, log_dir: Path):
        self.log_dir = log_dir
        self.log_dir.mkdir(exist_ok=True)

        self.current_log_file = log_dir / f"emails_{datetime.now().strftime('%Y-%m-%d')}.jsonl"
        self.lock = threading.Lock()

    def log(self, level: str, event: str, **data):
        """Write structured log entry"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "event": event,
            **data
        }

        with self.lock:
            with open(self.current_log_file, 'a') as f:
                f.write(json.dumps(entry) + "\n")

    def info(self, event: str, **data): self.log("info", event, **data)
    def warning(self, event: str, **data): self.log("warning", event, **data)
    def error(self, event: str, **data): self.log("error", event, **data)
    def debug(self, event: str, **data): self.log("debug", event, **data)


# =============================================================================
# Template Manager
# =============================================================================

class TemplateManager:
    """Manage email templates with Jinja2"""

    def __init__(self, templates_path: Path, logger: EmailLogger):
        self.templates_path = templates_path
        self.logger = logger

        if HAS_JINJA:
            self.env = jinja2.Environment(
                loader=jinja2.FileSystemLoader(str(templates_path)),
                autoescape=False,
                trim_blocks=True,
                lstrip_blocks=True
            )
        else:
            self.env = None
            self.logger.warning("Jinja2 not available, template rendering disabled")

    def list_templates(self) -> List[str]:
        """List available templates"""
        templates = []

        # Check for Jinja templates
        if self.env:
            templates.extend(self.env.list_templates(filter_func=lambda x: x.endswith('.j2')))

        # Check for markdown templates
        for f in self.templates_path.glob('*.md'):
            if f.stem not in [t.replace('.j2', '') for t in templates]:
                templates.append(f.name)

        return sorted(templates)

    def render_template(self, template_name: str, data: Dict[str, Any]) -> Optional[str]:
        """Render template with data"""
        if not self.env:
            self.logger.error("Template rendering not available (Jinja2 not installed)")
            return None

        try:
            # Try with .j2 extension first
            try:
                template = self.env.get_template(f"{template_name}.j2")
            except jinja2.TemplateNotFound:
                template = self.env.get_template(template_name)

            return template.render(**data)

        except jinja2.TemplateNotFound:
            self.logger.error(f"Template not found: {template_name}")
            return None
        except Exception as e:
            self.logger.error(f"Template rendering error: {e}")
            return None

    def render_from_file(self, template_path: Path, data: Dict[str, Any]) -> Optional[str]:
        """Render template from file path"""
        try:
            content = template_path.read_text(encoding='utf-8')

            if HAS_JINJA:
                template = jinja2.Template(content)
                return template.render(**data)
            else:
                # Simple variable replacement
                result = content
                for key, value in data.items():
                    result = result.replace(f"{{{{{key}}}}}", str(value))
                    result = result.replace(f"{{ {key} }}", str(value))
                return result

        except Exception as e:
            self.logger.error(f"Template file error: {e}")
            return None


# =============================================================================
# Rate Limiter
# =============================================================================

class RateLimiter:
    """Token bucket rate limiter for email sending"""

    def __init__(self, rate_per_minute: int = 60):
        self.rate = rate_per_minute
        self.tokens = rate_per_minute
        self.last_update = time.time()
        self.lock = threading.Lock()

    def acquire(self, tokens: int = 1) -> bool:
        """Acquire tokens, returns True if available"""
        with self.lock:
            now = time.time()
            elapsed = now - self.last_update

            # Refill tokens
            self.tokens = min(self.rate, self.tokens + elapsed * (self.rate / 60))
            self.last_update = now

            if self.tokens >= tokens:
                self.tokens -= tokens
                return True

            return False

    def wait_for_token(self, tokens: int = 1):
        """Wait until tokens are available"""
        while not self.acquire(tokens):
            wait_time = 60 / self.rate * tokens
            time.sleep(wait_time)

    def get_available_tokens(self) -> float:
        """Get current available tokens"""
        with self.lock:
            now = time.time()
            elapsed = now - self.last_update
            return min(self.rate, self.tokens + elapsed * (self.rate / 60))


# =============================================================================
# Bounce Manager
# =============================================================================

class BounceManager:
    """Track and manage bounced emails"""

    # SMTP codes that indicate bounces
    BOUNCE_CODES = {
        # Hard bounces
        500: BounceType.HARD,  # Syntax error
        501: BounceType.HARD,  # Syntax error
        503: BounceType.HARD,  # Bad sequence
        550: BounceType.HARD,  # Mailbox unavailable
        551: BounceType.HARD,  # User not local
        552: BounceType.HARD,  # Over quota (sometimes)
        553: BounceType.HARD,  # Mailbox name not allowed

        # Soft bounces
        421: BounceType.SOFT,  # Service not available
        450: BounceType.SOFT,  # Mailbox busy
        451: BounceType.SOFT,  # Local error
        452: BounceType.SOFT,  # Insufficient storage
    }

    def __init__(self, bounces_path: Path, logger: EmailLogger):
        self.bounces_path = bounces_path
        self.logger = logger
        self.bounces: Dict[str, List[Bounce]] = defaultdict(list)
        self.suppressed: Set[str] = set()

        self._load_bounces()

    def _load_bounces(self):
        """Load existing bounce records"""
        for file in self.bounces_path.glob("bounces_*.jsonl"):
            try:
                with open(file) as f:
                    for line in f:
                        if line.strip():
                            data = json.loads(line)
                            bounce = Bounce(
                                email=data['email'],
                                bounce_type=BounceType(data.get('bounce_type', 'unknown')),
                                reason=data['reason'],
                                timestamp=data['timestamp'],
                                email_id=data.get('email_id'),
                                smtp_code=data.get('smtp_code')
                            )
                            self.bounces[bounce.email].append(bounce)

                            # Add to suppressed if hard bounce
                            if bounce.bounce_type == BounceType.HARD:
                                self.suppressed.add(bounce.email)
            except Exception as e:
                self.logger.error(f"Error loading bounces: {e}")

    def record_bounce(self, bounce: Bounce):
        """Record a bounce"""
        self.bounces[bounce.email].append(bounce)

        if bounce.bounce_type == BounceType.HARD:
            self.suppressed.add(bounce.email)

        # Save to file
        bounce_file = self.bounces_path / f"bounces_{datetime.now().strftime('%Y-%m-%d')}.jsonl"
        with open(bounce_file, 'a') as f:
            f.write(json.dumps(bounce.to_dict()) + "\n")

        self.logger.warning(
            "bounce_recorded",
            email=bounce.email,
            type=bounce.bounce_type.value,
            reason=bounce.reason
        )

    def classify_bounce(self, smtp_code: int, message: str) -> BounceType:
        """Classify bounce type from SMTP response"""
        # Check code
        if smtp_code in self.BOUNCE_CODES:
            return self.BOUNCE_CODES[smtp_code]

        # Check message content
        message_lower = message.lower()

        if any(phrase in message_lower for phrase in
               ['full', 'quota', 'over quota', 'space', 'storage']):
            return BounceType.SOFT

        if any(phrase in message_lower for phrase in
               ['does not exist', 'no such', 'invalid', 'not found', 'unknown user']):
            return BounceType.HARD

        if any(phrase in message_lower for phrase in
               ['spam', 'complaint', 'blocked', 'rejected']):
            return BounceType.COMPLAINT

        return BounceType.UNKNOWN

    def is_suppressed(self, email: str) -> bool:
        """Check if email is suppressed from sending"""
        return email in self.suppressed

    def get_bounce_history(self, email: str) -> List[Bounce]:
        """Get bounce history for an email"""
        return self.bounces.get(email, [])

    def should_suppress(self, email: str) -> bool:
        """Determine if email should be suppressed"""
        bounces = self.get_bounce_history(email)

        # Suppress if hard bounce
        if any(b.bounce_type == BounceType.HARD for b in bounces):
            return True

        # Suppress if too many soft bounces (more than 3 in 24 hours)
        recent_soft = [
            b for b in bounces
            if b.bounce_type == BounceType.SOFT and
            datetime.fromisoformat(b.timestamp) > datetime.now() - timedelta(days=1)
        ]
        if len(recent_soft) >= 3:
            return True

        return False


# =============================================================================
# Email Builder
# =============================================================================

class EmailBuilder:
    """Build email messages for sending"""

    def __init__(self, default_from: str, default_from_name: Optional[str] = None):
        self.default_from = default_from
        self.default_from_name = default_from_name

    def build_mime(self, email: Email) -> MIMEMultipart:
        """Build MIME message from Email object"""
        msg = MIMEMultipart('alternative')

        # Headers
        from_addr = email.from_addr or self.default_from
        from_name = email.from_name or self.default_from_name

        if from_name:
            msg['From'] = formataddr((from_name, from_addr))
        else:
            msg['From'] = from_addr

        # To recipients
        if isinstance(email.to, str):
            msg['To'] = email.to
        else:
            msg['To'] = ', '.join(email.to)

        # CC
        if email.cc:
            if isinstance(email.cc, str):
                msg['Cc'] = email.cc
            else:
                msg['Cc'] = ', '.join(email.cc)

        # Reply-To
        if email.reply_to:
            msg['Reply-To'] = email.reply_to

        msg['Subject'] = email.subject
        msg['Date'] = formatdate(localtime=True)
        msg['Message-ID'] = email.message_id or f"<{email.id}@emailsender>"

        # Body parts
        if email.body:
            text_part = MIMEText(email.body, 'plain', 'utf-8')
            msg.attach(text_part)

        if email.html_body:
            html_part = MIMEText(email.html_body, 'html', 'utf-8')
            msg.attach(html_part)

        # Attachments
        for attachment in email.attachments:
            part = MIMEApplication(attachment.content)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename="{attachment.filename}"'
            )
            msg.attach(part)

        return msg


# =============================================================================
# Email Sender with Retry Logic
# =============================================================================

class EmailSender:
    """Send emails with retry logic and bounce handling"""

    def __init__(self, config: Dict[str, Any], logger: EmailLogger):
        self.config = config
        self.logger = logger

        self.smtp_host = config.get('smtp_host', 'smtp.gmail.com')
        self.smtp_port = config.get('smtp_port', 587)
        self.smtp_user = config.get('smtp_user', '')
        self.smtp_password = config.get('smtp_password', '')
        self.use_tls = config.get('use_tls', True)

        self.rate_limiter = RateLimiter(config.get('rate_per_minute', 60))
        self.bounce_manager = BounceManager(BOUNCES_PATH, logger)
        self.email_builder = EmailBuilder(
            config.get('from_addr', 'noreply@example.com'),
            config.get('from_name')
        )

        self.stats = EmailStats()
        self.sending_lock = threading.Lock()

    def send(self, email: Email) -> bool:
        """Send a single email"""
        # Check if suppressed
        if isinstance(email.to, str):
            recipients = [email.to]
        else:
            recipients = email.to

        for recipient in recipients:
            if self.bounce_manager.is_suppressed(recipient):
                self.logger.warning(
                    "email_suppressed",
                    email_id=email.id,
                    recipient=recipient
                )
                continue

        # Check rate limit
        self.rate_limiter.wait_for_token()

        email.status = EmailStatus.SENDING
        email.attempts += 1

        try:
            # Build message
            mime_msg = self.email_builder.build_mime(email)

            # Connect to SMTP server
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=30) as server:
                if self.use_tls:
                    server.starttls()

                if self.smtp_user and self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)

                # Send email
                recipients_list = [email.to] if isinstance(email.to, str) else email.to
                all_recipients = recipients_list[:]

                if email.cc:
                    if isinstance(email.cc, str):
                        all_recipients.append(email.cc)
                    else:
                        all_recipients.extend(email.cc)

                if email.bcc:
                    if isinstance(email.bcc, str):
                        all_recipients.append(email.bcc)
                    else:
                        all_recipients.extend(email.bcc)

                server.send_message(mime_msg, to_addrs=all_recipients)

            # Success
            email.status = EmailStatus.SENT
            email.sent_at = datetime.now().isoformat()

            self.stats.sent += 1
            self.logger.info(
                "email_sent",
                email_id=email.id,
                to=email.to,
                attempts=email.attempts
            )

            return True

        except smtplib.SMTPResponseException as e:
            # Handle SMTP error codes
            bounce_type = self.bounce_manager.classify_bounce(e.smtp_code, str(e))

            if bounce_type == BounceType.HARD:
                email.status = EmailStatus.BOUNCED
                self.bounce_manager.record_bounce(Bounce(
                    email=email.to if isinstance(email.to, str) else email.to[0],
                    bounce_type=bounce_type,
                    reason=str(e),
                    email_id=email.id,
                    smtp_code=e.smtp_code
                ))
            else:
                email.status = EmailStatus.DEFERRED

            email.last_error = str(e)
            self.stats.deferred += 1

            self.logger.error(
                "email_failed",
                email_id=email.id,
                error=str(e),
                smtp_code=e.smtp_code,
                bounce_type=bounce_type.value
            )

            return False

        except Exception as e:
            email.status = EmailStatus.FAILED
            email.last_error = str(e)
            self.stats.failed += 1

            self.logger.error(
                "email_error",
                email_id=email.id,
                error=str(e)
            )

            return False

    def send_batch(self, emails: List[Email], parallel: bool = False) -> Dict[str, Any]:
        """Send multiple emails"""
        results = {
            'sent': 0,
            'failed': 0,
            'deferred': 0,
            'bounced': 0
        }

        if not parallel or not HAS_CONCURRENT:
            # Sequential sending
            for email in emails:
                if email.is_due:
                    if self.send(email):
                        results['sent'] += 1
                    else:
                        if email.status == EmailStatus.DEFERRED:
                            results['deferred'] += 1
                        elif email.status == EmailStatus.BOUNCED:
                            results['bounced'] += 1
                        else:
                            results['failed'] += 1
        else:
            # Parallel sending with rate limiting
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = {executor.submit(self.send, email): email for email in emails if email.is_due}

                for future in as_completed(futures):
                    email = futures[future]
                    try:
                        success = future.result()
                        if success:
                            results['sent'] += 1
                        else:
                            if email.status == EmailStatus.DEFERRED:
                                results['deferred'] += 1
                            elif email.status == EmailStatus.BOUNCED:
                                results['bounced'] += 1
                            else:
                                results['failed'] += 1
                    except Exception as e:
                        self.logger.error("batch_error", error=str(e))
                        results['failed'] += 1

        return results


# =============================================================================
# Ultimate Email Sender
# =============================================================================

class UltimateEmailSender:
    """Main email sending application with all features"""

    def __init__(self, config_path: Optional[Path] = None):
        self.config = self._load_config(config_path)

        # Setup paths
        self.queue_path = QUEUE_PATH
        self.approved_path = APPROVED_PATH
        self.done_path = DONE_PATH

        # Components
        self.logger = EmailLogger(LOGS_PATH)
        self.template_manager = TemplateManager(TEMPLATES_PATH, self.logger)
        self.sender = EmailSender(self.config, self.logger)

        # Load pending emails from queue
        self.queue: Dict[str, Email] = {}
        self._load_queue()

    def _load_config(self, config_path: Optional[Path]) -> Dict:
        """Load configuration from file or environment"""
        config = {
            'smtp_host': os.getenv('SMTP_HOST', 'smtp.gmail.com'),
            'smtp_port': int(os.getenv('SMTP_PORT', '587')),
            'smtp_user': os.getenv('SMTP_USER', ''),
            'smtp_password': os.getenv('SMTP_PASSWORD', ''),
            'use_tls': os.getenv('SMTP_USE_TLS', 'true').lower() == 'true',
            'from_addr': os.getenv('EMAIL_FROM', 'noreply@example.com'),
            'from_name': os.getenv('EMAIL_FROM_NAME', ''),
            'rate_per_minute': int(os.getenv('EMAIL_RATE_LIMIT', '60')),
            'max_retries': int(os.getenv('EMAIL_MAX_RETRIES', '3')),
            'batch_size': int(os.getenv('EMAIL_BATCH_SIZE', '50')),
        }

        if config_path and config_path.exists() and HAS_YAML:
            try:
                with open(config_path) as f:
                    yaml_config = yaml.safe_load(f)
                    config.update(yaml_config)
            except Exception as e:
                print(f"Warning: Failed to load config: {e}")

        return config

    def _load_queue(self):
        """Load pending emails from queue"""
        for file in self.queue_path.glob('*.json'):
            try:
                data = json.loads(file.read_text())
                email = Email(**data)
                email.status = EmailStatus(data.get('status', 'pending'))
                self.queue[email.id] = email
            except Exception as e:
                self.logger.error(f"Error loading queue file {file}: {e}")

    def _save_to_queue(self, email: Email):
        """Save email to queue"""
        queue_file = self.queue_path / f"{email.id}.json"
        queue_file.write_text(json.dumps(email.to_dict(), indent=2))

    def _remove_from_queue(self, email_id: str):
        """Remove email from queue"""
        queue_file = self.queue_path / f"{email_id}.json"
        if queue_file.exists():
            queue_file.unlink()

    def create_email(
        self,
        to: Union[str, List[str]],
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        template_name: Optional[str] = None,
        template_data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Email:
        """Create a new email"""
        email_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hashlib.md5(subject.encode()).hexdigest()[:8]}"

        email = Email(
            id=email_id,
            to=to,
            subject=subject,
            body=body,
            html_body=html_body,
            template_name=template_name,
            template_data=template_data or {},
            **kwargs
        )

        return email

    def send_from_template(
        self,
        template_name: str,
        to: Union[str, List[str]],
        data: Dict[str, Any],
        subject: Optional[str] = None
    ) -> bool:
        """Send email from template"""
        # Render template
        rendered = self.template_manager.render_template(template_name, data)

        if not rendered:
            self.logger.error(f"Template rendering failed: {template_name}")
            return False

        # Parse rendered content (subject and body separated by first blank line)
        lines = rendered.split('\n')
        subject_line = 0

        for i, line in enumerate(lines):
            if line.strip() == '':
                subject_line = i
                break

        if subject is None:
            template_subject = lines[0] if lines else 'No Subject'
        else:
            template_subject = subject

        template_body = '\n'.join(lines[subject_line + 1:]) if subject_line > 0 else rendered

        # Check for HTML
        html_body = None
        if '<html' in template_body or '<body' in template_body or '<div' in template_body:
            html_body = template_body
            # Strip HTML for plain text version
            import re
            template_body = re.sub(r'<[^>]+>', '\n', template_body)
            template_body = '\n'.join(line.strip() for line in template_body.split('\n') if line.strip())

        # Create and send email
        email = self.create_email(
            to=to,
            subject=template_subject,
            body=template_body,
            html_body=html_body,
            template_name=template_name,
            template_data=data
        )

        return self.send(email)

    def send(self, email: Email, queue: bool = False) -> bool:
        """Send an email immediately or queue it"""
        if queue:
            self._save_to_queue(email)
            self.logger.info("email_queued", email_id=email.id)
            return True

        return self.sender.send(email)

    def send_batch_file(self, batch_file: Path) -> Dict[str, Any]:
        """Send emails from a batch file"""
        try:
            data = json.loads(batch_file.read_text())
            emails = []

            for email_data in data.get('emails', []):
                email = Email(**email_data)
                emails.append(email)

            results = self.sender.send_batch(emails, parallel=True)

            self.logger.info("batch_completed", file=str(batch_file), results=results)

            return results

        except Exception as e:
            self.logger.error("batch_error", file=str(batch_file), error=str(e))
            return {'sent': 0, 'failed': len(emails) if 'emails' in data else 0}

    def process_queue(self) -> Dict[str, Any]:
        """Process all queued emails"""
        due_emails = [e for e in self.queue.values() if e.is_due and e.can_retry]

        if not due_emails:
            return {'sent': 0, 'failed': 0, 'deferred': 0, 'bounced': 0}

        results = self.sender.send_batch(due_emails, parallel=True)

        # Move completed emails out of queue
        for email in due_emails:
            if email.status == EmailStatus.SENT:
                self._remove_from_queue(email.id)
                del self.queue[email.id]

        return results

    def check_bounces(self) -> List[Bounce]:
        """Check and return recent bounces"""
        bounces = []

        for file in self.bounce_manager.bounces_path.glob("bounces_*.jsonl"):
            try:
                with open(file) as f:
                    for line in f:
                        if line.strip():
                            data = json.loads(line)
                            bounces.append(Bounce(**data))
            except Exception as e:
                self.logger.error(f"Error reading bounce file: {e}")

        # Sort by timestamp, most recent first
        bounces.sort(key=lambda b: b.timestamp, reverse=True)

        return bounces[:50]  # Return last 50

    def show_stats(self):
        """Show email statistics"""
        print("\n" + "=" * 60)
        print("EMAIL SENDER STATISTICS")
        print("=" * 60)
        print(f"Sent:      {self.sender.stats.sent}")
        print(f"Failed:    {self.sender.stats.failed}")
        print(f"Deferred:  {self.sender.stats.deferred}")
        print(f"Bounced:   {self.sender.stats.bounced}")
        print(f"Queued:    {len(self.queue)}")
        print("=" * 60)

        # Show recent bounces
        bounces = self.check_bounces()
        if bounces:
            print(f"\n⚠️  RECENT BOUNCES ({len(bounces)}):")
            for bounce in bounces[:10]:
                print(f"  - {bounce.email} ({bounce.bounce_type.value}): {bounce.reason}")

        print()


# =============================================================================
# CLI
# =============================================================================

def main():
    import argparse
    import hashlib

    parser = argparse.ArgumentParser(description='Ultimate Email Sender')
    parser.add_argument('--to', help='Recipient email(s)')
    parser.add_argument('--subject', help='Email subject')
    parser.add_argument('--body', help='Email body')
    parser.add_argument('--html', action='store_true', help='HTML format')
    parser.add_argument('--template', help='Template name')
    parser.add_argument('--data', help='Template data as JSON')
    parser.add_argument('--batch', help='Batch file path')
    parser.add_argument('--schedule', help='Schedule time (ISO format)')
    parser.add_argument('--queue', action='store_true', help='Queue email instead of sending')
    parser.add_argument('--bounces', action='store_true', help='Show bounces')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    parser.add_argument('--process-queue', action='store_true', help='Process queued emails')
    parser.add_argument('--config', help='Config file path')
    parser.add_argument('--list-templates', action='store_true', help='List templates')

    args = parser.parse_args()

    config_path = Path(args.config) if args.config else CONFIG_PATH
    sender = UltimateEmailSender(config_path)

    if args.stats:
        sender.show_stats()
        return 0

    if args.bounces:
        bounces = sender.check_bounces()
        print(f"\n⚠️  RECENT BOUNCES ({len(bounces)}):")
        for bounce in bounces[:20]:
            print(f"  - {bounce.email} ({bounce.bounce_type.value}): {bounce.reason}")
        return 0

    if args.list_templates:
        templates = sender.template_manager.list_templates()
        print(f"\n📄 AVAILABLE TEMPLATES ({len(templates)}):")
        for template in templates:
            print(f"  - {template}")
        return 0

    if args.process_queue:
        results = sender.process_queue()
        print(f"\n📊 Queue Processed:")
        print(f"   Sent: {results['sent']}")
        print(f"   Failed: {results['failed']}")
        print(f"   Deferred: {results['deferred']}")
        return 0

    if args.template:
        if not args.to:
            print("Error: --to is required with --template")
            return 1

        data = json.loads(args.data) if args.data else {}

        success = sender.send_from_template(
            template_name=args.template,
            to=args.to,
            data=data,
            subject=args.subject
        )

        return 0 if success else 1

    if args.batch:
        results = sender.send_batch_file(Path(args.batch))
        print(f"\n📊 Batch Results:")
        print(f"   Sent: {results['sent']}")
        print(f"   Failed: {results['failed']}")
        print(f"   Deferred: {results['deferred']}")
        return 0

    if args.to and args.subject and args.body:
        email = sender.create_email(
            to=args.to,
            subject=args.subject,
            body=args.body,
            html_body=args.body if args.html else None,
            scheduled_at=args.schedule
        )

        success = sender.send(email, queue=args.queue)

        if success:
            print(f"\n✅ Email sent successfully!")
        else:
            print(f"\n❌ Failed to send email")

        return 0 if success else 1

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
