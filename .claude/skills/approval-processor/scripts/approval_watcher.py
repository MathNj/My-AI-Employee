#!/usr/bin/env python3
"""
Approval Watcher - Continuous Monitoring Script

Continuously monitors the /Approved folder for new approval files and processes them immediately.

Usage:
    python approval_watcher.py                  # Start watcher (default 30s interval)
    python approval_watcher.py --interval 60    # Custom check interval (seconds)
    python approval_watcher.py --verbose        # Verbose output

Background usage:
    # Windows
    start pythonw approval_watcher.py

    # Linux/Mac
    nohup python approval_watcher.py &
"""

import os
import sys
import time
import signal
from pathlib import Path
from datetime import datetime
import argparse
import subprocess

# Add process_approvals module to path
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

# Import from process_approvals
try:
    from process_approvals import (
        APPROVED, PENDING_APPROVAL, VAULT_PATH,
        process_approved, check_expirations
    )
except ImportError:
    print("Error: Could not import process_approvals module")
    sys.exit(1)

# Watcher state
running = True
last_files = set()


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully."""
    global running
    print("\n\n👋 Stopping approval watcher...")
    running = False
    sys.exit(0)


def get_current_files():
    """Get set of current files in Approved folder."""
    return set(f.name for f in APPROVED.glob('*.md'))


def watch_for_approvals(check_interval=30, verbose=False):
    """
    Continuously watch for new approvals and process them.

    Args:
        check_interval: Seconds between checks
        verbose: Print verbose output
    """
    global last_files
    global running

    print("👁️  Approval Watcher Started")
    print(f"   Monitoring: {APPROVED}")
    print(f"   Check interval: {check_interval} seconds")
    print(f"   Press Ctrl+C to stop\n")

    # Initialize with current files
    last_files = get_current_files()

    check_count = 0

    while running:
        try:
            check_count += 1
            timestamp = datetime.now().strftime("%H:%M:%S")

            # Get current files
            current_files = get_current_files()

            # Check for new files
            new_files = current_files - last_files

            if new_files:
                print(f"\n[{timestamp}] 🔔 Found {len(new_files)} new approval(s)")

                for filename in new_files:
                    print(f"[{timestamp}] Processing {filename}...")

                    # Process the single file by calling process_approved
                    # This will handle execution, logging, and moving to /Done
                    successful, failed = process_approved(dry_run=False, verbose=verbose)

                    if successful > 0:
                        print(f"[{timestamp}] ✅ {filename} executed successfully")
                    elif failed > 0:
                        print(f"[{timestamp}] ❌ {filename} execution failed")

                # Update last_files
                last_files = get_current_files()

            else:
                if verbose:
                    print(f"[{timestamp}] Checking for approved actions... (Check #{check_count})")
                    print(f"[{timestamp}] No new approvals")

            # Check for expirations every 10 checks (reduce overhead)
            if check_count % 10 == 0:
                expired = check_expirations(dry_run=False, verbose=False)
                if expired > 0:
                    print(f"[{timestamp}] ⚠️  Moved {expired} expired approval(s)")

            # Sleep until next check
            time.sleep(check_interval)

        except KeyboardInterrupt:
            break

        except Exception as e:
            print(f"\n[{timestamp}] ⚠️  Error: {e}")
            if verbose:
                import traceback
                traceback.print_exc()

            # Continue watching despite errors
            time.sleep(check_interval)

    print("\n✅ Approval watcher stopped")


def main():
    """Main entry point."""
    # Register signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)

    parser = argparse.ArgumentParser(description='Continuously monitor approval queue')
    parser.add_argument(
        '--interval',
        type=int,
        default=30,
        help='Check interval in seconds (default: 30)'
    )
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Verbose output'
    )

    args = parser.parse_args()

    # Validate interval
    if args.interval < 5:
        print("Warning: Minimum interval is 5 seconds")
        args.interval = 5

    # Start watching
    try:
        watch_for_approvals(
            check_interval=args.interval,
            verbose=args.verbose
        )
    except KeyboardInterrupt:
        print("\n\n👋 Stopping approval watcher...")
        sys.exit(0)


if __name__ == '__main__':
    main()
