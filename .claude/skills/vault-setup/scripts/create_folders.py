#!/usr/bin/env python3
"""
Create folder structure for Personal AI Employee Obsidian vault

This script creates all required folders for the Bronze tier implementation.
"""

from pathlib import Path
import sys


REQUIRED_FOLDERS = [
    'Inbox',
    'Needs_Action',
    'Plans',
    'Pending_Approval',
    'Approved',
    'Rejected',
    'Done',
    'Logs',
    'watchers',
]


def create_vault_structure(vault_path='.'):
    """
    Create all required folders in the vault.

    Args:
        vault_path: Path to the vault root (defaults to current directory)
    """
    vault = Path(vault_path).resolve()

    print(f"Creating vault structure in: {vault}")
    print("-" * 50)

    created = []
    already_exists = []

    for folder in REQUIRED_FOLDERS:
        folder_path = vault / folder
        if folder_path.exists():
            already_exists.append(folder)
            print(f"[EXISTS] {folder}")
        else:
            try:
                folder_path.mkdir(parents=True, exist_ok=True)
                created.append(folder)
                print(f"[CREATED] {folder}")
            except Exception as e:
                print(f"[ERROR] Failed to create {folder}: {e}")
                return False

    print("-" * 50)
    print(f"Summary:")
    print(f"  Created: {len(created)} folders")
    print(f"  Already existed: {len(already_exists)} folders")

    if created:
        print(f"\nNewly created folders:")
        for folder in created:
            print(f"  - {folder}")

    print(f"\nVault structure ready at: {vault}")
    return True


def main():
    """Main entry point"""
    vault_path = sys.argv[1] if len(sys.argv) > 1 else '.'

    success = create_vault_structure(vault_path)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
