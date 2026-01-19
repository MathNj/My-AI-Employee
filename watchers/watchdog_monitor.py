#!/usr/bin/env python3
"""
Watchdog - Health Monitor for AI Employee Orchestrator
Ensures the orchestrator stays running and restarts it if it crashes.

Based on Requirements1.md Section 7.4: Watchdog Process
"""

import time
import logging
import subprocess
import sys
from pathlib import Path
from datetime import datetime
import psutil

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
        logging.FileHandler('watchdog.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('Watchdog')


class Watchdog:
    """
    Monitors the orchestrator process and restarts it if it crashes.
    This is the watchdog for the watchdog - ensures the AI Employee stays alive.
    """

    def __init__(self, check_interval: int = 60):
        self.check_interval = check_interval
        self.orchestrator_path = Path(__file__).parent / 'orchestrator.py'
        self.restart_count = 0
        self.last_restart = None

        logger.info("=" * 70)
        logger.info("AI Employee Watchdog Started")
        logger.info("=" * 70)
        logger.info(f"Monitoring: {self.orchestrator_path}")
        logger.info(f"Check interval: {self.check_interval} seconds")
        logger.info("=" * 70)

    def find_orchestrator_process(self) -> bool:
        """Check if orchestrator is running"""
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] in ['python.exe', 'python']:
                    cmdline = proc.info['cmdline']
                    if cmdline and 'orchestrator.py' in ' '.join(cmdline):
                        return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False

    def start_orchestrator(self) -> bool:
        """Start the orchestrator process"""
        try:
            logger.info("Starting orchestrator...")

            subprocess.Popen(
                ['python', str(self.orchestrator_path)],
                cwd=self.orchestrator_path.parent,
                creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
            )

            self.restart_count += 1
            self.last_restart = datetime.now()

            logger.info(f"[OK] Orchestrator started (Restart count: {self.restart_count})")
            return True

        except Exception as e:
            logger.error(f"[ERROR] Failed to start orchestrator: {e}")
            return False

    def check_and_restart(self):
        """Check if orchestrator is running, restart if not"""
        if not self.find_orchestrator_process():
            logger.warning("Orchestrator not running!")

            if self.last_restart:
                time_since_restart = (datetime.now() - self.last_restart).total_seconds()
                if time_since_restart < 30:
                    logger.error("Orchestrator crashed within 30 seconds of restart - possible configuration issue")
                    logger.error("Waiting 60 seconds before retry...")
                    time.sleep(60)

            self.start_orchestrator()
        else:
            logger.debug("Orchestrator is running normally")

    def run(self):
        """Main watchdog loop"""
        logger.info("Watchdog monitoring started")

        # Ensure orchestrator is running at startup
        if not self.find_orchestrator_process():
            logger.info("Orchestrator not detected at startup, starting it...")
            self.start_orchestrator()
            time.sleep(5)  # Give it time to start

        try:
            while True:
                self.check_and_restart()
                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            logger.info("\nWatchdog stopped by user")

        except Exception as e:
            logger.error(f"Fatal error in watchdog: {e}", exc_info=True)


def main():
    """Main entry point"""
    watchdog = Watchdog(check_interval=60)

    try:
        watchdog.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
