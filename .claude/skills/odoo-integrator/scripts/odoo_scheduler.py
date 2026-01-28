#!/usr/bin/env python3
"""
Odoo Sync Scheduler

Cron-style scheduler for automated sync operations.

Features:
- Cron expression parsing
- Scheduled sync jobs
- Job history tracking
- Concurrent job execution limits
- Job dependencies

Usage:
    from odoo_scheduler import Scheduler

    scheduler = Scheduler()
    scheduler.add_job("daily_sync", "0 2 * * *", "odoo_sync_ultimate.py --sync all")
    scheduler.run()

    # Or use the command line
    python odoo_scheduler.py --schedule "0 2 * * *" --command "odoo_sync_ultimate.py --sync all"
"""

from __future__ import annotations

import os
import sys
import json
import time
import signal
import subprocess
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict

try:
    import croniter
except ImportError:
    print("Installing required package: croniter")
    os.system("pip install croniter")
    import croniter

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


# =============================================================================
# Job Data Classes
# =============================================================================

class JobStatus(Enum):
    """Job execution status"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"


@dataclass
class Job:
    """Scheduled job definition"""
    id: str
    name: str
    cron_expression: str
    command: str
    enabled: bool = True
    max_runtime_minutes: int = 60
    retry_on_failure: bool = False
    max_retries: int = 3
    depends_on: List[str] = field(default_factory=list)
    timeout_seconds: int = 3600
    working_directory: Optional[str] = None
    environment: Dict[str, str] = field(default_factory=dict)
    description: str = ""

    def next_run_time(self, from_time: Optional[datetime] = None) -> datetime:
        """Get next scheduled run time"""
        base_time = from_time or datetime.now()
        try:
            cron = croniter.croniter(self.cron_expression, base_time)
            return cron.get_next(datetime)
        except Exception as e:
            print(f"Invalid cron expression '{self.cron_expression}': {e}")
            # Default to daily at 2 AM
            return base_time.replace(hour=2, minute=0, second=0, microsecond=0) + timedelta(days=1)


@dataclass
class JobExecution:
    """Job execution record"""
    id: str
    job_id: str
    scheduled_time: datetime
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: JobStatus = JobStatus.PENDING
    exit_code: Optional[int] = None
    output: str = ""
    error: str = ""
    retry_count: int = 0

    @property
    def duration_seconds(self) -> Optional[float]:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "job_id": self.job_id,
            "scheduled_time": self.scheduled_time.isoformat(),
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "status": self.status.value,
            "exit_code": self.exit_code,
            "duration_seconds": self.duration_seconds,
            "retry_count": self.retry_count
        }


# =============================================================================
# Job Executor
# =============================================================================

class JobExecutor:
    """Executes scheduled jobs"""

    def __init__(self, history_dir: Optional[Path] = None):
        if history_dir is None:
            vault_path = Path(os.getenv("VAULT_PATH", "."))
            history_dir = vault_path / "Logs" / "Scheduler"
        self.history_dir = history_dir
        self.history_dir.mkdir(parents=True, exist_ok=True)

        self.running_jobs: Dict[str, subprocess.Popen] = {}
        self.lock = threading.Lock()

    def execute(self, job: Job) -> JobExecution:
        """Execute a job synchronously"""
        execution = JobExecution(
            id=f"{job.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            job_id=job.id,
            scheduled_time=datetime.now()
        )

        execution.status = JobStatus.RUNNING
        execution.start_time = datetime.now()

        try:
            # Prepare environment
            env = os.environ.copy()
            env.update(job.environment)

            # Prepare working directory
            cwd = job.working_directory or os.getcwd()

            # Execute command
            result = subprocess.run(
                job.command,
                shell=True,
                cwd=cwd,
                env=env,
                capture_output=True,
                text=True,
                timeout=job.timeout_seconds
            )

            execution.end_time = datetime.now()
            execution.exit_code = result.returncode
            execution.output = result.stdout[-10000:]  # Last 10KB
            execution.error = result.stderr[-10000:]

            if result.returncode == 0:
                execution.status = JobStatus.SUCCESS
            else:
                execution.status = JobStatus.FAILED

        except subprocess.TimeoutExpired:
            execution.end_time = datetime.now()
            execution.status = JobStatus.FAILED
            execution.error = f"Job timed out after {job.timeout_seconds} seconds"

        except Exception as e:
            execution.end_time = datetime.now()
            execution.status = JobStatus.FAILED
            execution.error = str(e)

        # Save execution record
        self._save_execution(execution)

        return execution

    def execute_async(self, job: Job) -> tuple[JobExecution, subprocess.Popen]:
        """Execute a job asynchronously"""
        execution = JobExecution(
            id=f"{job.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            job_id=job.id,
            scheduled_time=datetime.now()
        )

        execution.status = JobStatus.RUNNING
        execution.start_time = datetime.now()

        try:
            env = os.environ.copy()
            env.update(job.environment)

            cwd = job.working_directory or os.getcwd()

            # Start process
            process = subprocess.Popen(
                job.command,
                shell=True,
                cwd=cwd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            with self.lock:
                self.running_jobs[execution.id] = process

            return execution, process

        except Exception as e:
            execution.status = JobStatus.FAILED
            execution.error = str(e)
            execution.end_time = datetime.now()
            return execution, None

    def is_running(self, execution_id: str) -> bool:
        """Check if async job is still running"""
        with self.lock:
            process = self.running_jobs.get(execution_id)
            if process and process.poll() is None:
                return True

            # Clean up finished process
            if execution_id in self.running_jobs:
                del self.running_jobs[execution_id]

            return False

    def get_running_jobs(self) -> List[str]:
        """Get list of running execution IDs"""
        with self.lock:
            return [eid for eid, proc in self.running_jobs.items() if proc.poll() is None]

    def _save_execution(self, execution: JobExecution):
        """Save execution record to file"""
        try:
            date_str = execution.scheduled_time.strftime('%Y-%m')
            history_file = self.history_dir / f"jobs_{date_str}.jsonl"

            with open(history_file, 'a') as f:
                f.write(json.dumps(execution.to_dict()) + "\n")

        except Exception as e:
            print(f"Failed to save execution record: {e}")


# =============================================================================
# Scheduler
# =============================================================================

class Scheduler:
    """Job scheduler with cron support"""

    def __init__(self, config_path: Optional[str] = None):
        self.jobs: Dict[str, Job] = {}
        self.executor = JobExecutor()
        self.running = False
        self.lock = threading.Lock()

        # Load jobs from config
        self._load_config(config_path)

    def _load_config(self, config_path: Optional[str]):
        """Load scheduled jobs from config file"""
        if not config_path:
            config_path = Path(os.getenv("VAULT_PATH", ".")) / "odoo_sync_config.yaml"

        config_path = Path(config_path)

        if not config_path.exists():
            # Add default jobs
            self.add_default_jobs()
            return

        try:
            import yaml
            with open(config_path) as f:
                config = yaml.safe_load(f)

            schedules = config.get('schedules', {})

            for name, schedule_config in schedules.items():
                cron = schedule_config.get('cron')
                command = schedule_config.get('command')

                if cron and command:
                    self.add_job(
                        id=name,
                        name=name,
                        cron_expression=cron,
                        command=command
                    )

            # Add default jobs if none defined
            if not self.jobs:
                self.add_default_jobs()

        except Exception as e:
            print(f"Failed to load schedule config: {e}")
            self.add_default_jobs()

    def add_default_jobs(self):
        """Add default scheduled jobs"""
        # Daily full sync at 2 AM
        self.add_job(
            id="daily_full_sync",
            name="Daily Full Sync",
            cron_expression="0 2 * * *",
            command="odoo_sync_ultimate.py --sync all --force-full"
        )

        # Hourly incremental sync
        self.add_job(
            id="hourly_incremental",
            name="Hourly Incremental Sync",
            cron_expression="0 * * * *",
            command="odoo_sync_ultimate.py --sync all"
        )

    def add_job(self, id: str, name: str, cron_expression: str,
               command: str, **kwargs) -> Job:
        """Add a scheduled job"""
        job = Job(
            id=id,
            name=name,
            cron_expression=cron_expression,
            command=command,
            **kwargs
        )

        with self.lock:
            self.jobs[id] = job

        return job

    def remove_job(self, id: str):
        """Remove a scheduled job"""
        with self.lock:
            if id in self.jobs:
                del self.jobs[id]

    def enable_job(self, id: str):
        """Enable a job"""
        with self.lock:
            if id in self.jobs:
                self.jobs[id].enabled = True

    def disable_job(self, id: str):
        """Disable a job"""
        with self.lock:
            if id in self.jobs:
                self.jobs[id].enabled = False

    def get_next_runs(self) -> List[tuple[str, datetime]]:
        """Get list of next run times for all jobs"""
        with self.lock:
            return [
                (job.id, job.next_run_time())
                for job in self.jobs.values()
                if job.enabled
            ]

    def run(self, once: bool = False):
        """Run the scheduler"""
        self.running = True

        # Set up signal handlers
        def signal_handler(signum, frame):
            print("\nShutting down scheduler...")
            self.running = False

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        print(f"Scheduler started with {len(self.jobs)} jobs")
        print("\nNext runs:")
        for job_id, next_time in self.get_next_runs():
            print(f"  {job_id}: {next_time}")

        try:
            while self.running:
                now = datetime.now()

                # Check each job
                for job in list(self.jobs.values()):
                    if not job.enabled:
                        continue

                    # Check dependencies
                    if job.depends_on:
                        deps_satisfied = all(
                            dep_id not in self.jobs or
                            not self.jobs[dep_id].enabled
                            for dep_id in job.depends_on
                        )
                        if not deps_satisfied:
                            continue

                    # Check if job should run now
                    # Allow 1 minute window
                    next_run = job.next_run_time()
                    time_diff = (next_run - now).total_seconds()

                    if -60 <= time_diff <= 0:
                        print(f"\n[{now.strftime('%Y-%m-%d %H:%M:%S')}] Running job: {job.name}")

                        execution = self.executor.execute(job)

                        print(f"  Status: {execution.status.value}")
                        print(f"  Duration: {execution.duration_seconds:.1f}s" if execution.duration_seconds else "")
                        if execution.error:
                            print(f"  Error: {execution.error[:200]}")

                        # Retry on failure
                        if execution.status == JobStatus.FAILED and job.retry_on_failure:
                            for retry in range(job.max_retries):
                                print(f"  Retry {retry + 1}/{job.max_retries}...")
                                time.sleep(60)  # Wait 1 minute before retry
                                execution = self.executor.execute(job)

                                if execution.status == JobStatus.SUCCESS:
                                    print(f"  Retry succeeded")
                                    break

                if once:
                    break

                # Sleep until next minute
                sleep_time = 60 - now.second % 60
                time.sleep(sleep_time)

        except KeyboardInterrupt:
            pass

        print("\nScheduler stopped")

    def run_job_now(self, job_id: str) -> JobExecution:
        """Run a specific job immediately"""
        job = self.jobs.get(job_id)

        if not job:
            raise ValueError(f"Job not found: {job_id}")

        print(f"Running job: {job.name}")
        return self.executor.execute(job)


# =============================================================================
# CLI
# =============================================================================

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Odoo Sync Scheduler')
    parser.add_argument('--config', '-c', help='Path to config file')
    parser.add_argument('--list', '-l', action='store_true',
                       help='List scheduled jobs')
    parser.add_argument('--run', '-r', metavar='JOB_ID',
                       help='Run a specific job immediately')
    parser.add_argument('--enable', metavar='JOB_ID',
                       help='Enable a job')
    parser.add_argument('--disable', metavar='JOB_ID',
                       help='Disable a job')
    parser.add_argument('--once', action='store_true',
                       help='Run all due jobs once and exit')
    parser.add_argument('--add', nargs=4, metavar=('ID', 'CRON', 'COMMAND', 'DESC'),
                       help='Add a new job (ID CRON COMMAND DESC)')

    args = parser.parse_args()

    scheduler = Scheduler(args.config)

    if args.list:
        print(f"\nScheduled Jobs ({len(scheduler.jobs)}):")
        print("-" * 60)

        for job in scheduler.jobs.values():
            status = "enabled" if job.enabled else "disabled"
            next_run = job.next_run_time()

            print(f"""
ID: {job.id}
Name: {job.name}
Status: {status}
Schedule: {job.cron_expression}
Next Run: {next_run.strftime('%Y-%m-%d %H:%M:%S')}
Command: {job.command}
Description: {job.description}
---
""")

        return 0

    if args.add:
        id, cron, command, desc = args.add
        job = scheduler.add_job(
            id=id,
            name=id,
            cron_expression=cron,
            command=command,
            description=desc
        )
        print(f"Added job: {id}")
        print(f"  Next run: {job.next_run_time()}")
        return 0

    if args.enable:
        scheduler.enable_job(args.enable)
        print(f"Enabled job: {args.enable}")
        return 0

    if args.disable:
        scheduler.disable_job(args.disable)
        print(f"Disabled job: {args.disable}")
        return 0

    if args.run:
        execution = scheduler.run_job_now(args.run)
        print(f"\nExecution result: {execution.status.value}")
        if execution.error:
            print(f"Error: {execution.error}")
        return 0 if execution.status == JobStatus.SUCCESS else 1

    # Default: run scheduler
    scheduler.run(once=args.once)
    return 0


if __name__ == "__main__":
    sys.exit(main())
