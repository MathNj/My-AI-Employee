#!/usr/bin/env python3
"""
Odoo Alerting System

Sends alerts via email, webhook, or other channels when issues occur.

Features:
- Alert rules with conditions
- Multiple notification channels
- Alert deduplication (prevent spam)
- Alert history and tracking
- Rate limiting per alert type

Usage:
    from odoo_alerts import Alerter, AlertRule

    alerter = Alerter()

    # Send simple alert
    alerter.send_alert("sync_failed", "Sync operation failed", severity="high")

    # Create alert rule
    rule = AlertRule(
        name="high_error_rate",
        condition=lambda ctx: ctx.get("error_rate", 0) > 0.1,
        message="Error rate exceeds 10%"
    )
    alerter.add_rule(rule)
"""

from __future__ import annotations

import os
import sys
import json
import smtplib
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Literal
from dataclasses import dataclass, field
from enum import Enum
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from collections import deque
import hashlib

try:
    import requests
except ImportError:
    requests = None

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


# =============================================================================
# Alert Types
# =============================================================================

class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertStatus(Enum):
    """Alert delivery status"""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    SUPPRESSED = "suppressed"  # Deduplicated


# =============================================================================
# Alert Data
# =============================================================================

@dataclass
class Alert:
    """An alert to be sent"""
    id: str
    name: str
    message: str
    severity: AlertSeverity = AlertSeverity.WARNING
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    context: Dict[str, Any] = field(default_factory=dict)
    status: AlertStatus = AlertStatus.PENDING
    delivery_attempts: int = 0
    last_error: Optional[str] = None

    def __post_init__(self):
        if not self.id:
            # Generate ID from name and timestamp
            content = f"{self.name}:{self.timestamp}"
            self.id = hashlib.sha256(content.encode()).hexdigest()[:16]


@dataclass
class AlertRule:
    """Rule for triggering alerts"""
    name: str
    condition: Callable[[Dict[str, Any]], bool]
    message: str
    severity: AlertSeverity = AlertSeverity.WARNING
    cooldown_minutes: int = 60  # Minimum time between same alert
    enabled: bool = True


# =============================================================================
# Notification Channels
# =============================================================================

class NotificationChannel:
    """Base class for notification channels"""

    def send(self, alert: Alert) -> bool:
        """Send alert. Returns True if successful."""
        raise NotImplementedError


class EmailChannel(NotificationChannel):
    """Email notification channel"""

    def __init__(self, smtp_host: str, smtp_port: int,
                 from_addr: str, username: str, password: str,
                 use_tls: bool = True):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.from_addr = from_addr
        self.username = username
        self.password = password
        self.use_tls = use_tls

    def send(self, alert: Alert) -> bool:
        """Send email alert"""
        try:
            # Parse recipients
            to_addrs = alert.context.get("recipients", [])
            if isinstance(to_addrs, str):
                to_addrs = [to_addrs]

            if not to_addrs:
                # Use default from context or config
                to_addrs = [alert.context.get("to_email", "admin@example.com")]

            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"[{alert.severity.value.upper()}] {alert.name}"
            msg['From'] = self.from_addr
            msg['To'] = ', '.join(to_addrs)

            # Plain text body
            text = f"""
Alert: {alert.name}
Severity: {alert.severity.value.upper()}
Time: {alert.timestamp}

{alert.message}

"""
            if alert.context:
                text += "\nContext:\n"
                for key, value in alert.context.items():
                    text += f"  {key}: {value}\n"

            msg.attach(MIMEText(text, 'plain'))

            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                if self.username and self.password:
                    server.login(self.username, self.password)
                server.send_message(msg)

            return True

        except Exception as e:
            alert.last_error = str(e)
            return False


