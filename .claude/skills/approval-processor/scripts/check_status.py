#!/usr/bin/env python3
"""
Check Status - Approval Queue Status Viewer

Displays current status of the approval queue with pending, approved, rejected, done, and expired items.

Usage:
    python check_status.py                # Current status
    python check_status.py --detailed     # Detailed view with file contents
    python check_status.py --json         # JSON output
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
import json
import argparse

# Vault base path
VAULT_PATH = Path(__file__).parent.parent.parent.parent.absolute()

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

# Expiration threshold
EXPIRATION_HOURS = 24


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


def get_file_age(file_path):
    """Get file age in hours."""
    file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
    age = datetime.now() - file_time
    return age.total_seconds() / 3600  # hours


def is_expiring_soon(file_path, metadata, hours=2):
    """Check if approval will expire soon."""
    # Check expires field in metadata
    if 'expires' in metadata:
        try:
            expires_dt = datetime.fromisoformat(metadata['expires'].replace('Z', '+00:00'))
            time_until_expiry = expires_dt - datetime.now()
            return 0 < time_until_expiry.total_seconds() / 3600 < hours
        except:
            pass

    # Check file age as fallback
    file_age = get_file_age(file_path)
    return EXPIRATION_HOURS - hours < file_age < EXPIRATION_HOURS


def get_folder_status(folder_path):
    """Get status of files in a folder."""
    files = list(folder_path.glob('*.md'))

    status = {
        'count': len(files),
        'files': []
    }

    for file_path in files:
        metadata = parse_frontmatter(file_path)
        age_hours = get_file_age(file_path)

        file_info = {
            'name': file_path.name,
            'type': metadata.get('type', 'unknown'),
            'age_hours': round(age_hours, 1),
            'created': datetime.fromtimestamp(file_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
        }

        # Add type-specific info
        if metadata.get('type') == 'email':
            file_info['to'] = metadata.get('to', 'unknown')
            file_info['subject'] = metadata.get('subject', 'No subject')
        elif metadata.get('type') == 'linkedin_post':
            message = metadata.get('message', '')
            file_info['message_preview'] = message[:50] + '...' if len(message) > 50 else message

        status['files'].append(file_info)

    return status


def display_status(detailed=False):
    """Display approval queue status."""
    print("\n📋 Approval Queue Status\n")

    # Pending Approval
    pending = get_folder_status(PENDING_APPROVAL)
    print(f"Pending Approval: {pending['count']} items")
    if detailed and pending['files']:
        for file_info in pending['files']:
            age_str = f"{file_info['age_hours']:.1f} hours ago" if file_info['age_hours'] < 24 else f"{file_info['age_hours']/24:.1f} days ago"
            print(f"  - {file_info['name']} ({file_info['type']}, Created {age_str})")
            if file_info['type'] == 'email':
                print(f"    To: {file_info['to']}")
                print(f"    Subject: {file_info['subject']}")
    print()

    # Awaiting Review (same as pending for summary)
    print(f"Awaiting Review: {pending['count']} items")

    # Approved (ready to execute)
    approved = get_folder_status(APPROVED)
    print(f"Approved (Ready): {approved['count']} items")
    if detailed and approved['files']:
        for file_info in approved['files']:
            print(f"  - {file_info['name']} ({file_info['type']})")
    print()

    # Rejected
    rejected = get_folder_status(REJECTED)
    print(f"Rejected: {rejected['count']} items")

    # Done (today only)
    done = get_folder_status(DONE)
    done_today = [f for f in done['files'] if f['age_hours'] < 24]
    print(f"Done (Today): {len(done_today)} items")

    # Expired
    expired = get_folder_status(EXPIRED)
    print(f"Expired: {expired['count']} items")

    # Failed
    failed = get_folder_status(FAILED)
    print(f"Failed: {failed['count']} items")

    # Check for items expiring soon
    expiring_soon = []
    for file_path in PENDING_APPROVAL.glob('*.md'):
        metadata = parse_frontmatter(file_path)
        if is_expiring_soon(file_path, metadata):
            age_hours = get_file_age(file_path)
            hours_remaining = EXPIRATION_HOURS - age_hours
            expiring_soon.append({
                'name': file_path.name,
                'hours_remaining': hours_remaining
            })

    if expiring_soon:
        print(f"\n⚠️  Expiring Soon:")
        for item in expiring_soon:
            print(f"  - {item['name']} (expires in {item['hours_remaining']:.1f} hours)")
    else:
        print(f"\n✅ No items expiring soon")


def get_status_json():
    """Get status as JSON."""
    status = {
        'timestamp': datetime.now().isoformat(),
        'pending_approval': get_folder_status(PENDING_APPROVAL),
        'approved': get_folder_status(APPROVED),
        'rejected': get_folder_status(REJECTED),
        'done': get_folder_status(DONE),
        'expired': get_folder_status(EXPIRED),
        'failed': get_folder_status(FAILED)
    }

    # Add expiring soon
    expiring_soon = []
    for file_path in PENDING_APPROVAL.glob('*.md'):
        metadata = parse_frontmatter(file_path)
        if is_expiring_soon(file_path, metadata):
            age_hours = get_file_age(file_path)
            expiring_soon.append({
                'name': file_path.name,
                'hours_remaining': EXPIRATION_HOURS - age_hours
            })

    status['expiring_soon'] = expiring_soon

    return status


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Check approval queue status')
    parser.add_argument('--detailed', '-d', action='store_true', help='Show detailed information')
    parser.add_argument('--json', action='store_true', help='Output as JSON')

    args = parser.parse_args()

    if args.json:
        status = get_status_json()
        print(json.dumps(status, indent=2, ensure_ascii=False))
    else:
        display_status(detailed=args.detailed)


if __name__ == '__main__':
    main()
