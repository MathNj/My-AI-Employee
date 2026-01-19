#!/usr/bin/env python3
"""
Daily Briefing Generator

Generates a daily business briefing with:
- Pending tasks summary
- Recent activity log
- Upcoming deadlines
- Business goals progress

Silver Tier T083: Implement daily_briefing task
"""

import os
import sys
import json
import logging
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
        logging.FileHandler(log_dir / "daily_briefing.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("DailyBriefing")

# Vault paths
VAULT_ROOT = Path("/")
NEEDS_ACTION = VAULT_ROOT / "Needs_Action"
PENDING_APPROVAL = VAULT_ROOT / "Pending_Approval"
SCHEDULED = VAULT_ROOT / "Scheduled"
DONE = VAULT_ROOT / "Done"
DASHBOARD = VAULT_ROOT / "Dashboard.md"


class DailyBriefingGenerator:
    """
    Generates daily business briefing for AI Employee system
    """

    def __init__(self):
        self.briefing_date = datetime.now()
        self.briefing_data = {}

    def generate_briefing(self) -> str:
        """
        Generate complete daily briefing

        Returns:
            Briefing markdown content
        """
        logger.info(f"[BRIEFING] Generating daily briefing for {self.briefing_date.strftime('%Y-%m-%d')}")

        # Collect briefing data
        self.briefing_data = {
            'date': self.briefing_date.strftime('%Y-%m-%d'),
            'timestamp': self.briefing_date.isoformat(),
            'pending_tasks': self._get_pending_tasks(),
            'approvals_pending': self._get_pending_approvals(),
            'recent_activity': self._get_recent_activity(),
            'upcoming_deadlines': self._get_upcoming_deadlines(),
            'business_goals': self._get_business_goals_progress(),
        }

        # Generate markdown
        briefing_md = self._generate_markdown()

        logger.info("[BRIEFING] Daily briefing generated successfully")
        return briefing_md

    def _get_pending_tasks(self) -> List[Dict]:
        """Get pending tasks from /Needs_Action"""
        try:
            if not NEEDS_ACTION.exists():
                return []

            tasks = []
            for task_file in NEEDS_ACTION.glob("*.md"):
                tasks.append({
                    'name': task_file.stem,
                    'created': datetime.fromtimestamp(task_file.stat().st_mtime).isoformat()
                })

            return sorted(tasks, key=lambda x: x['created'], reverse=True)[:10]

        except Exception as e:
            logger.error(f"[ERROR] Failed to get pending tasks: {e}")
            return []

    def _get_pending_approvals(self) -> List[Dict]:
        """Get pending approvals from /Pending_Approval"""
        try:
            if not PENDING_APPROVAL.exists():
                return []

            approvals = []
            for approval_file in PENDING_APPROVAL.glob("*.md"):
                approvals.append({
                    'name': approval_file.stem,
                    'created': datetime.fromtimestamp(approval_file.stat().st_mtime).isoformat()
                })

            return sorted(approvals, key=lambda x: x['created'], reverse=True)[:10]

        except Exception as e:
            logger.error(f"[ERROR] Failed to get pending approvals: {e}")
            return []

    def _get_recent_activity(self) -> List[Dict]:
        """Get recent completed tasks from /Done"""
        try:
            if not DONE.exists():
                return []

            # Get tasks completed in last 24 hours
            yesterday = datetime.now() - timedelta(days=1)
            activity = []

            for task_file in DONE.glob("*.md"):
                mtime = datetime.fromtimestamp(task_file.stat().st_mtime)
                if mtime > yesterday:
                    activity.append({
                        'name': task_file.stem,
                        'completed': mtime.isoformat()
                    })

            return sorted(activity, key=lambda x: x['completed'], reverse=True)[:20]

        except Exception as e:
            logger.error(f"[ERROR] Failed to get recent activity: {e}")
            return []

    def _get_upcoming_deadlines(self) -> List[Dict]:
        """Get upcoming deadlines from /Scheduled"""
        try:
            if not SCHEDULED.exists():
                return []

            deadlines = []
            for task_file in SCHEDULED.glob("*.md"):
                deadlines.append({
                    'name': task_file.stem,
                    'scheduled': datetime.fromtimestamp(task_file.stat().st_mtime).isoformat()
                })

            return sorted(deadlines, key=lambda x: x['scheduled'])[:10]

        except Exception as e:
            logger.error(f"[ERROR] Failed to get upcoming deadlines: {e}")
            return []

    def _get_business_goals_progress(self) -> Dict:
        """Get business goals progress from Company_Handbook.md"""
        try:
            handbook_path = VAULT_ROOT / "Company_Handbook.md"
            if not handbook_path.exists():
                return {}

            with open(handbook_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract business goals section (simplified)
            if "## Business Goals" in content:
                return {
                    'goals_defined': True,
                    'last_reviewed': datetime.fromtimestamp(handbook_path.stat().st_mtime).isoformat()
                }

            return {}

        except Exception as e:
            logger.error(f"[ERROR] Failed to get business goals: {e}")
            return {}

    def _generate_markdown(self) -> str:
        """Generate briefing markdown content"""
        data = self.briefing_data

        md = f"""# Daily Business Briefing

**Date**: {data['date']}
**Generated**: {data['timestamp']}

---

## Summary

- **Pending Tasks**: {len(data['pending_tasks'])}
- **Approvals Pending**: {len(data['approvals_pending'])}
- **Completed (24h)**: {len(data['recent_activity'])}
- **Upcoming Deadlines**: {len(data['upcoming_deadlines'])}

---

## Pending Tasks

{self._format_task_list(data['pending_tasks'])}

---

## Pending Approvals

{self._format_task_list(data['approvals_pending'])}

---

## Recent Activity (Last 24 Hours)

{self._format_activity_list(data['recent_activity'])}

---

## Upcoming Deadlines

{self._format_task_list(data['upcoming_deadlines'])}

---

## Business Goals

{self._format_business_goals(data['business_goals'])}

---

*Generated by Daily Briefing Generator (Silver Tier T083)*
"""

        return md

    def _format_task_list(self, tasks: List[Dict]) -> str:
        """Format task list for markdown"""
        if not tasks:
            return "No items."

        lines = []
        for task in tasks[:10]:
            lines.append(f"- **{task['name']}** ({task.get('created', 'N/A')})")

        return "\n".join(lines)

    def _format_activity_list(self, activity: List[Dict]) -> str:
        """Format activity list for markdown"""
        if not activity:
            return "No recent activity."

        lines = []
        for item in activity[:20]:
            lines.append(f"- **{item['name']}** - {item.get('completed', 'N/A')}")

        return "\n".join(lines)

    def _format_business_goals(self, goals: Dict) -> str:
        """Format business goals for markdown"""
        if not goals:
            return "No business goals defined."

        if goals.get('goals_defined'):
            return f"Business goals are defined. Last reviewed: {goals.get('last_reviewed', 'N/A')}"

        return "Business goals not yet defined in Company_Handbook.md"

    def save_briefing(self, briefing_path: str = None) -> Path:
        """
        Save briefing to file

        Args:
            briefing_path: Path to save briefing (default: /Briefings/daily_briefing_YYYY-MM-DD.md)

        Returns:
            Path to saved briefing
        """
        try:
            # Generate briefing
            briefing_md = self.generate_briefing()

            # Determine save path
            if briefing_path is None:
                briefing_dir = VAULT_ROOT / "Briefings"
                briefing_dir.mkdir(parents=True, exist_ok=True)
                briefing_path = briefing_dir / f"daily_briefing_{self.briefing_date.strftime('%Y-%m-%d')}.md"

            # Save briefing
            with open(briefing_path, 'w', encoding='utf-8') as f:
                f.write(briefing_md)

            logger.info(f"[BRIEFING] Saved to: {briefing_path}")
            return Path(briefing_path)

        except Exception as e:
            logger.error(f"[ERROR] Failed to save briefing: {e}")
            return None


def main():
    """Main entry point for daily briefing generation"""
    logger.info("=" * 60)
    logger.info("Daily Briefing Generator Started (Silver Tier T083)")
    logger.info("=" * 60)

    generator = DailyBriefingGenerator()

    # Generate and save briefing
    briefing_path = generator.save_briefing()

    if briefing_path:
        logger.info(f"[SUCCESS] Daily briefing generated: {briefing_path}")
        return 0
    else:
        logger.error("[ERROR] Failed to generate daily briefing")
        return 1


if __name__ == "__main__":
    sys.exit(main())
