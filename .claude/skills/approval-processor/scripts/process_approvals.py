#!/usr/bin/env python3
"""
Approval Processor - Main Script

Processes approval requests from the approval workflow folders.
Scans /Approved, /Rejected, and /Pending_Approval folders and takes appropriate actions.

Usage:
    python process_approvals.py                    # Process all pending
    python process_approvals.py --verbose          # Verbose output
    python process_approvals.py --dry-run          # Preview only (no execution)
    python process_approvals.py --folder /Approved # Process specific folder
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
import argparse
import time

# Vault base path
VAULT_PATH = Path(__file__).parent.parent.parent.parent.absolute()

# Import audit logger
sys.path.insert(0, str(VAULT_PATH / "Logs"))
from audit_logger import get_audit_logger

# Approval folders
PENDING_APPROVAL = VAULT_PATH / "Pending_Approval"
APPROVED = VAULT_PATH / "Approved"
REJECTED = VAULT_PATH / "Rejected"
DONE = VAULT_PATH / "Done"
EXPIRED = VAULT_PATH / "Expired"
FAILED = VAULT_PATH / "Failed"

# Ensure folders exist
for folder in [PENDING_APPROVAL, APPROVED, REJECTED, DONE, EXPIRED, FAILED]:
    folder.mkdir(exist_ok=True)

# Logs folder
LOGS = VAULT_PATH / "Logs"
LOGS.mkdir(exist_ok=True)

# Configuration
MAX_RETRIES = 3
RETRY_DELAYS = [0, 30, 60]  # seconds
EXPIRATION_HOURS = 24

# Executor mapping
EXECUTORS = {
    'email': {
        'script': VAULT_PATH / '.claude' / 'skills' / 'email-sender' / 'scripts' / 'send_email.py',
        'arg': '--execute-approved'
    },
    'linkedin_post': {
        'script': VAULT_PATH / '.claude' / 'skills' / 'linkedin-poster' / 'scripts' / 'linkedin_post.py',
        'arg': '--execute-approved'
    },
    'x_post': {
        'script': VAULT_PATH / '.claude' / 'skills' / 'x-poster' / 'scripts' / 'x_post.py',
        'arg': '--execute-approved'
    },
    'instagram_post': {
        'script': VAULT_PATH / '.claude' / 'skills' / 'instagram-poster' / 'scripts' / 'instagram_post.py',
        'arg': '--execute-approved'
    },
    'facebook_post': {
        'script': VAULT_PATH / '.claude' / 'skills' / 'facebook-poster' / 'scripts' / 'facebook_post.py',
        'arg': '--execute-approved'
    }
}


def log_activity(action, details, skill="approval-processor"):
    """Log activity to activity log file."""
    log_file = LOGS / f"approval_activity_{datetime.now().strftime('%Y-%m-%d')}.json"

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "details": details,
        "skill": skill
    }

    # Append to log file
    try:
        logs = []
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)

        logs.append(log_entry)

        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Warning: Failed to log activity: {e}")


def parse_frontmatter(file_path):
    """Parse frontmatter from markdown file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if not content.startswith('---'):
        return None

    # Extract frontmatter
    parts = content.split('---', 2)
    if len(parts) < 3:
        return None

    frontmatter_text = parts[1].strip()

    # Simple YAML parsing (handles basic key: value pairs)
    metadata = {}
    current_key = None
    multiline_value = []
    in_multiline = False

    for line in frontmatter_text.split('\n'):
        line_stripped = line.strip()

        # Skip empty lines
        if not line_stripped:
            continue

        # Handle multiline value end
        if in_multiline:
            if line_stripped and not line.startswith(' ') and not line.startswith('\t') and ':' in line:
                # New key found, save previous multiline value
                metadata[current_key] = '\n'.join(multiline_value).strip()
                multiline_value = []
                in_multiline = False
            else:
                # Continue multiline value
                multiline_value.append(line_stripped)
                continue

        # Handle key: value pairs
        if ':' in line_stripped and not in_multiline:
            key, value = line_stripped.split(':', 1)
            key = key.strip()
            value = value.strip()

            # Handle multiline indicator (|)
            if value == '|':
                current_key = key
                in_multiline = True
                multiline_value = []
            # Handle list items
            elif value.startswith('[') and value.endswith(']'):
                # Parse simple list: ["item1", "item2"]
                items = value[1:-1].split(',')
                metadata[key] = [item.strip().strip('"').strip("'") for item in items if item.strip()]
            else:
                metadata[key] = value.strip('"').strip("'")

    # Save final multiline value if exists
    if in_multiline and multiline_value:
        metadata[current_key] = '\n'.join(multiline_value).strip()

    return metadata


