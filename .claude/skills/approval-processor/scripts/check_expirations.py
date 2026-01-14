#!/usr/bin/env python3
"""
Check Expirations - Approval Expiration Handler

Checks for and handles expired approval requests in /Pending_Approval folder.

Usage:
    python check_expirations.py              # Check and display expirations
    python check_expirations.py --move       # Move expired to /Expired
    python check_expirations.py --hours 48   # Custom expiration time
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import json
import argparse

# Vault base path
VAULT_PATH = Path(__file__).parent.parent.parent.parent.absolute()

# Approval folders
PENDING_APPROVAL = VAULT_PATH / "Pending_Approval"
EXPIRED = VAULT_PATH / "Expired"
LOGS = VAULT_PATH / "Logs"

# Ensure folders exist
for folder in [PENDING_APPROVAL, EXPIRED, LOGS]:
    folder.mkdir(exist_ok=True)

# Default expiration time
DEFAULT_EXPIRATION_HOURS = 24


def log_activity(action, details, skill="approval-processor"):
    """Log activity to activity log file."""
    log_file = LOGS / f"approval_activity_{datetime.now().strftime('%Y-%m-%d')}.json"

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "details": details,
        "skill": skill
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
        print(f"Warning: Failed to log activity: {e}")


def parse_frontmatter(file_path):
    """Parse frontmatter from markdown file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if not content.startswith('---'):
            return {}

        parts = content.split('---', 2)
        if len(parts) < 3:
            return {}

        frontmatter_text = parts[1].strip()
        metadata = {}

        for line in frontmatter_text.split('\n'):
            line_stripped = line.strip()
            if ':' in line_stripped:
                key, value = line_stripped.split(':', 1)
                metadata[key.strip()] = value.strip().strip('"').strip("'")

        return metadata
    except Exception:
        return {}


def is_expired(file_path, metadata, expiration_hours):
    """Check if approval request has expired."""
    # Check expires field in metadata first
    if 'expires' in metadata:
        try:
            expires_dt = datetime.fromisoformat(metadata['expires'].replace('Z', '+00:00'))
            return datetime.now() > expires_dt
        except:
            pass

    # Fallback to file age
    file_age = datetime.now() - datetime.fromtimestamp(file_path.stat().st_mtime)
    return file_age > timedelta(hours=expiration_hours)


def get_expiration_info(file_path, metadata, expiration_hours):
    """Get detailed expiration information for a file."""
    info = {
        'name': file_path.name,
        'type': metadata.get('type', 'unknown'),
        'created': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
        'is_expired': False,
        'time_since_creation': None,
        'expiration_method': None
    }

    # Check metadata expires field
    if 'expires' in metadata:
        try:
            expires_dt = datetime.fromisoformat(metadata['expires'].replace('Z', '+00:00'))
            info['expires_at'] = expires_dt.isoformat()
            info['is_expired'] = datetime.now() > expires_dt

            time_diff = expires_dt - datetime.now()
            if time_diff.total_seconds() > 0:
                info['time_until_expiry'] = str(time_diff)
            else:
                info['time_since_expiry'] = str(abs(time_diff))

            info['expiration_method'] = 'metadata'
            return info
        except:
            pass

    # Fallback to file age
    file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
    age = datetime.now() - file_time
    expiry_threshold = timedelta(hours=expiration_hours)

    info['time_since_creation'] = str(age)
    info['is_expired'] = age > expiry_threshold
    info['expiration_method'] = 'file_age'

    if age > expiry_threshold:
        info['time_since_expiry'] = str(age - expiry_threshold)
    else:
        info['time_until_expiry'] = str(expiry_threshold - age)

    return info


def check_expirations(expiration_hours=DEFAULT_EXPIRATION_HOURS, move=False, verbose=False):
    """Check for expired approvals."""
    pending_files = list(PENDING_APPROVAL.glob('*.md'))

    if not pending_files:
        print("No pending approvals to check")
        return 0

    print(f"\n🔍 Checking {len(pending_files)} pending approval(s) for expiration...")
    print(f"   Expiration threshold: {expiration_hours} hours\n")

    expired_files = []
    active_files = []

    for file_path in pending_files:
        metadata = parse_frontmatter(file_path)
        info = get_expiration_info(file_path, metadata, expiration_hours)

        if info['is_expired']:
            expired_files.append((file_path, info))
        else:
            active_files.append((file_path, info))

    # Display results
    if expired_files:
        print(f"⚠️  Found {len(expired_files)} expired approval(s):\n")
        for file_path, info in expired_files:
            print(f"  {info['name']}")
            print(f"    Type: {info['type']}")
            print(f"    Created: {info['created']}")

            if 'time_since_expiry' in info:
                print(f"    Expired: {info['time_since_expiry']} ago")
            elif 'time_since_creation' in info:
                print(f"    Age: {info['time_since_creation']}")

            if verbose:
                print(f"    Expiration method: {info['expiration_method']}")

            print()

        if move:
            print(f"📦 Moving expired files to /Expired...\n")
            moved_count = 0
            for file_path, info in expired_files:
                try:
                    dest_path = EXPIRED / file_path.name
                    shutil.move(str(file_path), str(dest_path))
                    print(f"  ✅ Moved: {file_path.name}")

                    # Log the expiration
                    log_activity("approval_expired", {
                        "file": file_path.name,
                        "type": info['type'],
                        "created": info['created'],
                        "expiration_method": info['expiration_method']
                    })

                    moved_count += 1
                except Exception as e:
                    print(f"  ❌ Failed to move {file_path.name}: {e}")

            print(f"\n✅ Moved {moved_count} expired approval(s) to /Expired")
        else:
            print(f"💡 Run with --move flag to move these files to /Expired")

    else:
        print(f"✅ No expired approvals found")

    # Show active approvals
    if active_files and verbose:
        print(f"\n📋 Active approvals ({len(active_files)}):\n")
        for file_path, info in active_files:
            print(f"  {info['name']}")
            print(f"    Type: {info['type']}")
            if 'time_until_expiry' in info:
                print(f"    Expires in: {info['time_until_expiry']}")
            print()

    return len(expired_files)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Check and handle expired approvals')
    parser.add_argument(
        '--hours',
        type=int,
        default=DEFAULT_EXPIRATION_HOURS,
        help=f'Expiration time in hours (default: {DEFAULT_EXPIRATION_HOURS})'
    )
    parser.add_argument(
        '--move',
        '-m',
        action='store_true',
        help='Move expired files to /Expired folder'
    )
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Show verbose output including active approvals'
    )

    args = parser.parse_args()

    expired_count = check_expirations(
        expiration_hours=args.hours,
        move=args.move,
        verbose=args.verbose
    )

    sys.exit(0 if expired_count == 0 else 1)


if __name__ == '__main__':
    main()