class WebhookChannel(NotificationChannel):
    """Webhook notification channel"""

    def __init__(self, url: str, method: str = "POST",
                 headers: Optional[Dict[str, str]] = None):
        self.url = url
        self.method = method
        self.headers = headers or {}

    def send(self, alert: Alert) -> bool:
        """Send webhook alert"""
        if requests is None:
            alert.last_error = "requests library not available"
            return False

        try:
            payload = {
                "alert_id": alert.id,
                "name": alert.name,
                "message": alert.message,
                "severity": alert.severity.value,
                "timestamp": alert.timestamp,
                "context": alert.context
            }

            response = requests.request(
                self.method,
                self.url,
                json=payload,
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()

            return True

        except Exception as e:
            alert.last_error = str(e)
            return False


class SlackChannel(WebhookChannel):
    """Slack webhook channel"""

    def __init__(self, webhook_url: str):
        super().__init__(webhook_url)
        self.webhook_url = webhook_url

    def send(self, alert: Alert) -> bool:
        """Send Slack alert"""
        if requests is None:
            return False

        try:
            # Map severity to Slack colors
            colors = {
                AlertSeverity.INFO: "#36a64f",  # Green
                AlertSeverity.WARNING: "#ff9900",  # Orange
                AlertSeverity.ERROR: "#ff0000",  # Red
                AlertSeverity.CRITICAL: "#990000"  # Dark red
            }

            payload = {
                "attachments": [{
                    "color": colors.get(alert.severity, "#808080"),
                    "title": f"[{alert.severity.value.upper()}] {alert.name}",
                    "text": alert.message,
                    "fields": [
                        {"title": "Severity", "value": alert.severity.value.upper(), "short": True},
                        {"title": "Time", "value": alert.timestamp, "short": True}
                    ],
                    "footer": "Odoo Sync Alerter"
                }]
            }

            # Add context as fields
            if alert.context:
                for key, value in list(alert.context.items())[:5]:  # Max 5 fields
                    payload["attachments"][0]["fields"].append({
                        "title": key,
                        "value": str(value)[:100],  # Truncate long values
                        "short": True
                    })

            response = requests.post(self.webhook_url, json=payload, timeout=10)
            response.raise_for_status()

            return True

        except Exception as e:
            alert.last_error = str(e)
            return False


class DiscordChannel(NotificationChannel):
    """Discord webhook channel"""

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def send(self, alert: Alert) -> bool:
        """Send Discord alert"""
        if requests is None:
            return False

        try:
            # Map severity to Discord colors
            colors = {
                AlertSeverity.INFO: 0x36a64f,  # Green
                AlertSeverity.WARNING: 0xff9900,  # Orange
                AlertSeverity.ERROR: 0xff0000,  # Red
                AlertSeverity.CRITICAL: 0x990000  # Dark red
            }

            embed = {
                "title": f"[{alert.severity.value.upper()}] {alert.name}",
                "description": alert.message,
                "color": colors.get(alert.severity, 0x808080),
                "timestamp": alert.timestamp,
                "fields": []
            }

            # Add context as fields
            if alert.context:
                for key, value in list(alert.context.items())[:5]:
                    embed["fields"].append({
                        "name": key,
                        "value": str(value)[:200],
                        "inline": True
                    })

            payload = {"embeds": [embed]}

            response = requests.post(self.webhook_url, json=payload, timeout=10)
            response.raise_for_status()

            return True

        except Exception as e:
            alert.last_error = str(e)
            return False


# =============================================================================
# Alerter
# =============================================================================

class Alerter:
    """Main alerting system"""

    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.channels: List[NotificationChannel] = []
        self.rules: List[AlertRule] = []
        self.alert_history: Dict[str, float] = {}  # alert_id -> last_sent_time
        self.lock = threading.Lock()

        # Setup channels from config
        self._setup_channels()

    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load alerting configuration"""
        return {
            # Email settings
            "email_enabled": os.getenv("ALERT_EMAIL_ENABLED", "false").lower() == "true",
            "email_smtp_host": os.getenv("ALERT_SMTP_HOST", "smtp.gmail.com"),
            "email_smtp_port": int(os.getenv("ALERT_SMTP_PORT", "587")),
            "email_from": os.getenv("ALERT_EMAIL_FROM", "noreply@example.com"),
            "email_username": os.getenv("ALERT_EMAIL_USERNAME", ""),
            "email_password": os.getenv("ALERT_EMAIL_PASSWORD", ""),
            "email_to": os.getenv("ALERT_EMAIL_TO", "admin@example.com"),

            # Webhook settings
            "webhook_enabled": os.getenv("ALERT_WEBHOOK_ENABLED", "false").lower() == "true",
            "webhook_url": os.getenv("ALERT_WEBHOOK_URL", ""),

            # Slack settings
            "slack_enabled": os.getenv("ALERT_SLACK_ENABLED", "false").lower() == "true",
            "slack_webhook": os.getenv("ALERT_SLACK_WEBHOOK", ""),

            # Discord settings
            "discord_enabled": os.getenv("ALERT_DISCORD_ENABLED", "false").lower() == "true",
            "discord_webhook": os.getenv("ALERT_DISCORD_WEBHOOK", ""),

            # General settings
            "cooldown_minutes": int(os.getenv("ALERT_COOLDOWN_MINUTES", "60")),
            "max_delivery_attempts": int(os.getenv("ALERT_MAX_ATTEMPTS", "3")),
            "retry_delay_seconds": int(os.getenv("ALERT_RETRY_DELAY", "60")),
        }

    def _setup_channels(self):
        """Setup notification channels from config"""
        # Email channel
        if self.config["email_enabled"] and self.config["email_username"]:
            self.channels.append(EmailChannel(
                smtp_host=self.config["email_smtp_host"],
                smtp_port=self.config["email_smtp_port"],
                from_addr=self.config["email_from"],
                username=self.config["email_username"],
                password=self.config["email_password"]
            ))

        # Webhook channel
        if self.config["webhook_enabled"] and self.config["webhook_url"]:
            self.channels.append(WebhookChannel(
                url=self.config["webhook_url"]
            ))

        # Slack channel
        if self.config["slack_enabled"] and self.config["slack_webhook"]:
            self.channels.append(SlackChannel(
                webhook_url=self.config["slack_webhook"]
            ))

        # Discord channel
        if self.config["discord_enabled"] and self.config["discord_webhook"]:
            self.channels.append(DiscordChannel(
                webhook_url=self.config["discord_webhook"]
            ))

    def add_channel(self, channel: NotificationChannel):
        """Add a notification channel"""
        with self.lock:
            self.channels.append(channel)

    def add_rule(self, rule: AlertRule):
        """Add an alert rule"""
        with self.lock:
            self.rules.append(rule)

    def check_rules(self, context: Dict[str, Any]) -> List[Alert]:
        """Check all rules against context and return triggered alerts"""
        alerts = []

        for rule in self.rules:
            if not rule.enabled:
                continue

            try:
                if rule.condition(context):
                    # Check cooldown
                    alert_id = f"{rule.name}:{context.get('key', 'default')}"
                    last_sent = self.alert_history.get(alert_id, 0)
                    cooldown_seconds = rule.cooldown_minutes * 60

                    if time.time() - last_sent >= cooldown_seconds:
                        alert = Alert(
                            id=alert_id,
                            name=rule.name,
                            message=rule.message,
                            severity=rule.severity,
                            context=context
                        )
                        alerts.append(alert)
            except Exception as e:
                # Log but don't fail other rules
                print(f"Error checking rule {rule.name}: {e}")

        return alerts

    def send_alert(self, name: str, message: str,
                   severity: AlertSeverity = AlertSeverity.WARNING,
                   context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Send an alert.

        Args:
            name: Alert name/title
            message: Alert message
            severity: Alert severity
            context: Additional context data

        Returns:
            True if alert was sent successfully to at least one channel
        """
        alert = Alert(
            id="",
            name=name,
            message=message,
            severity=severity,
            context=context or {}
        )

        return self._send_alert(alert)

    def _send_alert(self, alert: Alert) -> bool:
        """Internal alert sending"""
        with self.lock:
            # Check cooldown
            last_sent = self.alert_history.get(alert.id, 0)
            cooldown_seconds = self.config["cooldown_minutes"] * 60

            if time.time() - last_sent < cooldown_seconds:
                alert.status = AlertStatus.SUPPRESSED
                return False

            # No channels configured
            if not self.channels:
                alert.status = AlertStatus.FAILED
                alert.last_error = "No notification channels configured"
                return False

            # Try to send to all channels
            success = False
            for channel in self.channels:
                try:
                    if channel.send(alert):
                        success = True
                        alert.delivery_attempts += 1
                except Exception as e:
                    alert.last_error = str(e)

            # Update status and history
            if success:
                alert.status = AlertStatus.SENT
                self.alert_history[alert.id] = time.time()

                # Save to alert log
                self._save_alert(alert)
            else:
                alert.status = AlertStatus.FAILED

            return success

    def _save_alert(self, alert: Alert):
        """Save alert to log file"""
        try:
            vault_path = Path(os.getenv("VAULT_PATH", "."))
            alerts_dir = vault_path / "Logs" / "Alerts"
            alerts_dir.mkdir(parents=True, exist_ok=True)

            alert_file = alerts_dir / f"alerts_{datetime.now().strftime('%Y-%m')}.jsonl"

            with open(alert_file, 'a') as f:
                f.write(json.dumps({
                    "id": alert.id,
                    "name": alert.name,
                    "message": alert.message,
                    "severity": alert.severity.value,
                    "timestamp": alert.timestamp,
                    "context": alert.context,
                    "status": alert.status.value
                }) + "\n")

        except Exception as e:
            print(f"Failed to save alert: {e}")

    def check_and_alert(self, context: Dict[str, Any]) -> List[Alert]:
        """Check rules and send alerts for triggered conditions"""
        alerts = self.check_rules(context)

        for alert in alerts:
            self._send_alert(alert)

        return alerts


# =============================================================================
# Built-in Alert Rules
# =============================================================================

class BuiltInRules:
    """Built-in alert rules for common scenarios"""

    @staticmethod
    def high_error_rate(threshold: float = 0.1) -> AlertRule:
        """Alert when error rate exceeds threshold"""
        return AlertRule(
            name="high_error_rate",
            condition=lambda ctx: ctx.get("error_rate", 0) > threshold,
            message=f"Error rate exceeds {threshold * 100:.0f}%",
            severity=AlertSeverity.ERROR,
            cooldown_minutes=30
        )

    @staticmethod
    def sync_lag(threshold_seconds: int = 3600) -> AlertRule:
        """Alert when sync lag exceeds threshold"""
        return AlertRule(
            name="sync_lag",
            condition=lambda ctx: ctx.get("sync_lag_seconds", 0) > threshold_seconds,
            message=f"Sync lag exceeds {threshold_seconds // 60} minutes",
            severity=AlertSeverity.WARNING,
            cooldown_minutes=60
        )

    @staticmethod
    def disk_space(threshold_percent: int = 90) -> AlertRule:
        """Alert when disk space is low"""
        return AlertRule(
            name="disk_space",
            condition=lambda ctx: ctx.get("disk_used_percent", 0) > threshold_percent,
            message=f"Disk usage exceeds {threshold_percent}%",
            severity=AlertSeverity.CRITICAL,
            cooldown_minutes=120
        )

    @staticmethod
    def api_failure() -> AlertRule:
        """Alert when API fails"""
        return AlertRule(
            name="api_failure",
            condition=lambda ctx: ctx.get("api_success", True) == False,
            message="Odoo API request failed",
            severity=AlertSeverity.ERROR,
            cooldown_minutes=5
        )

    @staticmethod
    def circuit_breaker_open() -> AlertRule:
        """Alert when circuit breaker opens"""
        return AlertRule(
            name="circuit_breaker_open",
            condition=lambda ctx: ctx.get("circuit_breaker_state") == "open",
            message="Circuit breaker is OPEN - API calls blocked",
            severity=AlertSeverity.CRITICAL,
            cooldown_minutes=10
        )

    @staticmethod
    def queue_backlog(threshold: int = 1000) -> AlertRule:
        """Alert when queue backlog is high"""
        return AlertRule(
            name="queue_backlog",
            condition=lambda ctx: ctx.get("queue_size", 0) > threshold,
            message=f"Queue backlog exceeds {threshold} items",
            severity=AlertSeverity.WARNING,
            cooldown_minutes=30
        )


# =============================================================================
# Decorator for alerting on errors
# =============================================================================

def alert_on_error(alerter: Alerter, alert_name: str = "function_error"):
    """Decorator to send alert on function error"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                alerter.send_alert(
                    name=alert_name,
                    message=f"Error in {func.__name__}: {str(e)}",
                    severity=AlertSeverity.ERROR,
                    context={"function": func.__name__, "error_type": type(e).__name__}
                )
                raise
        return wrapper
    return decorator


# =============================================================================
# CLI
# =============================================================================

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Odoo Alerting System')
    parser.add_argument('--test', action='store_true', help='Send test alert')
    parser.add_argument('--severity', choices=['info', 'warning', 'error', 'critical'],
                       default='warning', help='Test alert severity')
    parser.add_argument('--message', default='Test alert from Odoo sync',
                       help='Test alert message')

    args = parser.parse_args()

    alerter = Alerter()

    if args.test:
        success = alerter.send_alert(
            name="test_alert",
            message=args.message,
            severity=AlertSeverity[args.severity.upper()],
            context={"test": True}
        )

        if success:
            print("Test alert sent successfully")
            return 0
        else:
            print("Failed to send test alert")
            print(f"  Channels configured: {len(alerter.channels)}")
            return 1

    print("Odoo Alerter - Ready")
    print(f"  Channels: {len(alerter.channels)}")
    print(f"  Rules: {len(alerter.rules)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