def is_expired(file_path, metadata):
    """Check if approval request has expired."""
    # Check expires field in metadata
    if 'expires' in metadata:
        try:
            expires_dt = datetime.fromisoformat(metadata['expires'].replace('Z', '+00:00'))
            if datetime.now() > expires_dt:
                return True
        except:
            pass

    # Check file age as fallback
    file_age = datetime.now() - datetime.fromtimestamp(file_path.stat().st_mtime)
    return file_age > timedelta(hours=EXPIRATION_HOURS)


def route_action(action_file, metadata, dry_run=False, verbose=False):
    """Route action to correct executor based on type."""
    action_type = metadata.get('type')

    if action_type not in EXECUTORS:
        raise ValueError(f"Unknown action type: {action_type}")

    executor = EXECUTORS[action_type]
    script_path = executor['script']
    script_arg = executor['arg']

    if not script_path.exists():
        raise FileNotFoundError(f"Executor script not found: {script_path}")

    if verbose:
        print(f"  Executor: {action_type}")
        print(f"  Script: {script_path}")
        print(f"  Argument: {script_arg}")

    if dry_run:
        print(f"  [DRY RUN] Would execute: python {script_path} {script_arg} {action_file}")
        return True

    # Get audit logger
    audit_logger = get_audit_logger(VAULT_PATH)

    # Prepare audit log parameters
    target = metadata.get('target', metadata.get('to', 'unknown'))
    if action_type == 'linkedin_post':
        target = 'LinkedIn'
    elif action_type == 'x_post':
        target = 'X/Twitter'
    elif action_type == 'instagram_post':
        target = 'Instagram'
    elif action_type == 'facebook_post':
        target = 'Facebook'

    # Execute with retries
    for attempt in range(MAX_RETRIES):
        try:
            if attempt > 0:
                delay = RETRY_DELAYS[attempt]
                if verbose:
                    print(f"  Retry attempt {attempt + 1} after {delay}s delay...")
                time.sleep(delay)

            # Execute the action
            result = subprocess.run(
                [sys.executable, str(script_path), script_arg, str(action_file)],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            if result.returncode == 0:
                # Log successful execution to audit trail
                audit_logger.log_approval_execution(
                    approval_file=action_file,
                    action_type=action_type,
                    actor="approval_processor",
                    target=target,
                    parameters={k: v for k, v in metadata.items() if k not in ['type', 'status', 'created']},
                    result="success"
                )
                return True
            else:
                error_msg = result.stderr or result.stdout
                if verbose:
                    print(f"  Attempt {attempt + 1} failed: {error_msg}")

                if attempt == MAX_RETRIES - 1:
                    # Log failed execution to audit trail
                    audit_logger.log_approval_execution(
                        approval_file=action_file,
                        action_type=action_type,
                        actor="approval_processor",
                        target=target,
                        parameters={k: v for k, v in metadata.items() if k not in ['type', 'status', 'created']},
                        result="failure",
                        error_message=error_msg
                    )
                    raise Exception(f"Execution failed after {MAX_RETRIES} attempts: {error_msg}")

        except subprocess.TimeoutExpired:
            if verbose:
                print(f"  Attempt {attempt + 1} timed out")
            if attempt == MAX_RETRIES - 1:
                raise Exception("Execution timed out")

        except Exception as e:
            if verbose:
                print(f"  Attempt {attempt + 1} error: {e}")
            if attempt == MAX_RETRIES - 1:
                raise

    return False


def process_approved(dry_run=False, verbose=False):
    """Process approved action requests."""
    approved_files = list(APPROVED.glob('*.md'))

    if not approved_files:
        if verbose:
            print("No approved actions found")
        return 0, 0

    print(f"\nFound {len(approved_files)} approved action(s)")

    successful = 0
    failed = 0

    for action_file in approved_files:
        print(f"\nProcessing: {action_file.name}")

        try:
            # Parse metadata
            metadata = parse_frontmatter(action_file)
            if not metadata:
                raise ValueError("Invalid frontmatter format")

            action_type = metadata.get('type')
            if verbose:
                print(f"  Type: {action_type}")
                if action_type == 'email':
                    print(f"  To: {metadata.get('to')}")
                    print(f"  Subject: {metadata.get('subject')}")
                elif action_type == 'linkedin_post':
                    print(f"  Message: {metadata.get('message', '')[:50]}...")

            # Check expiration
            if is_expired(action_file, metadata):
                print(f"  ⚠️ Expired - moving to /Expired")
                if not dry_run:
                    shutil.move(str(action_file), str(EXPIRED / action_file.name))
                    log_activity("approval_expired", {
                        "file": action_file.name,
                        "type": action_type
                    })
                continue

            # Route and execute
            success = route_action(action_file, metadata, dry_run=dry_run, verbose=verbose)

            if success:
                print(f"  ✅ Action executed successfully")
                if not dry_run:
                    # Move to Done
                    shutil.move(str(action_file), str(DONE / action_file.name))
                    log_activity("approval_executed", {
                        "file": action_file.name,
                        "type": action_type,
                        "status": "success"
                    })
                successful += 1
            else:
                print(f"  ❌ Action failed")
                if not dry_run:
                    # Move to Failed
                    shutil.move(str(action_file), str(FAILED / action_file.name))
                    log_activity("approval_failed", {
                        "file": action_file.name,
                        "type": action_type,
                        "status": "failed"
                    })
                failed += 1

        except Exception as e:
            print(f"  ❌ Error: {e}")
            if verbose:
                import traceback
                traceback.print_exc()

            if not dry_run:
                # Move to Failed
                shutil.move(str(action_file), str(FAILED / action_file.name))
                log_activity("approval_error", {
                    "file": action_file.name,
                    "error": str(e)
                })
            failed += 1

    return successful, failed


def process_rejections(dry_run=False, verbose=False):
    """Process rejected action requests."""
    rejected_files = list(REJECTED.glob('*.md'))

    if not rejected_files:
        if verbose:
            print("No rejections found")
        return 0

    print(f"\nFound {len(rejected_files)} rejection(s)")

    for action_file in rejected_files:
        print(f"\nProcessing rejection: {action_file.name}")

        try:
            # Parse metadata for rejection reason
            metadata = parse_frontmatter(action_file)
            action_type = metadata.get('type', 'unknown')
            rejection_reason = metadata.get('rejection_reason', 'No reason provided')

            if verbose:
                print(f"  Type: {action_type}")
                print(f"  Reason: {rejection_reason}")

            if not dry_run:
                log_activity("approval_rejected", {
                    "file": action_file.name,
                    "type": action_type,
                    "reason": rejection_reason
                })

            print(f"  ✅ Rejection logged")

        except Exception as e:
            print(f"  ⚠️ Error logging rejection: {e}")

    return len(rejected_files)


def check_expirations(dry_run=False, verbose=False):
    """Check for and handle expired approval requests."""
    pending_files = list(PENDING_APPROVAL.glob('*.md'))

    if not pending_files:
        if verbose:
            print("No pending approvals")
        return 0

    expired_count = 0

    for action_file in pending_files:
        try:
            metadata = parse_frontmatter(action_file)
            if metadata and is_expired(action_file, metadata):
                expired_count += 1
                print(f"\n⚠️ Expired: {action_file.name}")

                if not dry_run:
                    shutil.move(str(action_file), str(EXPIRED / action_file.name))
                    log_activity("approval_expired", {
                        "file": action_file.name,
                        "type": metadata.get('type', 'unknown')
                    })

        except Exception as e:
            if verbose:
                print(f"Error checking expiration for {action_file.name}: {e}")

    if expired_count > 0:
        print(f"\nMoved {expired_count} expired approval(s) to /Expired")

    return expired_count


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Process approval workflow')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--dry-run', action='store_true', help='Preview only (no execution)')
    parser.add_argument('--folder', type=str, help='Process specific folder only')

    args = parser.parse_args()

    print("🔄 Processing approval queue...")
    if args.dry_run:
        print("   [DRY RUN MODE - No actions will be executed]")

    # Check expirations first
    expired = check_expirations(dry_run=args.dry_run, verbose=args.verbose)

    # Process approved actions
    successful, failed = process_approved(dry_run=args.dry_run, verbose=args.verbose)

    # Process rejections
    rejected = process_rejections(dry_run=args.dry_run, verbose=args.verbose)

    # Summary
    print(f"\n📊 Summary:")
    print(f"  Processed: {successful + failed}")
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")
    print(f"  Rejected: {rejected}")
    print(f"  Expired: {expired}")


if __name__ == '__main__':
    main()
