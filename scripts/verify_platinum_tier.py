#!/usr/bin/env python3
"""
Platinum Tier Verification Script
Tests all components of the Platinum Tier deployment

Usage:
    # On cloud VM
    python3 scripts/verify_platinum_tier.py --zone cloud

    # On local machine
    python3 scripts/verify_platinum_tier.py --zone local
"""

import sys
import json
import os
from pathlib import Path
import subprocess
from datetime import datetime

class Colors:
    """ANSI color codes"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Print section header"""
    print()
    print(Colors.BOLD + Colors.BLUE + "=" * 70)
    print(f" {text}")
    print("=" * 70 + Colors.RESET)

def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")

def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")

def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")

def check_file_exists(path, description):
    """Check if a file exists"""
    p = Path(path)
    if p.exists():
        size = p.stat().st_size
        print_success(f"{description}: {path} ({size:,} bytes)")
        return True
    else:
        print_error(f"{description} NOT FOUND: {path}")
        return False

def check_process_running(process_name):
    """Check if a process is running"""
    try:
        result = subprocess.run(['pgrep', '-f', process_name],
                              capture_output=True, text=True)
        if result.returncode == 0:
            pids = result.stdout.strip().split('\n')
            print_success(f"{process_name} running (PID: {', '.join(pids)})")
            return True
        else:
            print_error(f"{process_name} NOT running")
            return False
    except Exception as e:
        print_warning(f"Could not check process: {e}")
        return None

def check_cron_job():
    """Check if cron job is installed"""
    try:
        result = subprocess.run(['crontab', '-l'],
                              capture_output=True, text=True)
        if 'cloud_sync' in result.stdout:
            print_success("Cron job installed (cloud_sync)")
            return True
        else:
            print_error("Cron job NOT installed")
            return False
    except Exception as e:
        print_warning(f"Could not check cron: {e}")
        return None

def check_git_config():
    """Check git configuration"""
    try:
        result = subprocess.run(['git', 'remote', '-v'],
                              capture_output=True, text=True)
        if 'ai-employee-vault' in result.stdout:
            print_success("Git remote configured: ai-employee-vault")
            return True
        else:
            print_warning("Git remote NOT found")
            return False
    except Exception as e:
        print_warning(f"Could not check git: {e}")
        return None

def verify_cloud_zone():
    """Verify cloud zone deployment"""
    print_header("CLOUD ZONE VERIFICATION")

    results = []

    # Check directory structure
    print("\n[Directory Structure]")
    results.append(check_file_exists(
        "/home/ubuntu/ai_employee/AI_Employee_Vault",
        "Repository root"
    ))

    for dir_name in ["Needs_Action", "Approved", "Updates", "Signals"]:
        results.append(check_file_exists(
            f"/home/ubuntu/ai_employee/AI_Employee_Vault/{dir_name}",
            f"Directory: {dir_name}"
        ))

    # Check credentials
    print("\n[Credentials]")
    results.append(check_file_exists(
        "/home/ubuntu/ai_employee/AI_Employee_Vault/credentials/gmail_readonly.json",
        "Gmail read-only credentials"
    ))

    # Check watchers
    print("\n[Watchers]")
    results.append(check_file_exists(
        "/home/ubuntu/ai_employee/AI_Employee_Vault/watchers/cloud_email_watcher.py",
        "Cloud email watcher"
    ))

    # Check sync script
    print("\n[Sync Automation]")
    results.append(check_file_exists(
        "/home/ubuntu/ai_employee/AI_Employee_Vault/cloud_sync.sh",
        "Git sync script"
    ))

    # Check processes
    print("\n[Running Processes]")
    results.append(check_process_running("cloud_email_watcher"))

    # Check cron
    print("\n[Cron Jobs]")
    results.append(check_cron_job())

    # Check git config
    print("\n[Git Configuration]")
    results.append(check_git_config())

    return results

