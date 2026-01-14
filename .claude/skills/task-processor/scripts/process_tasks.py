#!/usr/bin/env python3
"""
Task Processor for Personal AI Employee

Processes tasks from Needs_Action folder, creates plans,
and manages the workflow.
"""

from pathlib import Path
from datetime import datetime
import json
import logging


# Configuration
VAULT_PATH = Path(__file__).parent.parent.parent.parent.parent.resolve()
NEEDS_ACTION_PATH = VAULT_PATH / "Needs_Action"
PLANS_PATH = VAULT_PATH / "Plans"
DONE_PATH = VAULT_PATH / "Done"
LOGS_PATH = VAULT_PATH / "Logs"

# Setup logging
LOGS_PATH.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_PATH / 'task_processor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TaskProcessor:
    """Process tasks from Needs_Action folder"""

    def __init__(self):
        self.needs_action = NEEDS_ACTION_PATH
        self.plans = PLANS_PATH
        self.done = DONE_PATH

        # Ensure directories exist
        self.needs_action.mkdir(exist_ok=True)
        self.plans.mkdir(exist_ok=True)
        self.done.mkdir(exist_ok=True)

    def get_pending_tasks(self):
        """Get all task files from Needs_Action"""
        try:
            task_files = [f for f in self.needs_action.iterdir()
                         if f.is_file() and f.suffix == '.md']
            return sorted(task_files, key=lambda x: x.stat().st_mtime)
        except Exception as e:
            logger.error(f"Error reading tasks: {e}")
            return []

    def parse_task_metadata(self, task_file):
        """Parse frontmatter metadata from task file"""
        try:
            content = task_file.read_text(encoding='utf-8')

            # Simple frontmatter parsing
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    frontmatter = parts[1].strip()
                    body = parts[2].strip()

                    # Parse YAML-like frontmatter
                    metadata = {}
                    for line in frontmatter.split('\n'):
                        if ':' in line:
                            key, value = line.split(':', 1)
                            metadata[key.strip()] = value.strip()

                    return metadata, body

            return {}, content
        except Exception as e:
            logger.error(f"Error parsing {task_file.name}: {e}")
            return {}, ""

    def create_plan(self, task_file, metadata, body):
        """Create action plan for a task"""
        timestamp = datetime.now().isoformat()
        plan_filename = f"PLAN_{task_file.stem}.md"
        plan_path = self.plans / plan_filename

        task_type = metadata.get('type', 'unknown')
        priority = metadata.get('priority', 'medium')

        plan_content = f"""---
task_id: {task_file.name}
created: {timestamp}
status: pending
task_type: {task_type}
priority: {priority}
---

# Action Plan: {task_file.stem}

## Task Summary
**Type:** {task_type}
**Priority:** {priority}
**Detected:** {metadata.get('detected', 'unknown')}

## Analysis
This task was detected from: {metadata.get('source_file', 'unknown source')}

The task requires:
1. Review of the item
2. Categorization and filing
3. Potential action based on content

## Proposed Actions
- [ ] Review task details
- [ ] Analyze content/requirements
- [ ] Determine appropriate action
- [ ] Execute or request approval
- [ ] Archive to Done

## Notes
Task is ready for processing. Review Company_Handbook.md for any relevant rules.

## Execution Log
*Actions will be logged here as they are completed*
"""

        plan_path.write_text(plan_content, encoding='utf-8')
        logger.info(f"Created plan: {plan_filename}")

        return plan_path

    def move_to_done(self, task_file, plan_file=None):
        """Archive completed task and plan to Done folder"""
        try:
            # Move task file
            task_dest = self.done / task_file.name
            task_file.rename(task_dest)
            logger.info(f"Archived task: {task_file.name}")

            # Move plan file if it exists
            if plan_file and plan_file.exists():
                plan_dest = self.done / plan_file.name
                plan_file.rename(plan_dest)
                logger.info(f"Archived plan: {plan_file.name}")

            return True
        except Exception as e:
            logger.error(f"Error archiving files: {e}")
            return False

    def log_action(self, action, details):
        """Log action to JSON log file"""
        log_file = LOGS_PATH / f"actions_{datetime.now().strftime('%Y-%m-%d')}.json"

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details
        }

        try:
            # Append to log file
            logs = []
            if log_file.exists():
                logs = json.loads(log_file.read_text())

            logs.append(log_entry)
            log_file.write_text(json.dumps(logs, indent=2))
        except Exception as e:
            logger.error(f"Error writing log: {e}")

    def process_all_tasks(self):
        """Process all pending tasks"""
        logger.info("=== Task Processor Started ===")

        tasks = self.get_pending_tasks()
        logger.info(f"Found {len(tasks)} pending task(s)")

        if not tasks:
            logger.info("No tasks to process")
            return

        for task_file in tasks:
            logger.info(f"Processing: {task_file.name}")

            # Parse task
            metadata, body = self.parse_task_metadata(task_file)

            # Create plan
            plan_file = self.create_plan(task_file, metadata, body)

            # Log the action
            self.log_action("task_processed", {
                "task": task_file.name,
                "type": metadata.get('type', 'unknown'),
                "plan": plan_file.name
            })

            logger.info(f"✓ Created plan for: {task_file.name}")

        logger.info(f"=== Processed {len(tasks)} task(s) ===")
        logger.info(f"Plans created in: {self.plans}")
        logger.info("Review plans and execute or request approval as needed.")

    def show_status(self):
        """Show current status of tasks"""
        pending = self.get_pending_tasks()
        plans = list(self.plans.glob('*.md'))
        completed = list(self.done.glob('*.md'))

        print("\n" + "=" * 50)
        print("TASK PROCESSOR STATUS")
        print("=" * 50)
        print(f"Pending Tasks:     {len(pending)}")
        print(f"Action Plans:      {len(plans)}")
        print(f"Completed Tasks:   {len(completed)}")
        print("=" * 50)

        if pending:
            print("\nPending Tasks:")
            for task in pending:
                metadata, _ = self.parse_task_metadata(task)
                priority = metadata.get('priority', 'medium')
                task_type = metadata.get('type', 'unknown')
                print(f"  - {task.name} [{priority}] ({task_type})")

        print()


def main():
    """Entry point"""
    import sys

    processor = TaskProcessor()

    if len(sys.argv) > 1 and sys.argv[1] == "status":
        processor.show_status()
    else:
        processor.process_all_tasks()


if __name__ == "__main__":
    main()
