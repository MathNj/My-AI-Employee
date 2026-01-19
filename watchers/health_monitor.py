#!/usr/bin/env python3
"""
Health Monitor - Watcher health checking script for AI Employee Orchestrator

Monitors watcher processes, checks PID existence, log freshness, and CPU usage.
Logs health status to /Logs/watcher_health.log with timestamp and watcher_name.

Based on Silver Tier Phase 2 tasks T020-T024.
"""

import subprocess
import psutil
import logging
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Configure logging
log_dir = Path("/Logs")
log_dir.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "watcher_health.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("HealthMonitor")


class WatcherHealth:
    """Represents health state of a single watcher"""

    def __init__(self, name: str, pid: int):
        self.name = name
        self.pid = pid
        self.alive = False
        self.log_fresh = False
        self.cpu_usage = 0.0
        self.last_check = None
        self.error_count = 0

    def to_dict(self) -> Dict:
        """Convert watcher health to dictionary"""
        return {
            'watcher_name': self.name,
            'pid': self.pid if self.pid else None,
            'alive': self.alive,
            'log_fresh': self.log_fresh,
            'cpu_usage': self.cpu_usage,
            'last_check': self.last_check.isoformat() if self.last_check else None,
            'error_count': self.error_count
        }


class HealthMonitor:
    """
    Health monitoring system for all watcher processes

    Performs PID checks, log freshness checks, and CPU usage monitoring.
    Logs health status to /Logs/watcher_health.log with timestamp and watcher_name.
    """

    def __init__(self, config_path: str = None):
        self.config_path = config_path or "watchers/orchestrator_config.json"
        self.log_dir = Path("/Logs")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.watchers = {}
        self.last_check = None

    def check_all_watchers(self) -> Dict[str, WatcherHealth]:
        """
        Check health of all configured watchers

        Returns:
            Dictionary mapping watcher names to their health status
        """
        try:
            # Load orchestrator config to get list of enabled watchers
            config_path = Path(self.config_path)
            if not config_path.exists():
                logger.error(f"Config file not found: {config_path}")
                return {}

            with open(config_path, 'r') as f:
                config = json.load(f)

            self.last_check = datetime.now()

            # Check each enabled watcher
            for watcher_name, watcher_config in config.get('watchers', {}).items():
                if watcher_config.get('enabled', False):
                    health = self._check_watcher_health(watcher_name, watcher_config)
                    self.watchers[watcher_name] = health

            # Log overall health status
            self._log_health_status()

            return self.watchers

        except Exception as e:
            logger.error(f"[ERROR] check_all_watchers() failed: {e}")
            return {}

    def _check_watcher_health(self, name: str, config: dict) -> WatcherHealth:
        """
        Check health of a single watcher

        Args:
            name: Watcher name
            config: Watcher configuration

        Returns:
            WatcherHealth object with health status
        """
        health = WatcherHealth(name, None)

        # T021: Check PID existence
        pid = self._check_pid_exists(name)
        health.pid = pid

        if pid:
            health.alive = True

            # T022: Check log freshness
            health.log_fresh = self._check_log_freshness(name, config)

            # T023: Check CPU usage
            health.cpu_usage = self._check_cpu_usage(pid)

        health.last_check = datetime.now()

        return health

    def _check_pid_exists(self, watcher_name: str) -> Optional[int]:
        """
        Check if watcher process PID exists (T021)

        Args:
            watcher_name: Name of the watcher (e.g., "gmail_watcher")

        Returns:
            Process ID if found, None if not found
        """
        try:
            # Find process by name
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if watcher_name in proc.info.get('name', '') or \
                   watcher_name in ' '.join(proc.info.get('cmdline', [])):
                    logger.debug(f"[PID] Found {watcher_name} with PID: {proc.pid}")
                    return proc.pid

            logger.warning(f"[HEALTH] {watcher_name} process not found")
            return None

        except Exception as e:
            logger.error(f"[ERROR] PID check failed for {watcher_name}: {e}")
            return None

    def _check_log_freshness(self, watcher_name: str, config: dict) -> bool:
        """
        Check if watcher log has been modified in last 5 minutes (T022)

        Args:
            watcher_name: Name of the watcher
            config: Watcher configuration

        Returns:
            True if log is fresh, False otherwise
        """
        try:
            # Determine log file path based on watcher name
            log_file = self._get_watcher_log_path(watcher_name)

            if not log_file or not log_file.exists():
                logger.warning(f"[HEALTH] No log file found for {watcher_name}")
                return False

            # Check file modification time
            mtime = log_file.stat().st_mtime
            freshness_threshold = 5 * 60  # 5 minutes in seconds

            is_fresh = (datetime.now().timestamp() - mtime) < freshness_threshold

            if not is_fresh:
                logger.warning(f"[HEALTH] {watcher_name} log is stale (last modified: {datetime.fromtimestamp(mtime)})")

            return is_fresh

        except Exception as e:
            logger.error(f"[ERROR] Log freshness check failed for {watcher_name}: {e}")
            return False

    def _check_cpu_usage(self, pid: int) -> float:
        """
        Check CPU usage of process (T023)

        Args:
            pid: Process ID

        Returns:
            CPU usage as percentage (0-100)
        """
        try:
            proc = psutil.Process(pid)
            cpu_percent = proc.cpu_percent(interval=1)

            # Alert if CPU > 50%
            if cpu_percent > 50:
                logger.warning(f"[HEALTH] {proc.name()} CPU usage: {cpu_percent}% (HIGH)")

            return cpu_percent

        except psutil.NoSuchProcess:
            logger.error(f"[ERROR] Process {pid} no longer exists")
            return 0.0
        except Exception as e:
            logger.error(f"[ERROR] CPU check failed for PID {pid}: {e}")
            return 0.0

    def _get_watcher_log_path(self, watcher_name: str) -> Optional[Path]:
        """
        Determine log file path for a watcher

        Args:
            watcher_name: Name of the watcher

        Returns:
            Path to watcher log file or None
        """
        try:
            # Standard log location
            log_file = Path(f"watchers/{watcher_name}_watcher_*.log")
            log_files = list(Path("watchers").glob(log_file.replace("*", f"_{datetime.now().strftime('%Y-%m-%d')}")))

            if log_files:
                return sorted(log_files)[-1]  # Most recent log file
            else:
                return None

        except Exception as e:
            logger.error(f"[ERROR] Could not determine log path for {watcher_name}: {e}")
            return None

    def _log_health_status(self):
        """
        Log health status to /Logs/watcher_health.log with timestamp (T024)
        """
        try:
            health_status = {
                'timestamp': datetime.now().isoformat(),
                'watchers': {name: health.to_dict() for name, health in self.watchers.items()},
                'summary': {
                    'total_watchers': len(self.watchers),
                    'alive_watchers': sum(1 for h in self.watchers.values() if h.alive),
                    'fresh_logs': sum(1 for h in self.watchers.values() if h.log_fresh),
                    'high_cpu': sum(1 for h in self.watchers() if h.cpu_usage > 50),
                    'errors': sum(1 for h in self.watchers() if h.error_count > 0)
                }
            }

            # Log to health log
            with open(self.log_dir / "watcher_health.log", 'a') as f:
                f.write(f"\n{json.dumps(health_status, indent=2)}\n")

            logger.info(f"[HEALTH] Health status logged: {health_status['summary']}")

        except Exception as e:
            logger.error(f"[ERROR] Failed to log health status: {e}")


