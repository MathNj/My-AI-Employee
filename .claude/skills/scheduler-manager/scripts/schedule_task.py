#!/usr/bin/env python3
"""
Schedule Task - Cross-Platform Task Scheduler

Creates scheduled tasks using Windows Task Scheduler or Unix cron.

Usage:
    python schedule_task.py --name "task_name" --command "python script.py" --schedule hourly
    python schedule_task.py --name "dashboard_update" --command "python dashboard_updater.py" --schedule "0 * * * *"
    python schedule_task.py --list
    python schedule_task.py --remove "task_name"
    python schedule_task.py --setup-recommended
"""

import os
import sys
import platform
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
import json

# Vault paths
VAULT_PATH = Path(__file__).parent.parent.parent.parent.absolute()
LOGS = VAULT_PATH / "Logs"
LOGS.mkdir(exist_ok=True)

# Detect platform
PLATFORM = platform.system().lower()

# Recommended schedules for AI Employee
RECOMMENDED_SCHEDULES = {
    'dashboard_update': {
        'name': 'AI_Employee_Dashboard_Update',
        'command': f'python "{VAULT_PATH}/.claude/skills/dashboard-updater/scripts/update_dashboard.py"',
        'schedule': 'hourly',
        'description': 'Update dashboard every hour'
    },
    'approval_processor': {
        'name': 'AI_Employee_Approval_Processor',
        'command': f'python "{VAULT_PATH}/.claude/skills/approval-processor/scripts/process_approvals.py"',
        'schedule': '*/5 * * * *',  # Every 5 minutes
        'description': 'Process approvals every 5 minutes'
    },
    'financial_analysis': {
        'name': 'AI_Employee_Financial_Analysis',
        'command': f'python "{VAULT_PATH}/.claude/skills/financial-analyst/scripts/analyze_finances.py"',
        'schedule': 'daily',
        'description': 'Daily financial analysis at 9 AM'
    },
    'task_processor': {
        'name': 'AI_Employee_Task_Processor',
        'command': f'python "{VAULT_PATH}/.claude/skills/task-processor/scripts/process_tasks.py"',
        'schedule': 'hourly',
        'description': 'Process new tasks hourly'
    }
}

# Schedule patterns
SCHEDULE_PATTERNS = {
    'hourly': '0 * * * *',
    'daily': '0 9 * * *',  # 9 AM daily
    'weekly': '0 9 * * 1',  # 9 AM Monday
    'monthly': '0 9 1 * *',  # 9 AM 1st of month
    'every_5_min': '*/5 * * * *',
    'every_15_min': '*/15 * * * *',
    'every_30_min': '*/30 * * * *'
}


def log_activity(action: str, details: dict):
    """Log scheduling activity."""
    log_file = LOGS / f"scheduler_{datetime.now().strftime('%Y-%m-%d')}.json"

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "details": details,
        "skill": "scheduler-manager"
    }

    try:
        logs = []
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)

        logs.append(log_entry)

        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Warning: Failed to log activity: {e}", file=sys.stderr)


def parse_schedule(schedule_str: str) -> str:
    """Convert schedule string to cron format if needed."""
    # If it's a named pattern, convert to cron
    if schedule_str in SCHEDULE_PATTERNS:
        return SCHEDULE_PATTERNS[schedule_str]

    # If it already looks like cron (5 parts), return as-is
    parts = schedule_str.split()
    if len(parts) == 5:
        return schedule_str

    raise ValueError(f"Invalid schedule format: {schedule_str}")


def create_windows_task(name: str, command: str, schedule: str, description: str = ""):
    """Create scheduled task on Windows using Task Scheduler."""
    try:
        # Parse schedule to determine trigger
        cron_format = parse_schedule(schedule)

        # Convert cron to Task Scheduler parameters
        # Cron format: minute hour day month day_of_week
        parts = cron_format.split()

        minute = parts[0]
        hour = parts[1]

        # Determine schedule type
        if minute == '*/5':
            # Every 5 minutes
            interval = 'MINUTE'
            modifier = '5'
        elif minute == '*/15':
            interval = 'MINUTE'
            modifier = '15'
        elif minute == '*/30':
            interval = 'MINUTE'
            modifier = '30'
        elif minute == '0' and hour == '*':
            # Hourly
            interval = 'HOURLY'
            modifier = '1'
        elif hour.isdigit():
            # Daily at specific hour
            interval = 'DAILY'
            modifier = '1'
            start_time = f"{int(hour):02d}:00"
        else:
            # Default to daily
            interval = 'DAILY'
            modifier = '1'
            start_time = '09:00'

        # Build schtasks command
        cmd = [
            'schtasks',
            '/Create',
            '/TN', name,
            '/TR', command,
            '/SC', interval
        ]

        if interval != 'MINUTE':
            cmd.extend(['/MO', modifier])
        else:
            cmd.extend(['/MO', modifier])

        if 'start_time' in locals():
            cmd.extend(['/ST', start_time])

        cmd.extend(['/F'])  # Force create (overwrite if exists)

        if description:
            # Description not directly supported, add as comment
            pass

        # Execute
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"✅ Task created: {name}")
            log_activity("task_created", {
                "name": name,
                "command": command,
                "schedule": schedule,
                "platform": "windows"
            })
            return True
        else:
            print(f"❌ Failed to create task: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ Error creating Windows task: {e}")
        return False


