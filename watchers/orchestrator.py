#!/usr/bin/env python3
"""
Orchestrator - Master Process Manager for AI Employee Watchers
Manages all watcher and poster processes, handles scheduling, and monitors health.

Based on Requirements1.md Section: Orchestration Layer
"""

import subprocess
import time
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import sys

# Configure UTF-8 for Windows
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('orchestrator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('Orchestrator')


class Process:
    """Represents a managed process (watcher or poster)"""

    def __init__(self, name: str, script: str, args: List[str] = None,
                 enabled: bool = True, restart_on_fail: bool = True):
        self.name = name
        self.script = script
        self.args = args or []
        self.enabled = enabled
        self.restart_on_fail = restart_on_fail
        self.process: Optional[subprocess.Popen] = None
        self.start_count = 0
        self.last_start = None
        self.status = 'stopped'

    def start(self) -> bool:
        """Start the process"""
        if not self.enabled:
            logger.info(f"{self.name} is disabled, skipping")
            return False

        if self.is_running():
            logger.warning(f"{self.name} is already running")
            return False

        try:
            cmd = ['python', self.script] + self.args
            logger.info(f"Starting {self.name}: {' '.join(cmd)}")

            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=Path(__file__).parent
            )

            self.start_count += 1
            self.last_start = datetime.now()
            self.status = 'running'

            logger.info(f"[OK] {self.name} started (PID: {self.process.pid})")
            return True

        except Exception as e:
            logger.error(f"[ERROR] Failed to start {self.name}: {e}")
            self.status = 'failed'
            return False

    def stop(self) -> bool:
        """Stop the process"""
        if not self.is_running():
            return True

        try:
            logger.info(f"Stopping {self.name}...")
            self.process.terminate()
            self.process.wait(timeout=10)
            self.status = 'stopped'
            logger.info(f"[OK] {self.name} stopped")
            return True

        except subprocess.TimeoutExpired:
            logger.warning(f"{self.name} did not terminate, killing...")
            self.process.kill()
            self.status = 'killed'
            return True

        except Exception as e:
            logger.error(f"[ERROR] Failed to stop {self.name}: {e}")
            return False

    def is_running(self) -> bool:
        """Check if process is running"""
        if self.process is None:
            return False
        return self.process.poll() is None

    def get_status(self) -> Dict:
        """Get process status information"""
        return {
            'name': self.name,
            'enabled': self.enabled,
            'status': self.status,
            'running': self.is_running(),
            'pid': self.process.pid if self.is_running() else None,
            'start_count': self.start_count,
            'last_start': self.last_start.isoformat() if self.last_start else None
        }


