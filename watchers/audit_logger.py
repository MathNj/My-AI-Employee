#!/usr/bin/env python3
"""
Audit Logging System for AI Employee

Standardized JSON logging across all skills and actions.

Usage:
    from watchers.audit_logger import log_action, log_email_sent, log_approval

    # Generic action log
    log_action(
        action_type="file_processing",
        actor="filesystem_watcher",
        target="/path/to/file.pdf",
        result="success",
        skill="filesystem-watcher"
    )

    # Email-specific log
    log_email_sent(
        to="client@example.com",
        subject="Invoice #1234",
        result="success",
        skill="email-sender"
    )
"""

import json
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Any

# Configure logging
logger = logging.getLogger(__name__)


class AuditLogger:
    """
    Centralized audit logging for all AI Employee actions

    All actions must be logged with:
    - timestamp
    - action_type
    - actor (which skill/watcher)
    - result (success/error)
    - Optional: target, parameters, approval status, error, skill, duration
    """

    def __init__(self, vault_path: Optional[Path] = None):
        """
        Initialize audit logger

        Args:
            vault_path: Path to vault (defaults to auto-detect)
        """
        if vault_path is None:
            vault_path = Path(__file__).parent.parent.absolute()

        self.vault_path = vault_path
        self.logs_path = vault_path / "Logs"
        self.logs_path.mkdir(exist_ok=True)

        # Configuration
        self.retention_days = 90
        self.required_fields = ["timestamp", "action_type", "actor", "result"]
        self.optional_fields = ["target", "parameters", "approval_status", "approved_by", "skill", "duration_ms", "error"]

    def log(
        self,
        action_type: str,
        actor: str,
        result: str,
        target: Optional[str] = None,
        parameters: Optional[Dict] = None,
        approval_status: Optional[str] = None,
        approved_by: Optional[str] = None,
        skill: Optional[str] = None,
        duration_ms: Optional[int] = None,
        error: Optional[str] = None,
        additional_fields: Optional[Dict] = None
    ) -> Dict:
        """
        Log an action with standard format

        Args:
            action_type: Type of action (email_send, approval, social_post, etc.)
            actor: Who performed the action (skill name, watcher name)
            result: success or error
            target: Target of action (email address, file path, etc.)
            parameters: Additional parameters (dict)
            approval_status: approved, rejected, pending
            approved_by: auto_approver, human, system
            skill: Which skill performed the action
            duration_ms: How long the action took (milliseconds)
            error: Error message if result is "error"
            additional_fields: Any other fields to include

        Returns:
            The log entry that was created
        """
        # Build log entry
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action_type": action_type,
            "actor": actor,
            "result": result
        }

        # Add optional fields if provided
        if target:
            log_entry["target"] = target
        if parameters:
            log_entry["parameters"] = parameters
        if approval_status:
            log_entry["approval_status"] = approval_status
        if approved_by:
            log_entry["approved_by"] = approved_by
        if skill:
            log_entry["skill"] = skill
        if duration_ms is not None:
            log_entry["duration_ms"] = duration_ms
        if error:
            log_entry["error"] = error
        if additional_fields:
            log_entry.update(additional_fields)

        # Validate required fields
        missing_fields = [f for f in self.required_fields if f not in log_entry]
        if missing_fields:
            logger.error(f"Missing required fields: {missing_fields}")
            return {}

        # Write to log file
        self._write_log(log_entry)

        return log_entry

    def _write_log(self, log_entry: Dict) -> bool:
        """
        Write log entry to daily log file

        Args:
            log_entry: The log entry to write

        Returns:
            True if successful
        """
        try:
            log_file = self.logs_path / f"audit_{datetime.now().strftime('%Y-%m-%d')}.json"

            # Read existing logs
            logs = []
            if log_file.exists():
                try:
                    logs = json.loads(log_file.read_text(encoding='utf-8'))
                except json.JSONDecodeError:
                    logs = []

            # Add new entry
            logs.append(log_entry)

            # Write back
            log_file.write_text(json.dumps(logs, indent=2), encoding='utf-8')

            return True

        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")
            return False

    def cleanup_old_logs(self):
        """
        Remove log files older than retention period
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=self.retention_days)

            for log_file in self.logs_path.glob("audit_*.json"):
                # Extract date from filename
                try:
                    date_str = log_file.stem.split('_')[1]  # audit_YYYY-MM-DD.json
                    file_date = datetime.strptime(date_str, '%Y-%m-%d')

                    if file_date < cutoff_date:
                        log_file.unlink()
                        logger.info(f"Removed old log file: {log_file.name}")

                except (ValueError, IndexError):
                    # Invalid filename format, skip
                    pass

        except Exception as e:
            logger.error(f"Failed to cleanup old logs: {e}")


# Singleton instance
_audit_logger = None

def get_audit_logger(vault_path: Optional[Path] = None) -> AuditLogger:
    """Get or create the singleton audit logger instance"""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger(vault_path)
    return _audit_logger


# Convenience functions for common action types

def log_action(
    action_type: str,
    actor: str,
    result: str,
    **kwargs
) -> Dict:
    """
    Log a generic action

    Usage:
        log_action(
            action_type="file_processing",
            actor="filesystem_watcher",
            target="/path/to/file.pdf",
            result="success",
            skill="filesystem-watcher"
        )
    """
    return get_audit_logger().log(
        action_type=action_type,
        actor=actor,
        result=result,
        **kwargs
    )


def log_email_sent(
    to: str,
    subject: str,
    result: str,
    actor: str = "email_sender",
    has_attachments: bool = False,
    approval_status: Optional[str] = None,
    approved_by: Optional[str] = None,
    duration_ms: Optional[int] = None,
    error: Optional[str] = None
) -> Dict:
    """
    Log an email send action

    Usage:
        log_email_sent(
            to="client@example.com",
            subject="Invoice #1234",
            result="success",
            approval_status="approved",
            approved_by="auto_approver"
        )
    """
    return get_audit_logger().log(
        action_type="email_send",
        actor=actor,
        target=to,
        parameters={
            "subject": subject,
            "has_attachments": has_attachments
        },
        approval_status=approval_status,
        approved_by=approved_by,
        result=result,
        skill="email-sender",
        duration_ms=duration_ms,
        error=error
    )


def log_social_post(
    platform: str,
    content: str,
    result: str,
    actor: str = "social_media_manager",
    post_url: Optional[str] = None,
    approval_status: Optional[str] = None,
    approved_by: Optional[str] = None,
    duration_ms: Optional[int] = None,
    error: Optional[str] = None
) -> Dict:
    """
    Log a social media post action

    Usage:
        log_social_post(
            platform="linkedin",
            content="Just launched our new product!",
            result="success",
            post_url="https://linkedin.com/posts/12345"
        )
    """
    return get_audit_logger().log(
        action_type="social_post",
        actor=actor,
        target=platform,
        parameters={
            "content_preview": content[:100] + "..." if len(content) > 100 else content,
            "post_url": post_url
        },
        approval_status=approval_status,
        approved_by=approved_by,
        result=result,
        skill=f"{platform.lower()}-poster",
        duration_ms=duration_ms,
        error=error
    )


def log_approval(
    item_type: str,
    item_id: str,
    decision: str,
    actor: str = "auto_approver",
    confidence: Optional[float] = None,
    reasoning: Optional[str] = None,
    duration_ms: Optional[int] = None
) -> Dict:
    """
    Log an approval decision

    Usage:
        log_approval(
            item_type="email",
            item_id="EMAIL_client_123",
            decision="approve",
            confidence=0.92,
            reasoning="Known contact with 15+ interactions"
        )
    """
    return get_audit_logger().log(
        action_type="approval",
        actor=actor,
        target=item_id,
        parameters={
            "item_type": item_type,
            "decision": decision,
            "confidence": confidence
        },
        approval_status=decision,
        result="success" if decision in ["approve", "reject"] else "error",
        skill="auto-approver",
        duration_ms=duration_ms,
        error=reasoning if decision == "hold" else None
    )


def log_error(
    action_type: str,
    actor: str,
    error: str,
    context: Optional[Dict] = None,
    skill: Optional[str] = None
) -> Dict:
    """
    Log an error

    Usage:
        log_error(
            action_type="email_send",
            actor="email_sender",
            error="SMTP connection timeout",
            context={"to": "client@example.com"},
            skill="email-sender"
        )
    """
    return get_audit_logger().log(
        action_type=action_type,
        actor=actor,
        result="error",
        error=error,
        parameters=context,
        skill=skill
    )


def search_logs(
    action_type: Optional[str] = None,
    skill: Optional[str] = None,
    result: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> list:
    """
    Search logs by criteria

    Args:
        action_type: Filter by action type (email_send, approval, etc.)
        skill: Filter by skill (email-sender, auto-approver, etc.)
        result: Filter by result (success, error)
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)

    Returns:
        List of matching log entries
    """
    audit_logger = get_audit_logger()
    logs_path = audit_logger.logs_path

    matching_logs = []

    # Determine which log files to search
    if start_date and end_date:
        # Search specific date range
        from datetime import datetime, timedelta

        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')

        current = start
        while current <= end:
            log_file = logs_path / f"audit_{current.strftime('%Y-%m-%d')}.json"
            if log_file.exists():
                matching_logs.extend(_search_file(log_file, action_type, skill, result))
            current += timedelta(days=1)

    else:
        # Search all log files
        for log_file in logs_path.glob("audit_*.json"):
            matching_logs.extend(_search_file(log_file, action_type, skill, result))

    return matching_logs


def _search_file(log_file: Path, action_type: Optional[str], skill: Optional[str], result: Optional[str]) -> list:
    """Search a single log file for matching entries"""
    try:
        logs = json.loads(log_file.read_text(encoding='utf-8'))

        filtered = logs
        if action_type:
            filtered = [log for log in filtered if log.get('action_type') == action_type]
        if skill:
            filtered = [log for log in filtered if log.get('skill') == skill]
        if result:
            filtered = [log for log in filtered if log.get('result') == result]

        return filtered

    except Exception as e:
        logger.error(f"Error searching {log_file}: {e}")
        return []