def create_unix_cron(name: str, command: str, schedule: str, description: str = ""):
    """Create cron job on Linux/Mac."""
    try:
        # Parse schedule to cron format
        cron_format = parse_schedule(schedule)

        # Get current crontab
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)

        if result.returncode == 0:
            current_crontab = result.stdout
        else:
            current_crontab = ""

        # Check if task already exists
        task_marker = f"# AI_Employee: {name}"

        new_lines = []
        skip_next = False
        for line in current_crontab.split('\n'):
            if task_marker in line:
                skip_next = True
                continue
            if skip_next:
                skip_next = False
                continue
            if line.strip():
                new_lines.append(line)

        # Add new task
        new_lines.append(f"{task_marker}")
        new_lines.append(f"{cron_format} {command}")
        new_lines.append("")  # Empty line at end

        # Write new crontab
        new_crontab = '\n'.join(new_lines)

        process = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE, text=True)
        process.communicate(input=new_crontab)

        if process.returncode == 0:
            print(f"✅ Cron job created: {name}")
            log_activity("cron_created", {
                "name": name,
                "command": command,
                "schedule": cron_format,
                "platform": "unix"
            })
            return True
        else:
            print(f"❌ Failed to create cron job")
            return False

    except Exception as e:
        print(f"❌ Error creating cron job: {e}")
        return False


def schedule_task(name: str, command: str, schedule: str, description: str = ""):
    """Create scheduled task (cross-platform)."""
    print(f"Creating scheduled task: {name}")
    print(f"  Command: {command}")
    print(f"  Schedule: {schedule}")
    print(f"  Platform: {PLATFORM}")
    print()

    if PLATFORM == 'windows':
        return create_windows_task(name, command, schedule, description)
    elif PLATFORM in ['linux', 'darwin']:  # darwin = macOS
        return create_unix_cron(name, command, schedule, description)
    else:
        print(f"❌ Unsupported platform: {PLATFORM}")
        return False


def list_windows_tasks():
    """List Windows scheduled tasks."""
    try:
        result = subprocess.run(
            ['schtasks', '/Query', '/FO', 'LIST', '/V'],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            # Parse output
            tasks = []
            current_task = {}

            for line in result.stdout.split('\n'):
                line = line.strip()
                if not line:
                    if current_task:
                        tasks.append(current_task)
                        current_task = {}
                    continue

                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()

                    if key == 'TaskName':
                        current_task['name'] = value
                    elif key == 'Next Run Time':
                        current_task['next_run'] = value
                    elif key == 'Status':
                        current_task['status'] = value
                    elif key == 'Task To Run':
                        current_task['command'] = value

            # Filter for AI Employee tasks
            ai_tasks = [t for t in tasks if 'AI_Employee' in t.get('name', '')]

            return ai_tasks

    except Exception as e:
        print(f"Error listing Windows tasks: {e}")
        return []


def list_unix_crons():
    """List Unix cron jobs."""
    try:
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)

        if result.returncode != 0:
            return []

        cron_jobs = []
        current_name = None

        for line in result.stdout.split('\n'):
            line = line.strip()

            if line.startswith('# AI_Employee:'):
                current_name = line.replace('# AI_Employee:', '').strip()
            elif current_name and line and not line.startswith('#'):
                parts = line.split(None, 5)
                if len(parts) >= 6:
                    schedule = ' '.join(parts[:5])
                    command = parts[5]
                    cron_jobs.append({
                        'name': current_name,
                        'schedule': schedule,
                        'command': command
                    })
                current_name = None

        return cron_jobs

    except Exception as e:
        print(f"Error listing cron jobs: {e}")
        return []


