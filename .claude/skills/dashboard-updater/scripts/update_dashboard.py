#!/usr/bin/env python3
"""
Dashboard Updater for Personal AI Employee

Updates Dashboard.md with current system status, task counts,
and recent activity.
"""

from pathlib import Path
from datetime import datetime, timedelta
import json
import logging


# Configuration
VAULT_PATH = Path(__file__).parent.parent.parent.parent.parent.resolve()
DASHBOARD_PATH = VAULT_PATH / "Dashboard.md"
NEEDS_ACTION_PATH = VAULT_PATH / "Needs_Action"
PLANS_PATH = VAULT_PATH / "Plans"
PENDING_APPROVAL_PATH = VAULT_PATH / "Pending_Approval"
APPROVED_PATH = VAULT_PATH / "Approved"
DONE_PATH = VAULT_PATH / "Done"
LOGS_PATH = VAULT_PATH / "Logs"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DashboardUpdater:
    """Update Dashboard.md with current system status"""

    def __init__(self):
        self.vault_path = VAULT_PATH

    def count_files_in_folder(self, folder_path):
        """Count .md files in a folder"""
        try:
            if not folder_path.exists():
                return 0
            return len([f for f in folder_path.iterdir()
                       if f.is_file() and f.suffix == '.md'])
        except Exception as e:
            logger.error(f"Error counting files in {folder_path}: {e}")
            return 0

    def count_recent_completions(self, days=1):
        """Count files completed in the last N days"""
        try:
            if not DONE_PATH.exists():
                return 0

            cutoff_time = datetime.now() - timedelta(days=days)
            count = 0

            for file in DONE_PATH.iterdir():
                if file.is_file() and file.suffix == '.md':
                    if datetime.fromtimestamp(file.stat().st_mtime) > cutoff_time:
                        count += 1

            return count
        except Exception as e:
            logger.error(f"Error counting recent completions: {e}")
            return 0

    def get_recent_actions(self, limit=10):
        """Get recent actions from log files"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            log_file = LOGS_PATH / f"actions_{today}.json"

            if not log_file.exists():
                return []

            logs = json.loads(log_file.read_text())

            # Get last N entries
            recent = logs[-limit:] if len(logs) > limit else logs

            return list(reversed(recent))  # Most recent first
        except Exception as e:
            logger.error(f"Error reading logs: {e}")
            return []

    def check_for_alerts(self):
        """Check for items needing attention"""
        alerts = []

        # Check for stale approval requests
        if PENDING_APPROVAL_PATH.exists():
            for file in PENDING_APPROVAL_PATH.iterdir():
                if file.is_file():
                    age_hours = (datetime.now() - datetime.fromtimestamp(file.stat().st_mtime)).total_seconds() / 3600
                    if age_hours > 24:
                        alerts.append(f"Approval pending >24h: {file.name}")

        # Check for high priority tasks
        if NEEDS_ACTION_PATH.exists():
            for file in NEEDS_ACTION_PATH.iterdir():
                if file.is_file() and file.suffix == '.md':
                    content = file.read_text(encoding='utf-8')
                    if 'priority: high' in content.lower():
                        alerts.append(f"High priority task: {file.name}")

        return alerts

    def generate_dashboard_content(self):
        """Generate complete dashboard content"""
        now = datetime.now()
        timestamp = now.strftime('%Y-%m-%d %H:%M:%S')

        # Collect statistics
        needs_action = self.count_files_in_folder(NEEDS_ACTION_PATH)
        plans = self.count_files_in_folder(PLANS_PATH)
        pending_approval = self.count_files_in_folder(PENDING_APPROVAL_PATH)
        completed_today = self.count_recent_completions(days=1)
        completed_week = self.count_recent_completions(days=7)

        # Get recent actions
        recent_actions = self.get_recent_actions(10)

        # Check for alerts
        alerts = self.check_for_alerts()

        # Generate content
        content = f"""# AI Employee Dashboard

---
last_updated: {timestamp}
status: active
tier: bronze
---

## System Status

**Vault Location:** `{self.vault_path}`
**Watchers Running:** Check /watchers folder
**Pending Tasks:** {needs_action}
**Completed Today:** {completed_today}

## Quick Stats

| Metric | Count |
|--------|-------|
| Tasks in Needs_Action | {needs_action} |
| Plans Generated | {plans} |
| Pending Approval | {pending_approval} |
| Completed (Today) | {completed_today} |
| Completed (This Week) | {completed_week} |

## Recent Activity

"""

        if recent_actions:
            content += "| Timestamp | Action | Status | Details |\n"
            content += "|-----------|--------|--------|---------||\n"
            for action in recent_actions:
                ts = action.get('timestamp', 'N/A')[:19]  # Trim to readable format
                act = action.get('action', 'unknown')
                details = action.get('details', {})
                status = details.get('outcome', 'completed')
                detail_str = str(details.get('task', ''))[:40]  # Limit length
                content += f"| {ts} | {act} | {status} | {detail_str} |\n"
        else:
            content += "*No recent activity*\n"

        content += "\n## Alerts & Notifications\n\n"

        if alerts:
            for alert in alerts:
                content += f"- ⚠️ {alert}\n"
        else:
            content += "*No alerts*\n"

        content += f"""
## System Health

- {'✅' if needs_action < 10 else '⚠️'} Needs Action: {needs_action} tasks
- {'✅' if pending_approval == 0 else '⚠️'} Pending Approval: {pending_approval} items
- {'✅' if plans < 20 else '⚠️'} Active Plans: {plans}
- ✅ Vault structure: OK

---

## Quick Actions

- 📥 Drop files in `/Inbox` to create tasks
- 📝 Check `/Needs_Action` for pending tasks
- ✅ Review `/Done` for completed tasks
- 📊 View `/Logs` for audit trail

---

*Last refreshed: {timestamp}*
*Generated by Personal AI Employee v0.1 (Bronze Tier)*
"""

        return content

    def update_dashboard(self):
        """Update Dashboard.md file"""
        try:
            content = self.generate_dashboard_content()
            DASHBOARD_PATH.write_text(content, encoding='utf-8')
            logger.info(f"Dashboard updated successfully: {DASHBOARD_PATH}")
            return True
        except Exception as e:
            logger.error(f"Error updating dashboard: {e}")
            return False


def main():
    """Entry point"""
    updater = DashboardUpdater()

    print("Updating Dashboard...")
    print("-" * 50)

    success = updater.update_dashboard()

    if success:
        print("[OK] Dashboard updated successfully")
        print(f"  Location: {DASHBOARD_PATH}")
    else:
        print("[FAIL] Dashboard update failed")
        return 1

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
