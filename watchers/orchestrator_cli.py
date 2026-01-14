#!/usr/bin/env python3
"""
Orchestrator CLI - Command-line interface for managing the AI Employee
Provides commands to start, stop, restart, and check status of watchers.
"""

import sys
import json
import argparse
from pathlib import Path
import subprocess
import psutil

def find_orchestrator_process():
    """Find the running orchestrator process"""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] == 'python.exe' or proc.info['name'] == 'python':
                cmdline = proc.info['cmdline']
                if cmdline and 'orchestrator.py' in ' '.join(cmdline):
                    return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return None

def get_status():
    """Get status of all processes"""
    proc = find_orchestrator_process()

    if proc is None:
        print("Orchestrator is not running")
        return

    print("=" * 70)
    print("AI Employee Status")
    print("=" * 70)
    print(f"Orchestrator PID: {proc.pid}")
    print(f"Memory: {proc.memory_info().rss / 1024 / 1024:.1f} MB")
    print()

    # Find all watcher processes
    print("Running Watchers:")
    for p in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if p.info['name'] in ['python.exe', 'python']:
                cmdline = ' '.join(p.info['cmdline'])
                if 'watcher.py' in cmdline:
                    watcher_name = cmdline.split('/')[-1].split('\\')[-1].replace('_watcher.py', '')
                    print(f"  - {watcher_name.capitalize()} Watcher (PID: {p.pid})")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    print("=" * 70)

def start_orchestrator():
    """Start the orchestrator"""
    proc = find_orchestrator_process()

    if proc is not None:
        print("Orchestrator is already running (PID: {proc.pid})")
        return

    print("Starting orchestrator...")
    subprocess.Popen(
        ['python', 'orchestrator.py'],
        creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
    )
    print("[OK] Orchestrator started")

def stop_orchestrator():
    """Stop the orchestrator"""
    proc = find_orchestrator_process()

    if proc is None:
        print("Orchestrator is not running")
        return

    print(f"Stopping orchestrator (PID: {proc.pid})...")
    proc.terminate()
    proc.wait(timeout=10)
    print("[OK] Orchestrator stopped")

def restart_orchestrator():
    """Restart the orchestrator"""
    stop_orchestrator()
    import time
    time.sleep(2)
    start_orchestrator()

def main():
    parser = argparse.ArgumentParser(description='AI Employee Orchestrator CLI')
    parser.add_argument('command', choices=['start', 'stop', 'restart', 'status'],
                        help='Command to execute')

    args = parser.parse_args()

    if args.command == 'start':
        start_orchestrator()
    elif args.command == 'stop':
        stop_orchestrator()
    elif args.command == 'restart':
        restart_orchestrator()
    elif args.command == 'status':
        get_status()

if __name__ == '__main__':
    main()