def list_scheduled_tasks():
    """List all scheduled tasks (cross-platform)."""
    print(f"📋 Scheduled Tasks ({PLATFORM})\n")

    if PLATFORM == 'windows':
        tasks = list_windows_tasks()

        if not tasks:
            print("No AI Employee tasks scheduled")
            return

        for task in tasks:
            print(f"**{task['name']}**")
            print(f"  Status: {task.get('status', 'Unknown')}")
            print(f"  Next Run: {task.get('next_run', 'N/A')}")
            print(f"  Command: {task.get('command', 'N/A')}")
            print()

    elif PLATFORM in ['linux', 'darwin']:
        crons = list_unix_crons()

        if not crons:
            print("No AI Employee cron jobs scheduled")
            return

        for cron in crons:
            print(f"**{cron['name']}**")
            print(f"  Schedule: {cron['schedule']}")
            print(f"  Command: {cron['command']}")
            print()


def remove_windows_task(name: str):
    """Remove Windows scheduled task."""
    try:
        result = subprocess.run(
            ['schtasks', '/Delete', '/TN', name, '/F'],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print(f"✅ Task removed: {name}")
            log_activity("task_removed", {"name": name, "platform": "windows"})
            return True
        else:
            print(f"❌ Failed to remove task: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ Error removing task: {e}")
        return False


def remove_unix_cron(name: str):
    """Remove Unix cron job."""
    try:
        # Get current crontab
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)

        if result.returncode != 0:
            print(f"❌ No crontab found")
            return False

        # Remove task
        task_marker = f"# AI_Employee: {name}"
        new_lines = []
        skip_next = False

        for line in result.stdout.split('\n'):
            if task_marker in line:
                skip_next = True
                continue
            if skip_next:
                skip_next = False
                continue
            if line.strip():
                new_lines.append(line)

        # Write new crontab
        new_crontab = '\n'.join(new_lines) + '\n'

        process = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE, text=True)
        process.communicate(input=new_crontab)

        if process.returncode == 0:
            print(f"✅ Cron job removed: {name}")
            log_activity("cron_removed", {"name": name, "platform": "unix"})
            return True
        else:
            print(f"❌ Failed to remove cron job")
            return False

    except Exception as e:
        print(f"❌ Error removing cron job: {e}")
        return False


def remove_scheduled_task(name: str):
    """Remove scheduled task (cross-platform)."""
    print(f"Removing scheduled task: {name}")

    if PLATFORM == 'windows':
        return remove_windows_task(name)
    elif PLATFORM in ['linux', 'darwin']:
        return remove_unix_cron(name)
    else:
        print(f"❌ Unsupported platform: {PLATFORM}")
        return False


def setup_recommended_schedules():
    """Set up recommended schedules for AI Employee."""
    print("🚀 Setting up recommended schedules for AI Employee\n")

    for key, config in RECOMMENDED_SCHEDULES.items():
        print(f"Setting up: {config['name']}")
        print(f"  Description: {config['description']}")

        success = schedule_task(
            config['name'],
            config['command'],
            config['schedule'],
            config['description']
        )

        if success:
            print(f"  ✅ Success\n")
        else:
            print(f"  ❌ Failed\n")

    print("\n✅ Recommended schedules setup complete!")
    print("\nTo view schedules:")
    print(f"  python {__file__} --list")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Manage scheduled tasks for AI Employee'
    )
    parser.add_argument(
        '--name',
        type=str,
        help='Task name'
    )
    parser.add_argument(
        '--command',
        type=str,
        help='Command to execute'
    )
    parser.add_argument(
        '--schedule',
        type=str,
        help='Schedule (hourly, daily, weekly, or cron format)'
    )
    parser.add_argument(
        '--description',
        type=str,
        default='',
        help='Task description'
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all scheduled tasks'
    )
    parser.add_argument(
        '--remove',
        type=str,
        metavar='NAME',
        help='Remove scheduled task by name'
    )
    parser.add_argument(
        '--setup-recommended',
        action='store_true',
        help='Set up recommended schedules for AI Employee'
    )

    args = parser.parse_args()

    if args.list:
        list_scheduled_tasks()
    elif args.remove:
        remove_scheduled_task(args.remove)
    elif args.setup_recommended:
        setup_recommended_schedules()
    elif args.name and args.command and args.schedule:
        schedule_task(args.name, args.command, args.schedule, args.description)
    else:
        parser.print_help()
        print("\n" + "="*60)
        print("Quick Start:")
        print("  --setup-recommended    Set up all recommended AI Employee schedules")
        print("  --list                 View current schedules")
        print("="*60)


if __name__ == '__main__':
    main()