class Orchestrator:
    """
    Master orchestrator for managing all AI Employee processes.
    Handles startup, shutdown, monitoring, and auto-restart.
    """

    def __init__(self, config_path: str = 'orchestrator_config.json'):
        self.config_path = Path(config_path)
        self.processes: Dict[str, Process] = {}
        self.running = False
        self.check_interval = 60  # Check health every 60 seconds

        logger.info("=" * 70)
        logger.info("Personal AI Employee - Orchestrator")
        logger.info("=" * 70)

        self._load_config()
        self._register_processes()

    def _load_config(self):
        """Load orchestrator configuration"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                self.check_interval = config.get('check_interval', 60)
                logger.info(f"Loaded config from {self.config_path}")
        else:
            logger.info("No config found, using defaults")

    def _register_processes(self):
        """Register all watcher and poster processes"""

        # Watchers
        self.processes['calendar'] = Process(
            name='Calendar Watcher',
            script='calendar_watcher.py',
            enabled=True,
            restart_on_fail=True
        )

        self.processes['slack'] = Process(
            name='Slack Watcher',
            script='slack_watcher.py',
            enabled=True,
            restart_on_fail=True
        )

        self.processes['gmail'] = Process(
            name='Gmail Watcher',
            script='gmail_watcher.py',
            enabled=True,
            restart_on_fail=True
        )

        self.processes['whatsapp'] = Process(
            name='WhatsApp Watcher',
            script='whatsapp_watcher.py',
            args=['--visible'],  # WhatsApp needs visible mode
            enabled=True,
            restart_on_fail=True
        )

        self.processes['filesystem'] = Process(
            name='Filesystem Watcher',
            script='filesystem_watcher.py',
            enabled=True,
            restart_on_fail=True
        )

        # AI Auto-Approver
        self.processes['auto_approver'] = Process(
            name='Auto-Approver',
            script='auto_approver_watcher.py',
            enabled=True,
            restart_on_fail=True
        )

        # Ad Monitoring (NEW - E-commerce enhancement)
        self.processes['ad_monitor'] = Process(
            name='Ad Monitor',
            script='../ad_management/2Check_Availability.py',
            enabled=False,  # Disabled by default - user can enable
            restart_on_fail=True
        )

        # Dashboard Server (NEW)
        self.processes['dashboard'] = Process(
            name='Dashboard',
            script='../ad_management/dashboard.py',
            enabled=False,  # Disabled by default
            restart_on_fail=True
        )

        logger.info(f"Registered {len(self.processes)} processes")

    def start_all(self):
        """Start all enabled processes"""
        logger.info("Starting all enabled processes...")

        for name, process in self.processes.items():
            if process.enabled:
                process.start()
                time.sleep(2)  # Stagger starts

        logger.info("All processes started")

    def stop_all(self):
        """Stop all running processes"""
        logger.info("Stopping all processes...")

        for name, process in self.processes.items():
            if process.is_running():
                process.stop()

        logger.info("All processes stopped")

    def restart_process(self, name: str) -> bool:
        """Restart a specific process"""
        if name not in self.processes:
            logger.error(f"Unknown process: {name}")
            return False

        process = self.processes[name]
        logger.info(f"Restarting {process.name}...")

        if process.is_running():
            process.stop()
            time.sleep(1)

        return process.start()

    def health_check(self):
        """Check health of all processes and restart failed ones"""
        logger.info("Running health check...")

        for name, process in self.processes.items():
            if not process.enabled:
                continue

            if not process.is_running():
                logger.warning(f"{process.name} is not running!")

                if process.restart_on_fail:
                    logger.info(f"Auto-restarting {process.name}...")
                    if process.start():
                        logger.info(f"[OK] {process.name} restarted successfully")
                    else:
                        logger.error(f"[ERROR] Failed to restart {process.name}")

        logger.info("Health check complete")

    def get_status(self) -> Dict:
        """Get status of all processes"""
        return {
            'orchestrator': {
                'running': self.running,
                'check_interval': self.check_interval,
                'uptime': datetime.now().isoformat()
            },
            'processes': {name: proc.get_status() for name, proc in self.processes.items()}
        }

    def print_status(self):
        """Print status to console"""
        print("\n" + "=" * 70)
        print("AI Employee Status")
        print("=" * 70)

        for name, process in self.processes.items():
            status = "[RUNNING]" if process.is_running() else "[STOPPED]"
            enabled = "[ENABLED]" if process.enabled else "[DISABLED]"

            print(f"{status} {enabled} {process.name}")
            if process.last_start:
                print(f"         Last started: {process.last_start.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"         Restarts: {process.start_count}")

        print("=" * 70 + "\n")

    def run(self):
        """Main orchestrator loop"""
        self.running = True

        logger.info("=" * 70)
        logger.info("Orchestrator started")
        logger.info(f"Health check interval: {self.check_interval} seconds")
        logger.info("Press Ctrl+C to stop")
        logger.info("=" * 70)

        # Start all processes
        self.start_all()

        try:
            while self.running:
                time.sleep(self.check_interval)
                self.health_check()

        except KeyboardInterrupt:
            logger.info("\nShutdown signal received")

        finally:
            self.stop_all()
            logger.info("Orchestrator stopped")


def main():
    """Main entry point"""
    orchestrator = Orchestrator()

    try:
        orchestrator.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        orchestrator.stop_all()
        sys.exit(1)


if __name__ == "__main__":
    main()