def verify_local_zone():
    """Verify local zone deployment"""
    print_header("LOCAL ZONE VERIFICATION")

    results = []

    # Check directory structure
    print("\n[Directory Structure]")
    vault_path = Path.cwd()

    for dir_name in ["Needs_Action", "Approved", "Pending_Approval", "Done"]:
        results.append(check_file_exists(
            vault_path / dir_name,
            f"Directory: {dir_name}"
        ))

    # Check skills
    print("\n[Skills]")
    skills_dir = vault_path / ".claude" / "skills"
    if skills_dir.exists():
        skill_count = len(list(skills_dir.glob("*/SKILL.md")))
        print_success(f"Skills found: {skill_count}")
        results.append(True)
    else:
        print_error("Skills directory NOT found")
        results.append(False)

    # Check watchers
    print("\n[Watchers]")
    watchers_dir = vault_path / "watchers"
    if watchers_dir.exists():
        watcher_count = len(list(watchers_dir.glob("*_watcher.py")))
        print_success(f"Watchers found: {watcher_count}")
        results.append(True)
    else:
        print_error("Watchers directory NOT found")
        results.append(False)

    # Check MCP servers
    print("\n[MCP Servers]")
    mcp_dir = vault_path / "mcp-servers"
    if mcp_dir.exists():
        mcp_count = len([d for d in mcp_dir.iterdir() if d.is_dir()])
        print_success(f"MCP servers found: {mcp_count}")
        results.append(True)
    else:
        print_warning("MCP servers directory NOT found")
        results.append(None)

    # Check git config
    print("\n[Git Configuration]")
    results.append(check_git_config())

    return results

def verify_integration():
    """Verify cloud-local integration"""
    print_header("CLOUD-LOCAL INTEGRATION TEST")

    print("\nThis test requires both zones to be operational.")
    print("Steps to verify integration:")
    print()
    print("1. Send a test email to your Gmail account")
    print("2. Wait 10-15 minutes")
    print("3. Check cloud VM: Needs_Action/email/ should contain draft")
    print("4. Pull changes on local: git pull origin master")
    print("5. Check local: Needs_Action/email/ should contain draft")
    print("6. Move draft to Approved/email/")
    print("7. Push changes: git push origin master")
    print("8. Wait 10 minutes")
    print("9. Verify email was sent")
    print()

    return []

def generate_report(results, zone):
    """Generate verification report"""
    print_header("VERIFICATION REPORT")

    # Count results
    passed = sum(1 for r in results if r is True)
    failed = sum(1 for r in results if r is False)
    warnings = sum(1 for r in results if r is None)
    total = len(results)

    print(f"\nZone: {zone.upper()}")
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {failed}/{total}")
    print(f"Warnings: {warnings}/{total}")

    if passed == total:
        print()
        print_success("ALL CHECKS PASSED! ✓")
        print()
        print("Your Platinum Tier deployment is operational.")
        return True
    elif failed == 0:
        print()
        print_warning("SOME WARNINGS ⚠")
        print()
        print("Your deployment is operational with minor issues.")
        return True
    else:
        print()
        print_error("SOME CHECKS FAILED ✗")
        print()
        print("Please resolve the failures above.")
        return False

def main():
    """Main entry point"""
    print()
    print(Colors.BOLD + "Platinum Tier Verification" + Colors.RESET)
    print(f"Started at: {datetime.now().isoformat()}")

    # Parse arguments
    zone = "local"
    if len(sys.argv) > 1:
        zone = sys.argv[1].replace("--zone=", "")

    # Run verification
    results = []

    if zone == "cloud":
        results = verify_cloud_zone()
    elif zone == "local":
        results = verify_local_zone()
    elif zone == "integration":
        results = verify_integration()
    else:
        print_error(f"Unknown zone: {zone}")
        print("Use: --zone=cloud|local|integration")
        sys.exit(1)

    # Generate report
    if results:
        success = generate_report(results, zone)
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
