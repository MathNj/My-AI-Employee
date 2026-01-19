#!/usr/bin/env python3
"""
Weekly Audit Generator

Generates a weekly business audit with:
- Tasks completed this week
- Approval workflow metrics
- Watcher health summary
- Business goals progress
- Recommendations for improvements

Silver Tier T084: Implement weekly_audit task
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List
from collections import Counter

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure logging
log_dir = Path("Logs")
log_dir.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "weekly_audit.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("WeeklyAudit")

# Vault paths
VAULT_ROOT = Path("/")
NEEDS_ACTION = VAULT_ROOT / "Needs_Action"
PENDING_APPROVAL = VAULT_ROOT / "Pending_Approval"
APPROVED = VAULT_ROOT / "Approved"
REJECTED = VAULT_ROOT / "Rejected"
DONE = VAULT_ROOT / "Done"
LOGS = VAULT_ROOT / "Logs"


class WeeklyAuditGenerator:
    """
    Generates weekly business audit for AI Employee system
    """

    def __init__(self):
        self.week_start = datetime.now() - timedelta(days=7)
        self.week_end = datetime.now()
        self.audit_data = {}

    def generate_audit(self) -> str:
        """
        Generate complete weekly audit

        Returns:
            Audit markdown content
        """
        logger.info(f"[AUDIT] Generating weekly audit: {self.week_start.strftime('%Y-%m-%d')} to {self.week_end.strftime('%Y-%m-%d')}")

        # Collect audit data
        self.audit_data = {
            'week_start': self.week_start.strftime('%Y-%m-%d'),
            'week_end': self.week_end.strftime('%Y-%m-%d'),
            'generated': self.week_end.isoformat(),
            'tasks_completed': self._get_completed_tasks(),
            'tasks_created': self._get_created_tasks(),
            'approval_metrics': self._get_approval_metrics(),
            'watcher_health': self._get_watcher_health(),
            'business_goals': self._get_business_goals_status(),
            'recommendations': self._generate_recommendations(),
        }

        # Generate markdown
        audit_md = self._generate_markdown()

        logger.info("[AUDIT] Weekly audit generated successfully")
        return audit_md

    def _get_completed_tasks(self) -> Dict:
        """Get tasks completed this week"""
        try:
            if not DONE.exists():
                return {'count': 0, 'tasks': []}

            tasks = []
            for task_file in DONE.glob("*.md"):
                mtime = datetime.fromtimestamp(task_file.stat().st_mtime)
                if mtime > self.week_start:
                    tasks.append({
                        'name': task_file.stem,
                        'completed': mtime.isoformat()
                    })

            return {
                'count': len(tasks),
                'tasks': sorted(tasks, key=lambda x: x['completed'], reverse=True)[:50]
            }

        except Exception as e:
            logger.error(f"[ERROR] Failed to get completed tasks: {e}")
            return {'count': 0, 'tasks': []}

    def _get_created_tasks(self) -> Dict:
        """Get tasks created this week"""
        try:
            if not NEEDS_ACTION.exists():
                return {'count': 0, 'tasks': []}

            tasks = []
            for task_file in NEEDS_ACTION.glob("*.md"):
                mtime = datetime.fromtimestamp(task_file.stat().st_mtime)
                if mtime > self.week_start:
                    tasks.append({
                        'name': task_file.stem,
                        'created': mtime.isoformat()
                    })

            return {
                'count': len(tasks),
                'tasks': sorted(tasks, key=lambda x: x['created'], reverse=True)[:50]
            }

        except Exception as e:
            logger.error(f"[ERROR] Failed to get created tasks: {e}")
            return {'count': 0, 'tasks': []}

    def _get_approval_metrics(self) -> Dict:
        """Get approval workflow metrics"""
        try:
            # Count approved and rejected
            approved_count = 0
            rejected_count = 0

            if APPROVED.exists():
                approved_count = len(list(APPROVED.glob("*.md")))

            if REJECTED.exists():
                rejected_count = len(list(REJECTED.glob("*.md")))

            pending_count = 0
            if PENDING_APPROVAL.exists():
                for approval_file in PENDING_APPROVAL.glob("*.md"):
                    mtime = datetime.fromtimestamp(approval_file.stat().st_mtime)
                    if mtime > self.week_start:
                        pending_count += 1

            total = approved_count + rejected_count + pending_count
            approval_rate = (approved_count / total * 100) if total > 0 else 0

            return {
                'approved': approved_count,
                'rejected': rejected_count,
                'pending': pending_count,
                'total': total,
                'approval_rate': round(approval_rate, 1)
            }

        except Exception as e:
            logger.error(f"[ERROR] Failed to get approval metrics: {e}")
            return {}

    def _get_watcher_health(self) -> Dict:
        """Get watcher health summary from logs"""
        try:
            health_log = LOGS / "watcher_health.log"

            if not health_log.exists():
                return {'status': 'no_data', 'watchers': []}

            # Parse health log (simplified)
            watchers = []
            with open(health_log, 'r', encoding='utf-8') as f:
                for line in f:
                    if 'alive_watchers' in line:
                        # Extract health metrics from log line
                        watchers.append(line.strip())

            return {
                'status': 'monitored',
                'log_entries': len(watchers),
                'latest_checks': watchers[-10:] if watchers else []
            }

        except Exception as e:
            logger.error(f"[ERROR] Failed to get watcher health: {e}")
            return {'status': 'error', 'error': str(e)}

    def _get_business_goals_status(self) -> Dict:
        """Get business goals status"""
        try:
            handbook_path = VAULT_ROOT / "Company_Handbook.md"

            if not handbook_path.exists():
                return {'status': 'not_defined'}

            with open(handbook_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for business goals section
            if "## Business Goals" in content or "## Goals" in content:
                return {
                    'status': 'defined',
                    'last_updated': datetime.fromtimestamp(handbook_path.stat().st_mtime).isoformat()
                }

            return {'status': 'not_found'}

        except Exception as e:
            logger.error(f"[ERROR] Failed to get business goals status: {e}")
            return {'status': 'error'}

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on audit data"""
        recommendations = []

        # Analyze completion rate
        completed = self.audit_data.get('tasks_completed', {}).get('count', 0)
        created = self.audit_data.get('tasks_created', {}).get('count', 0)

        if created > completed * 2:
            recommendations.append("⚠️ **Task Backlog**: Consider reviewing pending tasks to reduce backlog.")

        # Analyze approval rate
        approval_metrics = self.audit_data.get('approval_metrics', {})
        approval_rate = approval_metrics.get('approval_rate', 0)

        if approval_rate < 50:
            recommendations.append("⚠️ **Low Approval Rate**: Review approval workflow to identify bottlenecks.")

        # Check for pending approvals
        pending = approval_metrics.get('pending', 0)
        if pending > 10:
            recommendations.append("⚠️ **Approval Queue**: High number of pending approvals awaiting review.")

        # Business goals status
        goals_status = self.audit_data.get('business_goals', {}).get('status')
        if goals_status == 'not_defined' or goals_status == 'not_found':
            recommendations.append("💡 **Business Goals**: Define clear business goals in Company_Handbook.md.")

        if not recommendations:
            recommendations.append("✅ **Good Standing**: System operating within normal parameters.")

        return recommendations

    def _generate_markdown(self) -> str:
        """Generate audit markdown content"""
        data = self.audit_data

        md = f"""# Weekly Business Audit

**Week**: {data['week_start']} to {data['week_end']}
**Generated**: {data['generated']}

---

## Executive Summary

- **Tasks Completed**: {data['tasks_completed']['count']}
- **Tasks Created**: {data['tasks_created']['count']}
- **Approval Rate**: {data['approval_metrics'].get('approval_rate', 0)}%
- **System Status**: {data['watcher_health'].get('status', 'unknown')}

---

## Tasks Completed This Week

**Total**: {data['tasks_completed']['count']}

{self._format_task_list(data['tasks_completed']['tasks'][:20])}

---

## Tasks Created This Week

**Total**: {data['tasks_created']['count']}

{self._format_task_list(data['tasks_created']['tasks'][:20])}

---

## Approval Workflow Metrics

| Metric | Count |
|--------|-------|
| Approved | {data['approval_metrics'].get('approved', 0)} |
| Rejected | {data['approval_metrics'].get('rejected', 0)} |
| Pending | {data['approval_metrics'].get('pending', 0)} |
| **Total** | {data['approval_metrics'].get('total', 0)} |
| **Approval Rate** | {data['approval_metrics'].get('approval_rate', 0)}% |

---

## Watcher Health

**Status**: {data['watcher_health'].get('status', 'unknown')}
**Log Entries**: {data['watcher_health'].get('log_entries', 0)}

---

## Business Goals

**Status**: {data['business_goals'].get('status', 'unknown')}
{f"**Last Updated**: {data['business_goals'].get('last_updated', 'N/A')}" if data['business_goals'].get('last_updated') else ""}

---

## Recommendations

{chr(10).join(data['recommendations'])}

---

## Detailed Analysis

### Task Completion Rate
{(data['tasks_completed']['count'] / data['tasks_created']['count'] * 100) if data['tasks_created']['count'] > 0 else 0:.1f}% of created tasks were completed this week.

### Approval Efficiency
{data['approval_metrics'].get('approval_rate', 0)}% of approval decisions were approved.

### System Health
Watcher health monitoring: {data['watcher_health'].get('status', 'unknown')}

---

*Generated by Weekly Audit Generator (Silver Tier T084)*
"""

        return md

    def _format_task_list(self, tasks: List[Dict]) -> str:
        """Format task list for markdown"""
        if not tasks:
            return "No tasks."

        lines = []
        for task in tasks:
            name = task.get('name', 'Unknown')
            date_key = 'completed' if 'completed' in task else 'created'
            date = task.get(date_key, 'N/A')[:10]
            lines.append(f"- **{name}** ({date})")

        return "\n".join(lines)

    def save_audit(self, audit_path: str = None) -> Path:
        """
        Save audit to file

        Args:
            audit_path: Path to save audit (default: /Audits/weekly_audit_YYYY-MM-DD.md)

        Returns:
            Path to saved audit
        """
        try:
            # Generate audit
            audit_md = self.generate_audit()

            # Determine save path
            if audit_path is None:
                audit_dir = VAULT_ROOT / "Audits"
                audit_dir.mkdir(parents=True, exist_ok=True)
                audit_path = audit_dir / f"weekly_audit_{self.week_end.strftime('%Y-%m-%d')}.md"

            # Save audit
            with open(audit_path, 'w', encoding='utf-8') as f:
                f.write(audit_md)

            logger.info(f"[AUDIT] Saved to: {audit_path}")
            return Path(audit_path)

        except Exception as e:
            logger.error(f"[ERROR] Failed to save audit: {e}")
            return None


def main():
    """Main entry point for weekly audit generation"""
    logger.info("=" * 60)
    logger.info("Weekly Audit Generator Started (Silver Tier T084)")
    logger.info("=" * 60)

    generator = WeeklyAuditGenerator()

    # Generate and save audit
    audit_path = generator.save_audit()

    if audit_path:
        logger.info(f"[SUCCESS] Weekly audit generated: {audit_path}")
        return 0
    else:
        logger.error("[ERROR] Failed to generate weekly audit")
        return 1


if __name__ == "__main__":
    sys.exit(main())