def main():
    """
    Main entry point for health monitoring

    Usage: python watchers/health_monitor.py
    """
    import sys

    # Optionally accept config path as command line argument
    config_path = sys.argv[1] if len(sys.argv) > 1 else None

    health_monitor = HealthMonitor(config_path)
    health_data = health_monitor.check_all_watchers()

    # Print health status summary
    print("\n=== Watcher Health Status ===")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total Watchers: {health_data.get('summary', {}).get('total_watchers', 0)}")
    print(f"Alive: {health_data.get('summary', {}).get('alive_watchers', 0)}")
    print(f"Fresh Logs: {health_data.get('summary', {}).get('fresh_logs', 0)}")
    print(f"High CPU (>50%): {health_data.get('summary', {}).get('high_cpu', 0)}")
    print(f"Errors: {health_data.get('summary', {}).get('errors', 0)}")
    print("=" * 50)

    # Show individual watcher status
    for name, health in health_data.items():
        status = "✓ ALIVE" if health.alive else "✗ STOPPED"
        log_status = "✓ FRESH" if health.log_fresh else "✗ STALE"
        cpu_status = f"{health.cpu_usage}%"
        error_status = f"✓ OK" if health.error_count == 0 else f"✗ {health.error_count} errors"
        print(f"{status} {log_status} {cpu_status:6} {error_status:12} {name:20}")

    # Exit with appropriate code
    alive_count = health_data.get('summary', {}).get('alive_watchers', 0)
    sys.exit(0 if alive_count > 0 else 1)


if __name__ == "__main__":
    main()
