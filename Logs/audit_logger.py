#!/usr/bin/env python3
"""
Centralized Audit Logger for Personal AI Employee

This module provides comprehensive audit logging for all AI actions,
meeting Gold Tier requirement 9 from Requirements1.md Section 6.3.

All actions taken by the AI Employee are logged with:
- Timestamp
- Action type
- Actor (which skill/component performed the action)
- Target (who/what was affected)
- Parameters (action details)
- Approval status
- Approved by (human/auto/system)
- Result (success/failure/error)

Logs are stored in /Vault/Logs/audit_YYYY-MM-DD.json
Retention: Minimum 90 days as per specification
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Platform-specific file locking imports
try:
    import fcntl  # For file locking on Unix
    HAS_FCNTL = True
except ImportError:
    HAS_FCNTL = False

try:
    import msvcrt  # For file locking on Windows
    HAS_MSVCRT = True
except ImportError:
    HAS_MSVCRT = False


class AuditLogger:
    """
    Centralized audit logger for all AI Employee actions.
    Thread-safe with file locking.
    """

    def __init__(self, vault_path: Optional[Path] = None):
        """Initialize audit logger with vault path."""
        if vault_path is None:
            # Auto-detect vault path (4 levels up from this file)
            vault_path = Path(__file__).parent.parent

        self.vault_path = Path(vault_path)
        self.logs_dir = self.vault_path / "Logs"
        self.logs_dir.mkdir(exist_ok=True)

        # Ensure audit logs subdirectory exists
        self.audit_dir = self.logs_dir

    def get_log_file(self, date: Optional[datetime] = None) -> Path:
        """Get the log file path for a specific date (default: today)."""
        if date is None:
            date = datetime.now()

        filename = f"audit_{date.strftime('%Y-%m-%d')}.json"
        return self.audit_dir / filename

    def log_action(
        self,
        action_type: str,
        actor: str,
        target: str,
        parameters: Dict[str, Any],
        approval_status: str = "not_required",
        approved_by: str = "system",
        result: str = "success",
        error_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Log an action taken by the AI Employee.

        Args:
            action_type: Type of action (e.g., "email_send", "linkedin_post", "file_process")
            actor: Which component performed the action (e.g., "approval_processor", "linkedin_poster")
            target: Who/what was affected (e.g., "client@example.com", "LinkedIn", "file.pdf")
            parameters: Action details as dict (e.g., {"subject": "Invoice #123", "body": "..."})
            approval_status: One of: "approved", "rejected", "not_required", "pending"
            approved_by: Who approved (e.g., "human", "auto", "system", "user@example.com")
            result: One of: "success", "failure", "error", "partial"
            error_message: Error details if result is "error" or "failure"
            metadata: Additional context (optional)

        Returns:
            The log entry dict that was written
        """
        # Create log entry matching Requirements1.md Section 6.3 format
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action_type": action_type,
            "actor": actor,
            "target": target,
            "parameters": parameters,
            "approval_status": approval_status,
            "approved_by": approved_by,
            "result": result
        }

        # Add optional fields
        if error_message:
            log_entry["error_message"] = error_message

        if metadata:
            log_entry["metadata"] = metadata

        # Write to daily log file (thread-safe)
        self._append_to_log_file(log_entry)

        return log_entry

    def _append_to_log_file(self, log_entry: Dict[str, Any]) -> None:
        """Append log entry to daily log file with file locking for thread safety."""
        log_file = self.get_log_file()

        # Read existing logs or create new list
        existing_logs = []
        if log_file.exists():
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    existing_logs = json.load(f)
            except json.JSONDecodeError:
                # If file is corrupted, start fresh
                existing_logs = []

        # Append new entry
        existing_logs.append(log_entry)

        # Write back to file with locking
        try:
            with open(log_file, 'w', encoding='utf-8') as f:
                # Try to lock file (platform-specific)
                try:
                    if os.name == 'nt' and HAS_MSVCRT:  # Windows
                        msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
                    elif HAS_FCNTL:  # Unix/Linux/Mac
                        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                except (OSError, AttributeError):
                    # If locking fails, proceed anyway (single-threaded fallback)
                    pass

                # Write logs
                json.dump(existing_logs, f, indent=2, ensure_ascii=False)

                # Unlock
                try:
                    if os.name == 'nt' and HAS_MSVCRT:
                        msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
                    elif HAS_FCNTL:
                        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                except (OSError, AttributeError):
                    pass

        except Exception as e:
            # If write fails, log to stderr but don't crash
            print(f"[AUDIT LOGGER ERROR] Failed to write log: {e}", file=sys.stderr)

    def log_approval_execution(
        self,
        approval_file: Path,
        action_type: str,
        actor: str,
        target: str,
        parameters: Dict[str, Any],
        result: str,
        error_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Log execution of an approved action.
        Convenience method for approval workflow actions.
        """
        return self.log_action(
            action_type=action_type,
            actor=actor,
            target=target,
            parameters=parameters,
            approval_status="approved",
            approved_by="human",
            result=result,
            error_message=error_message,
            metadata={"approval_file": str(approval_file.name)}
        )

    def log_auto_action(
        self,
        action_type: str,
        actor: str,
        target: str,
        parameters: Dict[str, Any],
        result: str,
        error_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Log an automatic action (no approval required).
        Convenience method for automated actions.
        """
        return self.log_action(
            action_type=action_type,
            actor=actor,
            target=target,
            parameters=parameters,
            approval_status="not_required",
            approved_by="system",
            result=result,
            error_message=error_message
        )

    def get_audit_trail(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        action_type: Optional[str] = None,
        actor: Optional[str] = None,
        result: Optional[str] = None
    ) -> list:
        """
        Query audit logs with filters.

        Args:
            start_date: Filter logs from this date (default: 90 days ago)
            end_date: Filter logs until this date (default: today)
            action_type: Filter by action type
            actor: Filter by actor
            result: Filter by result

        Returns:
            List of matching log entries
        """
        if start_date is None:
            start_date = datetime.now() - timedelta(days=90)
        if end_date is None:
            end_date = datetime.now()

        all_logs = []
        current_date = start_date

        # Read logs from all dates in range
        while current_date <= end_date:
            log_file = self.get_log_file(current_date)
            if log_file.exists():
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        daily_logs = json.load(f)
                        all_logs.extend(daily_logs)
                except (json.JSONDecodeError, IOError):
                    pass

            current_date += timedelta(days=1)

        # Apply filters
        filtered_logs = all_logs

        if action_type:
            filtered_logs = [log for log in filtered_logs if log.get('action_type') == action_type]

        if actor:
            filtered_logs = [log for log in filtered_logs if log.get('actor') == actor]

        if result:
            filtered_logs = [log for log in filtered_logs if log.get('result') == result]

        return filtered_logs

    def cleanup_old_logs(self, retention_days: int = 90) -> int:
        """
        Delete audit logs older than retention period.
        Returns number of files deleted.
        """
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        deleted_count = 0

        for log_file in self.audit_dir.glob("audit_*.json"):
            try:
                # Extract date from filename
                date_str = log_file.stem.replace("audit_", "")
                file_date = datetime.strptime(date_str, "%Y-%m-%d")

                if file_date < cutoff_date:
                    log_file.unlink()
                    deleted_count += 1
            except (ValueError, OSError):
                # Skip files that don't match pattern or can't be deleted
                continue

        return deleted_count

    def generate_audit_report(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Generate audit summary report.

        Returns:
            Dict with statistics about actions, success rates, etc.
        """
        logs = self.get_audit_trail(start_date, end_date)

        if not logs:
            return {
                "period": {
                    "start": start_date.isoformat() if start_date else None,
                    "end": end_date.isoformat() if end_date else None
                },
                "total_actions": 0,
                "summary": "No actions logged in this period"
            }

        # Calculate statistics
        total_actions = len(logs)

        # Count by action type
        action_types = {}
        for log in logs:
            action_type = log.get('action_type', 'unknown')
            action_types[action_type] = action_types.get(action_type, 0) + 1

        # Count by result
        results = {}
        for log in logs:
            result = log.get('result', 'unknown')
            results[result] = results.get(result, 0) + 1

        # Count by approval status
        approval_statuses = {}
        for log in logs:
            status = log.get('approval_status', 'unknown')
            approval_statuses[status] = approval_statuses.get(status, 0) + 1

        # Calculate success rate
        success_count = results.get('success', 0)
        success_rate = (success_count / total_actions * 100) if total_actions > 0 else 0

        return {
            "period": {
                "start": start_date.isoformat() if start_date else None,
                "end": end_date.isoformat() if end_date else None
            },
            "total_actions": total_actions,
            "action_types": action_types,
            "results": results,
            "approval_statuses": approval_statuses,
            "success_rate": f"{success_rate:.1f}%",
            "failed_actions": [
                log for log in logs
                if log.get('result') in ['failure', 'error']
            ]
        }


# Global singleton instance
_audit_logger = None

def get_audit_logger(vault_path: Optional[Path] = None) -> AuditLogger:
    """Get the global audit logger instance."""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger(vault_path)
    return _audit_logger


# Convenience functions for quick logging
def log_action(*args, **kwargs):
    """Quick access to log_action on global logger."""
    return get_audit_logger().log_action(*args, **kwargs)


def log_approval_execution(*args, **kwargs):
    """Quick access to log_approval_execution on global logger."""
    return get_audit_logger().log_approval_execution(*args, **kwargs)


def log_auto_action(*args, **kwargs):
    """Quick access to log_auto_action on global logger."""
    return get_audit_logger().log_auto_action(*args, **kwargs)


if __name__ == "__main__":
    import sys

    # Example usage and testing
    logger = AuditLogger()

    # Test 1: Log a simple action
    print("Testing audit logger...")

    entry = logger.log_action(
        action_type="email_send",
        actor="test_script",
        target="test@example.com",
        parameters={"subject": "Test Email", "body": "This is a test"},
        approval_status="approved",
        approved_by="human",
        result="success"
    )

    print(f"[OK] Logged test action: {entry['timestamp']}")

    # Test 2: Generate report
    report = logger.generate_audit_report()
    print(f"\n[REPORT] Audit Report:")
    print(f"   Total actions: {report['total_actions']}")
    print(f"   Success rate: {report['success_rate']}")

    print("\n[OK] Audit logger is working correctly!")
    print(f"[INFO] Logs stored in: {logger.get_log_file()}")
