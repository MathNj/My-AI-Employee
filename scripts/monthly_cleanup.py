#!/usr/bin/env python3
"""
Monthly Cleanup Script

Performs monthly maintenance tasks:
- Archives old logs (>90 days)
- Cleans up old Done files (>1 year)
- Purges old watcher state entries
- Generates cleanup report

Silver Tier T085: Implement monthly_cleanup task
"""

import os
import sys
import json
import logging
import shutil
import gzip
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure logging
log_dir = Path("Logs")
log_dir.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "monthly_cleanup.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("MonthlyCleanup")

# Vault paths
VAULT_ROOT = Path("/")
LOGS = VAULT_ROOT / "Logs"
DONE = VAULT_ROOT / "Done"
ARCHIVE = VAULT_ROOT / "Archive"
WATCHER_STATE = Path("watchers_state.json")


class MonthlyCleanup:
    """
    Performs monthly cleanup and maintenance tasks
    """

    def __init__(self, log_retention_days: int = 90):
        self.cleanup_date = datetime.now()
        self.log_retention_days = log_retention_days
        self.archive_cutoff = self.cleanup_date - timedelta(days=365)  # 1 year
        self.log_cutoff = self.cleanup_date - timedelta(days=log_retention_days)

        self.cleanup_stats = {
            'logs_archived': 0,
            'logs_deleted': 0,
            'tasks_archived': 0,
            'tasks_deleted': 0,
            'state_rotated': False,
            'disk_space_freed': 0,  # bytes
        }

    def run_cleanup(self) -> Dict:
        """
        Run all cleanup tasks

        Returns:
            Cleanup statistics dictionary
        """
        logger.info("=" * 60)
        logger.info(f"Monthly Cleanup Started: {self.cleanup_date.strftime('%Y-%m-%d')}")
        logger.info("=" * 60)

        # Run cleanup tasks
        logger.info("[CLEANUP] Archiving old logs...")
        self._archive_old_logs()

        logger.info("[CLEANUP] Archiving old completed tasks...")
        self._archive_old_tasks()

        logger.info("[CLEANUP] Rotating watcher state...")
        self._rotate_watcher_state()

        logger.info("[CLEANUP] Compressing archives...")
        self._compress_archives()

        # Generate report
        self._generate_cleanup_report()

        logger.info("[CLEANUP] Monthly cleanup complete")
        logger.info(f"[CLEANUP] Stats: {self.cleanup_stats}")

        return self.cleanup_stats

    def _archive_old_logs(self):
        """Archive logs older than retention period"""
        try:
            if not LOGS.exists():
                logger.warning("[CLEANUP] Logs directory not found")
                return

            archive_dir = LOGS / "Archive"
            archive_dir.mkdir(exist_ok=True)

            archived_count = 0
            deleted_count = 0

            for log_file in LOGS.glob("*.log"):
                # Skip archive directory
                if log_file.parent.name == "Archive":
                    continue

                # Check file age
                mtime = datetime.fromtimestamp(log_file.stat().st_mtime)

                if mtime < self.log_cutoff:
                    # Move to archive
                    archive_path = archive_dir / log_file.name
                    shutil.move(str(log_file), str(archive_path))
                    archived_count += 1
                    self.cleanup_stats['logs_archived'] += 1
                    logger.debug(f"[ARCHIVE] {log_file.name}")

            # Delete very old archived logs (>2 years)
            for archive_file in archive_dir.glob("*.log"):
                mtime = datetime.fromtimestamp(archive_file.stat().st_mtime)
                if mtime < self.log_cutoff - timedelta(days=365):
                    archive_file.unlink()
                    deleted_count += 1
                    self.cleanup_stats['logs_deleted'] += 1
                    logger.debug(f"[DELETE] {archive_file.name}")

            logger.info(f"[CLEANUP] Logs: {archived_count} archived, {deleted_count} deleted")

        except Exception as e:
            logger.error(f"[ERROR] Failed to archive logs: {e}")

    def _archive_old_tasks(self):
        """Archive completed tasks older than 1 year"""
        try:
            if not DONE.exists():
                logger.warning("[CLEANUP] Done directory not found")
                return

            archive_dir = ARCHIVE / "Done"
            archive_dir.mkdir(parents=True, exist_ok=True)

            archived_count = 0
            deleted_count = 0

            for task_file in DONE.glob("*.md"):
                # Check file age
                mtime = datetime.fromtimestamp(task_file.stat().st_mtime)

                if mtime < self.archive_cutoff:
                    # Move to archive
                    archive_path = archive_dir / task_file.name
                    shutil.move(str(task_file), str(archive_path))
                    archived_count += 1
                    self.cleanup_stats['tasks_archived'] += 1
                    self.cleanup_stats['disk_space_freed'] += task_file.stat().st_size
                    logger.debug(f"[ARCHIVE] {task_file.name}")

            # Delete very old archived files (>2 years)
            for archive_file in archive_dir.glob("*.md"):
                mtime = datetime.fromtimestamp(archive_file.stat().st_mtime)
                if mtime < self.archive_cutoff - timedelta(days=365):
                    archive_file.unlink()
                    deleted_count += 1
                    self.cleanup_stats['tasks_deleted'] += 1
                    logger.debug(f"[DELETE] {archive_file.name}")

            logger.info(f"[CLEANUP] Tasks: {archived_count} archived, {deleted_count} deleted")

        except Exception as e:
            logger.error(f"[ERROR] Failed to archive tasks: {e}")

    def _rotate_watcher_state(self):
        """Rotate watchers_state.json to purge old entries"""
        try:
            if not WATCHER_STATE.exists():
                logger.warning("[CLEANUP] watchers_state.json not found")
                return

            # Load state
            with open(WATCHER_STATE, 'r') as f:
                state = json.load(f)

            # Rotate state (purge old entries)
            from watchers.orchestrator import MultiWatcherManager
            manager = MultiWatcherManager()
            manager.rotate_state_file(max_age_hours=24)  # Purge entries older than 24 hours

            self.cleanup_stats['state_rotated'] = True
            logger.info("[CLEANUP] Watcher state rotated")

        except Exception as e:
            logger.error(f"[ERROR] Failed to rotate watcher state: {e}")

    def _compress_archives(self):
        """Compress archive files to save disk space"""
        try:
            archive_dir = ARCHIVE / "Done"
            if not archive_dir.exists():
                return

            compressed_count = 0

            for archive_file in archive_dir.glob("*.md"):
                # Skip already compressed files
                if archive_file.suffix == '.gz':
                    continue

                # Compress file
                compressed_path = archive_dir / f"{archive_file.name}.gz"

                with open(archive_file, 'rb') as f_in:
                    with gzip.open(compressed_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)

                # Get sizes
                original_size = archive_file.stat().st_size
                compressed_size = compressed_path.stat().st_size
                space_saved = original_size - compressed_size

                # Delete original if compression is effective
                if compressed_size < original_size:
                    archive_file.unlink()
                    self.cleanup_stats['disk_space_freed'] += space_saved
                    compressed_count += 1
                    logger.debug(f"[COMPRESS] {archive_file.name} (saved {space_saved} bytes)")

            logger.info(f"[CLEANUP] Compressed {compressed_count} archive files")

        except Exception as e:
            logger.error(f"[ERROR] Failed to compress archives: {e}")

    def _generate_cleanup_report(self):
        """Generate cleanup report and save to file"""
        try:
            report = f"""# Monthly Cleanup Report

**Date**: {self.cleanup_date.strftime('%Y-%m-%d %H:%M:%S')}

---

## Summary

| Metric | Count |
|--------|-------|
| Logs Archived | {self.cleanup_stats['logs_archived']} |
| Logs Deleted | {self.cleanup_stats['logs_deleted']} |
| Tasks Archived | {self.cleanup_stats['tasks_archived']} |
| Tasks Deleted | {self.cleanup_stats['tasks_deleted']} |
| State Rotated | {'Yes' if self.cleanup_stats['state_rotated'] else 'No'} |
| Disk Space Freed | {self._format_bytes(self.cleanup_stats['disk_space_freed'])} |

---

## Details

### Log Retention Policy
- Logs older than {self.log_retention_days} days are archived to /Logs/Archive/
- Archived logs older than 2 years are deleted

### Task Retention Policy
- Completed tasks older than 1 year are archived to /Archive/Done/
- Archived tasks older than 2 years are deleted
- Archives are compressed to save disk space

### Watcher State
- Deduplication state entries older than 24 hours are purged
- State file is rotated to maintain performance

---

## Recommendations

- Review archived logs before deletion if needed for compliance
- Consider exporting important archived tasks to external storage
- Monitor disk space usage to adjust retention policies

---

*Generated by Monthly Cleanup Script (Silver Tier T085)*
"""

            # Save report
            report_path = LOGS / f"cleanup_report_{self.cleanup_date.strftime('%Y-%m')}.md"
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report)

            logger.info(f"[CLEANUP] Report saved to: {report_path}")

        except Exception as e:
            logger.error(f"[ERROR] Failed to generate cleanup report: {e}")

    def _format_bytes(self, bytes_count: int) -> str:
        """Format bytes to human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_count < 1024:
                return f"{bytes_count:.2f} {unit}"
            bytes_count /= 1024
        return f"{bytes_count:.2f} TB"


def main():
    """Main entry point for monthly cleanup"""
    logger.info("Monthly Cleanup Script Started (Silver Tier T085)")

    cleanup = MonthlyCleanup(log_retention_days=90)
    stats = cleanup.run_cleanup()

    logger.info(f"[SUCCESS] Monthly cleanup complete")
    logger.info(f"[SUCCESS] Disk space freed: {cleanup._format_bytes(stats['disk_space_freed'])}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
